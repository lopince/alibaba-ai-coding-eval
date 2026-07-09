# Three-Tier Metrics

Use applicability first. A metric that does not apply is `N/A`, not `0`.

## Tier 1: Must-Have

Hard correctness gates.

| Metric | Applies To | Evaluator |
|---|---|---|
| Test pass rate | Python, Kotlin/Java code tasks | selected baseline tests |
| Pass@k | code tasks with multiple attempts | attempt records |
| API hallucination rate | Python, Kotlin/Java, docs API references | static compare + compile/import output |
| Fix success rate | bug_fix | bug tests pass and baseline tests still pass |
| Regression rate | code tasks | reference-passing checks that fail on candidate |
| Behavior preservation | code_generation, refactor | tests + signature/static comparison + judge when needed |
| Time to working code | all task families when timing is recorded | run metadata |

## Tier 2: Should-Have

Production-readiness signals.

| Metric | Applies To | Evaluator |
|---|---|---|
| Pattern consistency | all | static comparison + LLM judge |
| False positive rate | code review tasks | LLM judge or human labels |
| Test coverage % | code/test_generation when coverage available | coverage tool |
| Cost per accepted line | code tasks when cost available | run metadata |
| Multi-file coherence | multi-file code/docs tasks | static comparison + LLM judge |
| Root cause accuracy | bug_fix/debugging | LLM judge against evidence |
| Documentation accuracy | docs | static source check + LLM judge |

## Tier 3: Nice-to-Have

Optimization and quality signals.

| Metric | Applies To | Evaluator |
|---|---|---|
| Style compliance | Python, Kotlin/Java, docs | configured linters/style checks |
| Suggestion usefulness | review/docs tasks | human labels or LLM judge |
| Retry attempts | all when attempts are tracked | run metadata |
| Meaningful assertion rate | test_generation | static/LLM inspection of assertions |
| Review acceptance rate | review tasks | human labels |
| Iterations to completion | all when tracked | run metadata |
| Test pass rate maintained | refactor | selected baseline tests |
| Documentation completeness | docs | rubric judge |

## Scoring Guidance

- Objective metrics should include numerator, denominator, and command/check source.
- Subjective metrics must include score, evidence, and confidence.
- Report both raw metric values and tier status.
- Do not aggregate into a single score unless the user asks for weighting.
