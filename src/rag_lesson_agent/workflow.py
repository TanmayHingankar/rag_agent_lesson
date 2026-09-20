import uuid
from pathlib import Path

from .models import RunResult


class LessonWorkflow:
    def __init__(self, model, memory, max_retries=2):
        self.model = model
        self.memory = memory
        self.max_retries = max_retries

    def run(self, topic="Introduction to RAG", demo_error=False):
        run_id = uuid.uuid4().hex[:10]

        feedback = []
        evaluations = []
        rejection_log = []

        # Load persistent memory once at the beginning of the run.
        memory_context = self.memory.context()

        # max_retries=2 means:
        # Attempt 1 + Retry 1 + Retry 2 = maximum 3 attempts.
        for attempt in range(1, self.max_retries + 2):

            # Generate a fresh lesson using previous evaluator feedback.
            lesson = self.model.generate(
                topic,
                memory_context,
                feedback,
                demo_error=False,
            )

            # ---------------------------------------------------------
            # DEMO MODE
            # ---------------------------------------------------------
            # We deliberately inject an unexplained technical term into
            # the first draft so the evaluator has something concrete
            # to reject during the Loom demonstration.
            if demo_error and attempt == 1:
                lesson += (
                    "\n\n"
                    "### Advanced note\n"
                    "This pipeline also uses a reranker to reorder "
                    "retrieved passages before generation.\n"
                )

            # ---------------------------------------------------------
            # EVALUATION
            # ---------------------------------------------------------
            evaluation = self.model.evaluate(
                topic,
                lesson,
            )

            evaluations.append(evaluation)

            # ---------------------------------------------------------
            # PASS
            # ---------------------------------------------------------
            if evaluation.overall_pass:

                result = RunResult(
                    run_id=run_id,
                    topic=topic,
                    status="PASSED",
                    attempts=attempt,
                    lesson=lesson,
                    evaluations=evaluations,
                    rejection_log=rejection_log,
                )

                self._write_outputs(result)

                # Persist what happened in this run so future runs
                # can learn from previous failure patterns.
                self.memory.record(
                    topic,
                    evaluations,
                )

                return result

            # ---------------------------------------------------------
            # FAIL / REJECTION
            # ---------------------------------------------------------
            rejection_log.append(
                {
                    "attempt": attempt,
                    "status": "REJECTED",
                    "failed_checks": evaluation.failed_checks,
                    "reasons": [
                        check.reason
                        for check in evaluation.checks
                        if not check.passed
                    ],
                    "changes_requested_for_retry": (
                        evaluation.retry_instructions
                    ),
                }
            )

            # Feed evaluator feedback into the next generation attempt.
            feedback = evaluation.retry_instructions

        # -------------------------------------------------------------
        # FINAL FAILURE AFTER ALL ATTEMPTS
        # -------------------------------------------------------------
        result = RunResult(
            run_id=run_id,
            topic=topic,
            status="FAILED",
            attempts=self.max_retries + 1,
            lesson=lesson,
            evaluations=evaluations,
            rejection_log=rejection_log,
        )

        self._write_outputs(result)

        self.memory.record(
            topic,
            evaluations,
        )

        return result

    def _write_outputs(self, result):
        out = Path("outputs")
        out.mkdir(exist_ok=True)

        # Save complete run information.
        (out / f"run_{result.run_id}.json").write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Save the final lesson only when the lesson passes.
        if result.status == "PASSED":
            (out / "final_lesson.md").write_text(
                result.lesson,
                encoding="utf-8",
            )

        # -------------------------------------------------------------
        # REJECTION LOG
        # -------------------------------------------------------------
        lines = [
            "# Rejection Log",
            "",
        ]

        if not result.rejection_log:
            lines.append(
                "No rejection occurred; the first draft passed all checks."
            )

        for item in result.rejection_log:

            lines.extend(
                [
                    f"## Attempt {item['attempt']} — {item['status']}",
                    "",
                    "**Failed checks:** "
                    + ", ".join(item["failed_checks"]),
                    "",
                    "**Reasons:**",
                ]
            )

            lines.extend(
                f"- {reason}"
                for reason in item["reasons"]
            )

            lines.extend(
                [
                    "",
                    "**Changes requested:**",
                ]
            )

            lines.extend(
                f"- {instruction}"
                for instruction in item[
                    "changes_requested_for_retry"
                ]
            )

            lines.append("")

        (out / "rejection_log.md").write_text(
            "\n".join(lines),
            encoding="utf-8",
        )