---
description: Summarize an existing self-host LLM evaluation run
agent: build
---

Use the `self-host-llm-eval` skill to summarize this evaluation run:

```text
$ARGUMENTS
```

If a run directory is provided, run:

```bash
python3 eval-tools/summarize_metrics.py --run-dir <run-dir>
```

Then explain the Tier 1, Tier 2, and Tier 3 results, including any `N/A` metrics and remaining review risks.
