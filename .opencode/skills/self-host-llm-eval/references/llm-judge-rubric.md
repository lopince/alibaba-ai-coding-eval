# LLM Judge Rubric

Use LLM judgment only after objective checks and static comparison are available.

## Required Output Shape

```json
{
  "metric": "pattern_consistency",
  "score": 4,
  "max_score": 5,
  "confidence": 0.78,
  "evidence": [
    {
      "file": "path/to/file",
      "observation": "Specific factual reason for the score."
    }
  ],
  "risks": [
    "Remaining uncertainty or missing evidence."
  ]
}
```

## General Scale

- `5`: Clearly satisfies the metric with strong evidence.
- `4`: Mostly satisfies the metric with minor issues.
- `3`: Mixed result; acceptable but needs review.
- `2`: Significant issues.
- `1`: Mostly fails.
- `0`: Not enough relevant work to score, or wholly incorrect.

## Rules

- Cite concrete files, functions, tests, commands, or snippets.
- Penalize hallucinated APIs, invented behavior, and unsupported claims.
- Prefer objective evidence over stylistic preference.
- Separate factual accuracy from writing quality.
- Use `N/A` when the metric does not apply.
