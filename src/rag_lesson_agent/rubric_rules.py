from .models import RubricCheck

REQUIRED_TERMS = {
    "what_is_rag": ["retrieval-augmented generation", "rag"],
    "retrieval": ["retriev"],
    "generation": ["generat"],
    "context": ["context"],
    "example": ["example"],
    "limitations": ["limitation", "does not", "wrong information"],
}

DEMO_JARGON = "reranker"


def _has_any(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term in t for term in terms)


def deterministic_checks(topic: str, lesson: str):
    """Cheap deterministic guardrails complement the LLM evaluator.

    These checks are not a replacement for semantic evaluation. They protect
    the most important binary gates from model variance and make the demo
    reproducible.
    """
    t = lesson.lower()
    checks = []

    accurate = not any(x in t for x in ["rag means training a new model", "rag is a database"])
    checks.append(RubricCheck(
        name="accuracy_and_groundedness",
        passed=accurate,
        reason="No known contradictory RAG statement was detected by the deterministic guard." if accurate else "A contradictory RAG statement was detected.",
        evidence="deterministic_guard"
    ))

    beginner = len(lesson.split()) >= 180 and all(x not in t for x in ["asymptotic complexity", "backpropagation"])
    checks.append(RubricCheck(
        name="beginner_friendly_language",
        passed=beginner,
        reason="Lesson has enough teaching content and avoids unrelated advanced terminology." if beginner else "Lesson is too short or contains unrelated advanced terminology.",
        evidence="deterministic_guard"
    ))

    checks.append(RubricCheck(
        name="teaches_by_example",
        passed=_has_any(lesson, ["example", "suppose", "imagine"]),
        reason="A concrete example marker is present." if _has_any(lesson, ["example", "suppose", "imagine"]) else "No concrete example marker was found.",
        evidence="deterministic_guard"
    ))

    # For the demo, 'reranker' is deliberately injected without a definition.
    # A normal generated lesson is allowed to discuss it only if it defines it.
    reranker_ok = DEMO_JARGON not in t or any(
        phrase in t for phrase in ["reranker is", "reranker means", "reranker, which", "reranker is a"]
    )
    checks.append(RubricCheck(
        name="no_unexplained_jargon",
        passed=reranker_ok,
        reason="No unexplained demo jargon detected." if reranker_ok else "The term 'reranker' is used without a beginner-level definition.",
        evidence="deterministic_guard"
    ))

    coverage = all(_has_any(lesson, terms) for terms in REQUIRED_TERMS.values())
    checks.append(RubricCheck(
        name="key_point_coverage",
        passed=coverage,
        reason="Required introductory RAG concepts are present." if coverage else "One or more required introductory RAG concepts are missing.",
        evidence="deterministic_guard"
    ))

    flow = all(x in t for x in ["what is", "how does", "recap"])
    checks.append(RubricCheck(
        name="coherent_teaching_flow",
        passed=flow,
        reason="Lesson contains definition, how-it-works, and recap sections." if flow else "Expected teaching-flow headings are missing.",
        evidence="deterministic_guard"
    ))
    return checks
