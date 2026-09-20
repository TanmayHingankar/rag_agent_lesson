from typing import List, Literal
from pydantic import BaseModel, Field

class RubricCheck(BaseModel):
    name: str
    passed: bool
    reason: str
    evidence: str = ""

class Evaluation(BaseModel):
    overall_pass: bool
    checks: List[RubricCheck]
    failed_checks: List[str] = Field(default_factory=list)
    retry_instructions: List[str] = Field(default_factory=list)

class RunResult(BaseModel):
    run_id: str
    topic: str
    status: Literal["PASSED", "FAILED"]
    attempts: int
    lesson: str = ""
    evaluations: List[Evaluation] = Field(default_factory=list)
    rejection_log: List[dict] = Field(default_factory=list)
