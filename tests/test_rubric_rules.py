from src.rag_lesson_agent.rubric_rules import deterministic_checks

GOOD = """
# What is RAG?
RAG means Retrieval-Augmented Generation. It retrieves useful information and uses an AI model to generate an answer.
## Why it matters
It helps an AI answer using a specific document collection.
## Example
For example, a student asks about an attendance rule in a college handbook.
## How does RAG work?
The system retrieves useful text, gives it as context, and then the model generates an answer.
## Limitations
RAG can be wrong if retrieval finds the wrong information or the documents are wrong.
## Recap
RAG retrieves information before generation.
""" + (" simple " * 180)

def test_demo_jargon_is_rejected():
    lesson = GOOD + "\nThis uses a reranker to reorder passages."
    checks = {c.name: c for c in deterministic_checks("Introduction to RAG", lesson)}
    assert not checks["no_unexplained_jargon"].passed

def test_good_lesson_passes_deterministic_guards():
    checks = {c.name: c for c in deterministic_checks("Introduction to RAG", GOOD)}
    assert all(c.passed for c in checks.values())
