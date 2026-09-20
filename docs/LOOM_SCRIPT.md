# Loom Script — 15 to 20 Minutes

## 0:00–2:00 — Context
Explain that the assignment is about owning the quality-control loop, not just prompt writing.

## 2:00–4:00 — Architecture
Show:
Topic → Generator → Evaluator → PASS/FAIL → Retry → Memory → Ship.

Explain the six hard checks.

## 4:00–7:00 — Code walkthrough
Open:
- `src/rag_lesson_agent/prompts.py`
- `src/rag_lesson_agent/models.py`
- `src/rag_lesson_agent/workflow.py`
- `src/rag_lesson_agent/memory.py`

Point out the evaluator's binary gate and retry limit.

## 7:00–12:00 — End-to-end demo
Run:

```bash
python -m src.rag_lesson_agent.main --demo-error
```

Explain that the first attempt deliberately contains an undefined term. Show the evaluator rejection in the terminal/output JSON.

Then show the second attempt receiving retry instructions and passing.

## 12:00–15:00 — Outputs
Open:
- `outputs/final_lesson.md`
- `outputs/rejection_log.md`
- `outputs/run_<id>.json`
- `data/memory.json`

Explain how the rejection is recorded and how memory stores recurring failure patterns.

## 15:00–18:00 — Testing and design choices
Run:

```bash
pytest -q
```

Explain why hard gates, explicit state, JSON memory, and limited retries were selected.

## 18:00–20:00 — Closing
Discuss production extensions: database memory, source grounding, observability, prompt versioning, regression tests, and human escalation.

Keep your face visible during the walkthrough to satisfy the assignment requirement.
