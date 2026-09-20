# Self-Evaluating Lesson Content Generator — Introduction to RAG

A take-home implementation for **GenAI Engineer – Content Systems**.

The system builds a beginner lesson from zero knowledge, evaluates it using hard PASS/FAIL rubric checks, regenerates failed lessons with evaluator feedback, and persists learning signals across runs.

## What is included

- Generate → Evaluate → Regenerate agentic loop
- Maximum 2 retries (3 total attempts)
- Hard PASS/FAIL rubric with six dimensions
- Structured evaluator output using Pydantic
- Hybrid evaluator: LLM semantic judgement + deterministic hard guards
- Deliberate-error demo mode for the Loom requirement
- Persistent memory in `data/memory.json`
- Self-evolving prompt context from previous failures
- Rejection log with failure reasons and changes
- CLI for normal and demo runs
- Unit tests
- Architecture and design report
- Final lesson document
- Dockerfile
- GitHub-ready structure

## Architecture

```text
Topic
  |
  v
Memory Store ---> Generator Agent ---> Draft Lesson
                       ^                  |
                       |                  v
               Retry Feedback <--- Evaluator Agent
                                          |
                                  PASS / FAIL per check
                                          |
                           +--------------+--------------+
                           |                             |
                         PASS                           FAIL
                           |                             |
                           v                             v
                    Ship lesson                  Retry <= 2?
                                                       |
                                                yes -> regenerate
                                                no  -> terminate
```

## Rubric

Every checkpoint is binary. There is no partial credit.

1. **Accuracy & groundedness** — technically correct for an introductory RAG lesson.
2. **Beginner-friendly language** — short sentences and accessible vocabulary.
3. **Example-based teaching** — includes a concrete example that connects retrieval to generation.
4. **No unexplained jargon** — important technical terms are defined before/when used.
5. **Key-point coverage** — covers what RAG is, why it matters, core pipeline, retrieval, context, generation, and limitations.
6. **Coherent flow** — moves from motivation → definition → example → how it works → limitations → recap.

A lesson passes only when **all six checks pass**.

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

```bash
copy .env.example .env
```

PowerShell/Linux/macOS users can simply copy the file manually.

Put your OpenAI key in `.env`:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
MAX_RETRIES=2
QUALITY_THRESHOLD=0.85
```

## Run

Normal run:

```bash
python -m src.rag_lesson_agent.main
```

Deliberate-error demo (recommended for Loom):

```bash
python -m src.rag_lesson_agent.main --demo-error
```

The demo deterministically injects an undefined `reranker` term into the first draft. The hybrid evaluator rejects it, records the failure, and feeds the retry instructions into the next generation attempt.

## Outputs

A run creates:

- `outputs/run_<id>.json` — complete trace
- `outputs/final_lesson.md` — passing lesson
- `outputs/rejection_log.md` — failures, reasons, and retry changes
- `data/memory.json` — persistent learning memory

## Tests

```bash
pytest -q
```

Tests use a fake model and deterministic rubric tests, so they do not require an API key. The verified test suite currently contains 3 tests.

## Why this is agentic

The workflow is not just a single generation prompt. The evaluator is a separate decision-making component. It can reject content, produce structured reasons, and those reasons become explicit inputs to the next generation attempt. The memory layer carries recurring failure patterns into future runs.

## Design trade-offs

- **Python + OpenAI API** keeps the implementation easy to inspect and deploy.
- **Explicit state machine** is easier to debug than hidden autonomous behavior.
- **Structured JSON evaluation** prevents free-form evaluator output from becoming unreliable control logic.
- **Hybrid evaluator** combines semantic LLM judgement with deterministic guards for reproducible hard gates.
- **Hard gates instead of a single score** avoid a polished lesson passing despite a critical failure.
- **Small persistent JSON memory** is sufficient for a take-home and easy to inspect. Production would use a database/vector store.
- **Maximum two retries** guarantees termination and controls API cost.

## Production extensions

- Replace JSON memory with PostgreSQL + vector memory.
- Add source-grounded RAG evaluation with citations.
- Add prompt/version tracking and experiment metrics.
- Add moderation and PII checks.
- Add observability/tracing.
- Add human review for repeated failures.
- Add a retrieval benchmark and regression test set.
