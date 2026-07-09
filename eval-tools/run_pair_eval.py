#!/usr/bin/env python3
"""Run baseline and candidate commands and store raw results."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


def run_command(command: str, timeout: int) -> dict:
    start = time.time()
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    elapsed = time.time() - start
    return {
        "command": command,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "elapsed_seconds": round(elapsed, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--baseline-command", required=True)
    parser.add_argument("--candidate-command", required=True)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    run_dir = Path("eval-runs") / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    baseline = run_command(args.baseline_command, args.timeout)
    candidate = run_command(args.candidate_command, args.timeout)

    (run_dir / "baseline-output.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    (run_dir / "candidate-output.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "baseline": baseline["passed"], "candidate": candidate["passed"]}, indent=2))
    return 0 if baseline["passed"] and candidate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
