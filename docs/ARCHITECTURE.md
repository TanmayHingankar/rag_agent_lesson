# Architecture & Design Report

## 1. Problem framing

The assignment asks for a system that does more than produce a lesson. The system must decide whether the lesson is good enough to ship. Therefore generation and evaluation are separate responsibilities.

## 2. Components

### Generator
Produces a standalone lesson using an audience-specific system prompt. It receives previous failure feedback and persistent memory signals.

### Evaluator
Acts as a quality gate. It checks six binary rubric dimensions and returns structured JSON. One failed dimension rejects the draft.

### Orchestrator
Controls the loop, retry limit, state transitions, output files, and rejection log.

### Memory
Persists failure patterns and recent runs. Repeated failures are surfaced to the next generator as context. This is the self-evolving mechanism.

## 3. Why hard PASS/FAIL checks?

The assignment explicitly asks for hard pass/fail checkpoints. A weighted score can hide a critical failure. For example, a lesson could be fluent and accurate but still use unexplained jargon. The gate therefore requires every dimension to pass.

## 4. Why a separate evaluator?

Using the same instruction to generate and approve content can create confirmation bias: the generator has an incentive to consider its own output acceptable. A separate evaluator prompt creates a clearer critic/generator boundary.

## 5. Retry design

Maximum retries are configurable, defaulting to two retries after the initial attempt. This guarantees termination and limits API spend.

## 6. Self-evolving memory

The system stores:
- which checks failed
- how often they failed
- when they were last seen
- number of attempts per run

The generator receives the most frequent recent failure patterns. This means repeated issues can shape future drafts rather than disappearing after a single run.

## 7. Key trade-offs

### JSON memory vs database
JSON is transparent and zero-infrastructure. A production system should use a database.

### Direct model call vs framework
The code uses a small explicit state machine instead of hiding orchestration inside a framework. This makes the take-home easy to inspect and reason about. The same state transitions can later be moved to LangGraph.

### Score vs binary gate
Binary gates match the requirement and make shipping criteria auditable.

## 8. Failure handling

The evaluator returns explicit failed checks and retry instructions. The orchestrator feeds those instructions into the next generation call. If all retries fail, the workflow terminates with status FAILED rather than silently shipping content.

## 9. Observability

Every run is saved as JSON with evaluations and rejection data. This provides a lightweight audit trail and is suitable for demonstrating the workflow in a video.

## 10. Production hardening

Recommended next steps:
- source retrieval and citation validation
- adversarial evaluator tests
- prompt versioning
- model fallback
- token/cost metrics
- tracing
- moderation
- database-backed memory
- human escalation after repeated failure
- regression suite with golden lessons
