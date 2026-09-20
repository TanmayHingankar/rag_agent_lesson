import json
import os
import time

from openai import OpenAI

from .models import Evaluation
from .prompts import GENERATOR_SYSTEM, EVALUATOR_SYSTEM
from .rubric_rules import deterministic_checks
from .grounding import RAG_GROUNDING_FACTS


class GeminiModel:
    def __init__(self, model=None):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to the .env file."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

    def _chat_completion(self, messages, temperature, response_format):
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    response_format=response_format,
                    messages=messages,
                )

            except Exception as exc:
                error_text = str(exc)

                # Retry temporary Gemini availability errors
                if (
                    ("503" in error_text or "UNAVAILABLE" in error_text)
                    and attempt < max_attempts
                ):
                    wait_seconds = attempt * 2
                    time.sleep(wait_seconds)
                    continue

                # Retry temporary rate-limit errors
                if (
                    ("429" in error_text or "RESOURCE_EXHAUSTED" in error_text)
                    and attempt < max_attempts
                ):
                    wait_seconds = attempt * 2
                    time.sleep(wait_seconds)
                    continue

                raise

    def generate(self, topic, memory, feedback, demo_error=False):
        # ---------------------------------------------------------
        # 1. Prepare approved grounding facts
        # ---------------------------------------------------------
        grounding = "\n".join(
            f"- {fact}" for fact in RAG_GROUNDING_FACTS
        )

        # ---------------------------------------------------------
        # 2. Prepare generator system prompt
        # ---------------------------------------------------------
        system = GENERATOR_SYSTEM.format(
            memory=json.dumps(memory, indent=2),
            feedback=json.dumps(feedback, indent=2),
        )

        # ---------------------------------------------------------
        # 3. Give generator the approved grounding facts
        # ---------------------------------------------------------
        system += (
            "\n\nAPPROVED GROUNDING FACTS:\n"
            + grounding
            + "\n\nUse these facts as the factual source of truth."
        )

        # ---------------------------------------------------------
        # 4. Prepare user request
        # ---------------------------------------------------------
        user = f"Topic: {topic}"

        # ---------------------------------------------------------
        # 5. Optional deliberate error for demo
        # ---------------------------------------------------------
        if demo_error:
            user += (
                "\nFor this first attempt only, deliberately include one "
                "small quality problem: use the undefined term 'embedding' "
                "once without explaining it. This is a test of the evaluator."
            )

        # ---------------------------------------------------------
        # 6. Generate lesson
        # ---------------------------------------------------------
        response = self._chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": user,
                },
            ],
            temperature=0.2,
            response_format={"type": "text"},
        )

        return response.choices[0].message.content

    def evaluate(self, topic, lesson):
        # ---------------------------------------------------------
        # 1. Prepare approved grounding facts
        # ---------------------------------------------------------
        grounding = "\n".join(
            f"- {fact}" for fact in RAG_GROUNDING_FACTS
        )

        # ---------------------------------------------------------
        # 2. Prepare evaluator prompt
        # ---------------------------------------------------------
        prompt = (
            f"{EVALUATOR_SYSTEM}\n\n"
            f"APPROVED GROUNDING FACTS:\n"
            f"{grounding}\n\n"
            f"TOPIC:\n"
            f"{topic}\n\n"
            f"LESSON:\n"
            f"{lesson}"
        )

        # ---------------------------------------------------------
        # 3. Ask Gemini to evaluate the lesson
        # ---------------------------------------------------------
        response = self._chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # ---------------------------------------------------------
        # 4. Convert Gemini response into Evaluation object
        # ---------------------------------------------------------
        llm_eval = Evaluation.model_validate_json(
            response.choices[0].message.content
        )

        # ---------------------------------------------------------
        # 5. Run deterministic checks as a second safety layer
        # ---------------------------------------------------------
        rule_checks = deterministic_checks(
            topic,
            lesson,
        )

        # Map LLM checks by their name
        by_name = {
            check.name: check
            for check in llm_eval.checks
        }

        merged = []
        failed = []

        retry = list(
            llm_eval.retry_instructions
        )

        # ---------------------------------------------------------
        # 6. Merge LLM evaluation + deterministic evaluation
        # ---------------------------------------------------------
        for rule in rule_checks:
            llm_check = by_name.get(rule.name)

            passed = (
                rule.passed
                and (
                    llm_check.passed
                    if llm_check
                    else False
                )
            )

            reason = rule.reason
            evidence = rule.evidence

            if llm_check and not llm_check.passed:
                reason = (
                    f"{llm_check.reason} "
                    f"Deterministic guard: {rule.reason}"
                )

                evidence = (
                    f"LLM: {llm_check.evidence}; "
                    f"Rule: {rule.evidence}"
                )

            merged.append(
                type(rule)(
                    name=rule.name,
                    passed=passed,
                    reason=reason,
                    evidence=evidence,
                )
            )

            # -----------------------------------------------------
            # 7. Collect failed checks and retry instructions
            # -----------------------------------------------------
            if not passed:
                failed.append(rule.name)

                if llm_check and llm_check.reason:
                    retry.append(
                        f"Fix {rule.name}: "
                        f"{llm_check.reason}"
                    )
                else:
                    retry.append(
                        f"Fix {rule.name}: "
                        f"{rule.reason}"
                    )

        # ---------------------------------------------------------
        # 8. Return final combined evaluation
        # ---------------------------------------------------------
        return Evaluation(
            overall_pass=(len(failed) == 0),
            checks=merged,
            failed_checks=failed,
            retry_instructions=list(
                dict.fromkeys(retry)
            ),
        )