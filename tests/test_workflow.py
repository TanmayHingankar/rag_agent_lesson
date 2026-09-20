import json
from pathlib import Path
from src.rag_lesson_agent.memory import MemoryStore
from src.rag_lesson_agent.workflow import LessonWorkflow
from src.rag_lesson_agent.models import Evaluation, RubricCheck

class FakeModel:
    def __init__(self):
        self.calls = 0

    def generate(self, topic, memory, feedback, demo_error=False):
        self.calls += 1
        return "RAG is a method that retrieves useful information before an AI writes an answer."

    def evaluate(self, topic, lesson):
        if self.calls == 1:
            return Evaluation(
                overall_pass=False,
                checks=[RubricCheck(
                    name="teaches_by_example",
                    passed=False,
                    reason="No concrete example.",
                    evidence=""
                )],
                failed_checks=["teaches_by_example"],
                retry_instructions=["Add a simple concrete example."]
            )
        return Evaluation(
            overall_pass=True,
            checks=[RubricCheck(
                name="teaches_by_example",
                passed=True,
                reason="Example is present.",
                evidence="Example section."
            )],
            failed_checks=[],
            retry_instructions=[]
        )

def test_retry_and_persistence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory = MemoryStore("data/memory.json")
    workflow = LessonWorkflow(FakeModel(), memory, max_retries=2)
    result = workflow.run()
    assert result.status == "PASSED"
    assert result.attempts == 2
    assert Path("outputs/final_lesson.md").exists()
    assert Path("outputs/rejection_log.md").exists()
    data = json.loads(Path("data/memory.json").read_text())
    assert data["runs"]
