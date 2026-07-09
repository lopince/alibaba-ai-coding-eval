---
description: Evaluate a self-host LLM candidate against a trusted reference with tiered metrics
agent: build
---

Use the `self-host-llm-eval` skill to evaluate this request:

```text
$ARGUMENTS
```

Follow the skill workflow exactly:

1. Parse `reference`, `candidate`, `task_family`, `task_type`, and `scope`.
2. If any required value is missing, ask for it.
3. Show the evaluation pair summary and require user confirmation before discovery.
4. Discover candidate tests/checks with `eval-tools/discover_tests.py` when useful.
5. Ask the user to select the validation set before scoring.
6. Baseline selected checks on the reference.
7. Run the same baseline checks on the candidate.
8. Run static comparison with `eval-tools/static_compare.py`.
9. Judge subjective metrics only with score, evidence, and confidence.
10. Write artifacts under `eval-runs/<run-id>/` and produce a concise final report.
