#!/usr/bin/env python3
"""Summarize a Promptfoo JSON export for the long-horizon benchmark.

Promptfoo's JSON schema can evolve, so this script is deliberately defensive:
it walks the export tree, finds assertion-like records, and reports pass/fail
counts plus the weighted core score model used by the evaluation page.
"""

from __future__ import annotations

import json
import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


CORE_WEIGHTS = {
    "context_retention": 30,
    "stage_completion": 30,
    "workflow_continuity": 25,
    "reviewability": 15,
}

HARD_CHECK_METRICS = {
    "required_id_present",
    "stage_named",
    "no_placeholders",
}


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def find_results(data: Any) -> list[dict]:
    results = data.get("results", {}).get("results") if isinstance(data, dict) else None
    if isinstance(results, list):
        return [item for item in results if isinstance(item, dict)]
    return []


def metric_name_from_component(component: dict) -> str | None:
    assertion = component.get("assertion")
    if isinstance(assertion, dict) and isinstance(assertion.get("metric"), str):
        return assertion["metric"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Promptfoo long-horizon results.")
    parser.add_argument("results_json", type=Path, help="Promptfoo JSON export.")
    parser.add_argument("--json-out", type=Path, help="Optional summary JSON path.")
    args = parser.parse_args()

    path = args.results_json
    data = json.loads(path.read_text(encoding="utf-8"))

    test_pass_count = 0
    test_fail_count = 0
    assertion_pass_count = 0
    assertion_fail_count = 0
    metric_scores: dict[str, list[float]] = defaultdict(list)
    case_scores: list[dict[str, Any]] = []

    for node in walk(data):
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

    for result in find_results(data):
        grading = result.get("gradingResult")
        if not isinstance(grading, dict):
            continue

        passed = grading.get("pass")
        if isinstance(passed, bool):
            if passed:
                test_pass_count += 1
            else:
                test_fail_count += 1

        vars_ = result.get("vars") if isinstance(result.get("vars"), dict) else {}
        named_scores = grading.get("namedScores") if isinstance(grading.get("namedScores"), dict) else {}
        component_results = grading.get("componentResults") if isinstance(grading.get("componentResults"), list) else []

        core_scores: dict[str, float] = {}
        hard_checks: dict[str, bool] = {}

        for metric, score in named_scores.items():
            if isinstance(metric, str) and isinstance(score, (int, float)):
                if metric in CORE_WEIGHTS:
                    core_scores[metric] = float(score)

        for component in component_results:
            if not isinstance(component, dict):
                continue
            metric = metric_name_from_component(component)
            if metric in HARD_CHECK_METRICS and isinstance(component.get("pass"), bool):
                hard_checks[metric] = bool(component["pass"])
            if metric in CORE_WEIGHTS and isinstance(component.get("score"), (int, float)):
                core_scores[metric] = float(component["score"])

        weighted_total = 0.0
        observed_weight = 0
        for metric, weight in CORE_WEIGHTS.items():
            if metric in core_scores:
                weighted_total += core_scores[metric] * weight
                observed_weight += weight

        weighted_score = weighted_total / observed_weight if observed_weight else None
        case_scores.append(
            {
                "case_id": vars_.get("case_id"),
                "stage": vars_.get("stage"),
                "passed": passed,
                "weighted_score": weighted_score,
                "core_scores": core_scores,
                "hard_checks": hard_checks,
            }
        )

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

    scored_cases = [case for case in case_scores if isinstance(case.get("weighted_score"), (int, float))]
    if scored_cases:
        overall = sum(float(case["weighted_score"]) for case in scored_cases) / len(scored_cases)
        print(f"long_horizon_score={overall:.3f}")
        print(f"long_horizon_score_percent={overall * 100:.1f}%")

    print("\nCase Scores")
    for case in case_scores:
        score = case.get("weighted_score")
        score_text = f"{score:.3f}" if isinstance(score, (int, float)) else "n/a"
        case_id = case.get("case_id") or "unknown"
        stage = case.get("stage") or "unknown"
        print(f"- {case_id} | {stage} | score={score_text} | passed={case.get('passed')}")

    if args.json_out:
        summary = {
            "source": str(path),
            "test_pass": test_pass_count,
            "test_fail": test_fail_count,
            "assertion_pass": assertion_pass_count,
            "assertion_fail": assertion_fail_count,
            "core_weights": CORE_WEIGHTS,
            "long_horizon_score": (
                sum(float(case["weighted_score"]) for case in scored_cases) / len(scored_cases)
                if scored_cases
                else None
            ),
            "cases": case_scores,
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
