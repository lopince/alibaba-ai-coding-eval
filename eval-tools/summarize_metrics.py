#!/usr/bin/env python3
"""Summarize a self-host LLM evaluation run directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    baseline = load_json(run_dir / "baseline-output.json")
    candidate = load_json(run_dir / "candidate-output.json")
    static = load_json(run_dir / "static-analysis.json")
    judge = load_json(run_dir / "llm-judge.json")

    baseline_passed = baseline.get("passed")
    candidate_passed = candidate.get("passed")
    regression = baseline_passed is True and candidate_passed is False

    summary = {
        "run_dir": str(run_dir),
        "tier1": {
            "baseline_passed": baseline_passed,
            "candidate_passed": candidate_passed,
            "regression": regression,
            "test_pass_rate": 1.0 if candidate_passed else (0.0 if candidate_passed is False else "N/A"),
        },
        "static_findings": static.get("findings", []),
        "llm_judge_metrics": judge.get("metrics", judge),
        "recommendation": "review-needed",
    }
    if baseline_passed is True and candidate_passed is True and not static.get("findings"):
        summary["recommendation"] = "pass"
    elif regression or candidate_passed is False:
        summary["recommendation"] = "fail"

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
