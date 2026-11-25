#!/usr/bin/env python3
"""Generate SWE-bench Verified predictions by driving a CLI coding agent.

This script is intentionally small and harness-agnostic. It checks out each
SWE-bench repo at the task's base commit, writes an issue prompt, invokes a
user-provided CLI command, then records the resulting git diff as model_patch.
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

from datasets import load_dataset


DATASET_NAME = "princeton-nlp/SWE-bench_Verified"


def run(cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def shell_run(command: str, timeout: int | None = None) -> tuple[subprocess.CompletedProcess[str], bool]:
    process = subprocess.Popen(
        command,
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
            stdout, _ = process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, _ = process.communicate()
        timed_out = True

    return subprocess.CompletedProcess(command, process.returncode, stdout, None), timed_out


def build_prompt(instance: dict) -> str:
    return f"""You are solving a SWE-bench Verified task.

Repository: {instance["repo"]}
Instance ID: {instance["instance_id"]}
Base commit: {instance["base_commit"]}

Issue:
{instance["problem_statement"]}

Instructions:
- Modify the repository to resolve the issue.
- Keep the change minimal and focused.
- Run relevant tests if practical.
- Do not commit changes.
- Leave the final solution as working tree changes so `git diff` contains the patch.
"""


def checkout_repo(instance: dict, repo_dir: Path) -> None:
    if repo_dir.exists():
        return

    repo_url = f"https://github.com/{instance['repo']}.git"
    repo_dir.parent.mkdir(parents=True, exist_ok=True)

    clone = run(["git", "clone", repo_url, str(repo_dir)], timeout=1800)
    if clone.returncode != 0:
        raise RuntimeError(f"git clone failed for {repo_url}\n{clone.stdout}")

    checkout = run(["git", "checkout", instance["base_commit"]], cwd=repo_dir, timeout=300)
    if checkout.returncode != 0:
        raise RuntimeError(f"git checkout failed for {instance['instance_id']}\n{checkout.stdout}")


def collect_patch(repo_dir: Path) -> str:
    diff = run(["git", "diff", "--binary"], cwd=repo_dir, timeout=300)
    if diff.returncode != 0:
        raise RuntimeError(f"git diff failed in {repo_dir}\n{diff.stdout}")
    return diff.stdout


def reset_repo(repo_dir: Path) -> None:
    run(["git", "reset", "--hard"], cwd=repo_dir, timeout=300)
    run(["git", "clean", "-fd"], cwd=repo_dir, timeout=300)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a CLI agent over SWE-bench Verified tasks.")
    parser.add_argument("--limit", type=int, default=1, help="Number of instances to run.")
    parser.add_argument("--offset", type=int, default=0, help="Dataset offset.")
    parser.add_argument("--workdir", type=Path, required=True, help="Working directory for repo checkouts and prompts.")
    parser.add_argument("--out", type=Path, required=True, help="Output predictions JSONL path.")
    parser.add_argument("--model-name", required=True, help="Value for model_name_or_path in SWE-bench predictions.")
    parser.add_argument(
        "--agent-cmd",
        required=True,
        help="CLI command template. Supports {repo_dir}, {prompt_file}, {instance_id}.",
    )
    parser.add_argument("--timeout", type=int, default=3600, help="Per-instance agent timeout in seconds.")
    args = parser.parse_args()

    dataset = load_dataset(DATASET_NAME, split="test")
    selected = dataset.select(range(args.offset, min(args.offset + args.limit, len(dataset))))

    args.workdir.mkdir(parents=True, exist_ok=True)

    for instance in selected:
        instance_id = instance["instance_id"]
        safe_id = instance_id.replace("/", "__")
        repo_dir = args.workdir / "repos" / safe_id
        prompt_file = args.workdir / "prompts" / f"{safe_id}.md"
        log_file = args.workdir / "logs" / f"{safe_id}.log"

        print(f"[swebench] {instance_id}", flush=True)
        checkout_repo(instance, repo_dir)
        reset_repo(repo_dir)

        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(build_prompt(instance), encoding="utf-8")

        command = args.agent_cmd.format(
            repo_dir=shlex.quote(str(repo_dir)),
            prompt_file=shlex.quote(str(prompt_file)),
            instance_id=shlex.quote(instance_id),
        )

        start = time.time()
        result, timed_out = shell_run(command, timeout=args.timeout)
        elapsed = time.time() - start

        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(result.stdout, encoding="utf-8")

        patch = collect_patch(repo_dir)
        append_jsonl(
            args.out,
            {
                "instance_id": instance_id,
                "model_name_or_path": args.model_name,
                "model_patch": patch,
                "metadata": {
                    "agent_command": args.agent_cmd,
                    "returncode": result.returncode,
                    "timed_out": timed_out,
                    "elapsed_seconds": round(elapsed, 3),
                    "log_file": str(log_file),
                },
            },
        )

        print(
            f"[swebench] wrote patch for {instance_id}: "
            f"{len(patch)} chars, returncode={result.returncode}, timed_out={timed_out}, elapsed={elapsed:.1f}s",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
