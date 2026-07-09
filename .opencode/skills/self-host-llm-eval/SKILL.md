---
name: self-host-llm-eval
description: Evaluate self-hosted LLM outputs in OpenCode by comparing a trusted reference implementation or source truth against a generated candidate. Use for Python code tasks, Kotlin/Java code tasks, and documentation generation tasks where the user needs tiered metrics, test/check selection, baseline validation, static comparison, and LLM-judged subjective scores.
---

# Self-Hosted LLM Evaluation

Use this skill to run a controlled evaluation of generated work against a trusted reference. Support exactly three task families in the first version:

- `python`
- `kotlin-java`
- `docs`

## Required Workflow

1. Parse the user's requested pair:
   - `reference`: original code, docs, folder, or source truth
   - `candidate`: self-host LLM generated code/docs
   - `task_family`: `python`, `kotlin-java`, or `docs`
   - `task_type`: `code_generation`, `bug_fix`, `refactor`, `test_generation`, or `documentation_generation`
   - `scope`: typed target such as `function:calculate_price`, `method:FooService.calculatePrice`, or `docs:README`
2. Show the evaluation pair summary and ask the user to confirm or edit it before continuing.
3. Discover candidate tests or validation checks.
4. Show the ranked validation set and ask the user to select, edit, or add checks before scoring.
5. Run the selected checks on the reference first. Only checks that pass on the reference become the baseline.
6. Run the same baseline checks against the candidate.
7. Run static comparison for compatibility, hallucinated APIs, signatures, and structure.
8. Use LLM judgment only for subjective metrics; require score, evidence, and confidence.
9. Write outputs under `eval-runs/<run-id>/`.
10. Mark non-applicable metrics as `N/A`, never as failed or zero.

Do not overwrite reference files. If a candidate must be swapped into the reference path, do it only in an isolated temporary copy or after explicit user approval.

## Scope Values

Accept these scope forms:

- `function:<name>` or `function:<path>::<name>`
- `class:<name>` or `class:<path>::<name>`
- `method:<Class.method>` or `method:<path>::<Class.method>`
- `api:<METHOD route>`
- `module:<path>`
- `package:<path-or-package-name>`
- `cli:<command-or-entrypoint>`
- `dag:<dag-id-or-file>`
- `task:<task-id-or-function>`
- `workflow:<name-or-path>`
- `docs:<readme|api-reference|architecture|tutorial|changelog|path>`
- `repo`

If the scope is ambiguous, ask the user to choose the exact target.

## Confirmation Prompts

Before test/check discovery, show:

```yaml
reference: <path>
candidate: <path>
task_family: <python|kotlin-java|docs>
task_type: <...>
scope: <...>
language_adapter: <Python|Kotlin/Java|Documentation>
expected_validation: <tests/checks/static/llm-judge summary>
```

Ask: `Proceed with this evaluation pair? yes/edit/cancel`

Before scoring, show discovered validation candidates with ID, path/check, confidence, and reason. Ask the user to select:

- comma-separated IDs
- `all`
- manual paths or commands
- `none, generate checks`

## Task Family Adapters

### Python

Discover tests from `tests/`, `test_*.py`, `*_test.py`, imports of the reference module/function, matching test names, and nearby package paths.

Prefer existing commands in this order:

- user-provided command
- `python -m unittest discover tests/`
- `pytest`

Static checks:

- import existence
- function/class/method signature compatibility
- public symbol presence
- unresolved imports where detectable
- lint/format/type checks only if configured in the repo

### Kotlin/Java

Discover tests from `src/test/kotlin`, `src/test/java`, `*Test.kt`, `*Tests.kt`, `*Test.java`, `*IT.java`, package/class/method name matches, and Spring/Ktor/API route hints when relevant.

Prefer existing commands in this order:

- user-provided command
- `./gradlew test`
- `./gradlew check`
- `mvn test`

Static checks:

- compile success
- package/class/method signature compatibility
- unresolved symbols/imports from compiler output
- nullable/suspend signature differences for Kotlin
- Gradle/Maven dependency hallucination
- ktlint/detekt/checkstyle/spotbugs only if configured

### Docs

Use the reference as source truth and the candidate as generated documentation.

Validation checks:

- coverage of public APIs/classes/functions/routes/config keys
- broken internal links
- code snippet validity when runnable
- factual conflicts with source files
- heading/structure completeness
- terminology consistency

Skip code-only metrics such as test pass rate unless snippets or examples are executable and selected as checks.

## Metrics

Read `references/three-tier-metrics.md` for metric applicability and calculation rules. Read `references/llm-judge-rubric.md` before judging subjective metrics. Read `references/documentation-rubric.md` for docs tasks.

## Helper Scripts

Use the repo-local scripts when useful:

- `python3 eval-tools/discover_tests.py --reference <path> --candidate <path> --task-family <python|kotlin-java|docs> --scope <scope>`
- `python3 eval-tools/static_compare.py --reference <path> --candidate <path> --task-family <python|kotlin-java|docs> --scope <scope>`
- `python3 eval-tools/run_pair_eval.py --run-id <id> --baseline-command "<cmd>" --candidate-command "<cmd>"`
- `python3 eval-tools/summarize_metrics.py --run-dir eval-runs/<run-id>`

Scripts are helpers, not authority. User-confirmed validation choices and baseline pass/fail status decide the final set.

## Report Rules

Include:

- pair summary
- selected validation set and user confirmation
- baseline results
- candidate results
- static comparison
- Tier 1 / Tier 2 / Tier 3 metric table
- LLM judge model/prompt version when available
- evidence and confidence for subjective metrics
- `N/A` section with reasons
- final recommendation: `pass`, `fail`, or `review-needed`
