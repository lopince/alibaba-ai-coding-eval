#!/usr/bin/env python3
"""Summarize a Promptfoo JSON export for the long-horizon sample.

Promptfoo's JSON schema can evolve, so this script is deliberately defensive:
it walks the export tree, finds assertion-like records, and reports pass/fail
counts plus any named metric scores it can discover.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_results.py <promptfoo-results.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))

    test_pass_count = 0
    test_fail_count = 0
    assertion_pass_count = 0
    assertion_fail_count = 0
    metric_scores: dict[str, list[float]] = defaultdict(list)

    for node in walk(data):
        grading = node.get("gradingResult")
        if isinstance(grading, dict) and isinstance(grading.get("pass"), bool):
            if grading["pass"]:
                test_pass_count += 1
            else:
                test_fail_count += 1

        assertion = node.get("assertion")
        if isinstance(assertion, dict) and isinstance(node.get("pass"), bool):
            if node["pass"]:
                assertion_pass_count += 1
            else:
                assertion_fail_count += 1

            metric = assertion.get("metric")
            score = node.get("score")
            if isinstance(metric, str) and isinstance(score, (int, float)):
                metric_scores[metric].append(float(score))

    test_total = test_pass_count + test_fail_count
    assertion_total = assertion_pass_count + assertion_fail_count
    print(f"Promptfoo export: {path}")
    print(f"test_pass={test_pass_count}")
    print(f"test_fail={test_fail_count}")
    if test_total:
        print(f"test_pass_rate={test_pass_count / test_total:.2%}")
    print(f"assertion_pass={assertion_pass_count}")
    print(f"assertion_fail={assertion_fail_count}")
    if assertion_total:
        print(f"assertion_pass_rate={assertion_pass_count / assertion_total:.2%}")

    for metric, scores in sorted(metric_scores.items()):
        avg = sum(scores) / len(scores)
        print(f"metric.{metric}.avg={avg:.3f} count={len(scores)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
