# Documentation Evaluation Rubric

Use this for `task_family=docs` or `task_type=documentation_generation`.

## Objective/Semi-Objective Checks

- Public API/source coverage: important functions, classes, routes, config keys, and workflows are documented.
- Reference accuracy: names, parameters, defaults, return values, and paths match source truth.
- Broken internal links: local anchors and relative links resolve.
- Example validity: code snippets are syntactically valid or runnable when feasible.
- Conflict rate: generated docs do not contradict existing source truth.

## Subjective Checks

Score each 0-5 with evidence:

- Completeness: covers the expected audience journey.
- Clarity: easy to read and follow.
- Usefulness: helps a developer accomplish real tasks.
- Structure: headings and order match user needs.
- Audience fit: depth and language match the intended reader.
- Hallucination risk: avoids unsupported features, commands, and claims.

## Docs Report Notes

Mark these code metrics as `N/A` unless executable examples are explicitly selected:

- test pass rate
- regression rate
- fix success rate
- behavior preservation

Do not score a docs candidate higher for being longer unless the added detail is accurate and useful.
