#!/usr/bin/env python3
"""Small Terminal-Bench runner for model+harness smoke tests.

The script has two modes:

1. --dry-run: run a built-in local terminal task without installing Terminal-Bench.
2. real mode: prepare a task prompt/workdir and invoke a user-provided agent command.

The real benchmark score should come from the official Terminal-Bench harness.
This wrapper is intentionally lightweight so local PoC runs can record consistent
metadata and verify that a harness can execute terminal tasks.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path


SMOKE_TASK_ID = "smoke_file_task"
SMOKE_PROMPT = """#!/bin/sh
set -eu
echo "Terminal-Bench smoke task"
mkdir -p "$TASK_DIR"
echo "ok" > "$TASK_DIR/answer.txt"
"""


def shell_run(command: str, cwd: Path | None, timeout: int) -> tuple[int, str, bool, float]:
    start = time.time()
    process = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else None,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    try:
        stdout, _ = process.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, _ = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, _ = process.communicate()
        timed_out = True

    elapsed = time.time() - start
    return process.returncode, stdout, timed_out, elapsed


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def build_real_prompt(task_id: str) -> str:
    return f"""You are running a Terminal-Bench task.

Task ID: {task_id}

Use the terminal and files in the task working directory to complete the task.
When finished, leave the environment in the solved state. Do not delete logs.
"""


def run_one(args: argparse.Namespace, task_id: str, prompt: str) -> int:
    safe_id = task_id.replace("/", "__")
    task_dir = args.workdir / "tasks" / safe_id
    prompt_file = args.workdir / "prompts" / f"{safe_id}.sh"
    log_file = args.workdir / "logs" / f"{safe_id}.log"

    task_dir.mkdir(parents=True, exist_ok=True)
    write_prompt(prompt_file, prompt)

    command = args.agent_cmd.format(
        task_id=shlex.quote(task_id),
        task_dir=shlex.quote(str(task_dir)),
        prompt_file=shlex.quote(str(prompt_file)),
    )

    env_prefix = f"TASK_DIR={shlex.quote(str(task_dir))} "
    returncode, stdout, timed_out, elapsed = shell_run(env_prefix + command, cwd=task_dir, timeout=args.timeout)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(stdout, encoding="utf-8")

    passed = False
    if args.dry_run:
        passed = (task_dir / "answer.txt").read_text(encoding="utf-8").strip() == "ok" if (task_dir / "answer.txt").exists() else False

    append_jsonl(
        args.out,
        {
            "benchmark": "Terminal-Bench",
            "task_id": task_id,
            "model_name": args.model_name,
            "agent_command": args.agent_cmd,
            "dry_run": args.dry_run,
            "passed": passed if args.dry_run else None,
            "returncode": returncode,
            "timed_out": timed_out,
            "elapsed_seconds": round(elapsed, 3),
            "task_dir": str(task_dir),
            "log_file": str(log_file),
        },
    )

    status = "pass" if passed else "ran"
    if returncode != 0 or timed_out:
        status = "fail"
    print(f"[terminal-bench] {task_id}: {status} returncode={returncode} timed_out={timed_out} elapsed={elapsed:.1f}s")

    return 0 if (not args.dry_run or passed) and returncode == 0 and not timed_out else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a small Terminal-Bench harness sample.")
    parser.add_argument("--dry-run", action="store_true", help="Run the built-in smoke task.")
    parser.add_argument("--task-id", default=None, help="Terminal-Bench task ID for real runs.")
    parser.add_argument("--workdir", type=Path, required=True, help="Working directory for task files and logs.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL result file.")
    parser.add_argument("--model-name", required=True, help="Model/harness label for reporting.")
    parser.add_argument(
        "--agent-cmd",
        required=True,
        help="Agent command template. Supports {prompt_file}, {task_dir}, and {task_id}.",
    )
    parser.add_argument("--timeout", type=int, default=900, help="Per-task timeout in seconds.")
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        return run_one(args, SMOKE_TASK_ID, SMOKE_PROMPT)

    if not args.task_id:
        print("--task-id is required unless --dry-run is used", file=sys.stderr)
        return 2

    return run_one(args, args.task_id, build_real_prompt(args.task_id))


if __name__ == "__main__":
    sys.exit(main())
