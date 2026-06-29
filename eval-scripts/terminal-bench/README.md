# Terminal-Bench Sample Runner

This sample is for a small PoC run of **Terminal-Bench** against an agent stack such as:

- `Claude Code + Opus`
- `OpenCode + self-hosted GLM`
- another terminal-capable harness + model endpoint

Terminal-Bench evaluates whether an agent can solve tasks through a real terminal environment. This is useful for comparing a replacement harness because the score depends on both the model and the tool runner.

## What This Tests

```text
Terminal-Bench task
  -> CLI harness receives task instruction
  -> harness uses shell, files, tests, and environment
  -> benchmark checks whether the final environment satisfies the task
```

For replacement evaluation, always record the full stack:

```text
model + harness + serving stack + prompt/runtime settings
```

## Files

```text
run_terminal_bench.py   Run a small Terminal-Bench sample or dry-run smoke test
```

## Smoke Test

This does not require Terminal-Bench to be installed. It verifies that the local runner, command templating, logging, and JSONL output work.

```bash
python3 eval-scripts/terminal-bench/run_terminal_bench.py \
  --dry-run \
  --workdir /tmp/terminal-bench-smoke \
  --out /tmp/terminal-bench-smoke/results.jsonl \
  --model-name "local-smoke" \
  --agent-cmd 'sh {prompt_file}'
```

Expected result:

```text
[terminal-bench] smoke_file_task: pass
```

## Real Terminal-Bench Run

Install and run the official harness separately. The recommended official path may change, so prefer the current Terminal-Bench documentation for installation details:

- Terminal-Bench: https://www.tbench.ai/
- Terminal-Bench GitHub: https://github.com/laude-institute/terminal-bench

Once the official CLI is installed, use this wrapper to keep run metadata consistent with the rest of this repo:

```bash
python3 eval-scripts/terminal-bench/run_terminal_bench.py \
  --task-id "hello-world" \
  --workdir /tmp/terminal-bench-run \
  --out /tmp/terminal-bench-run/results.jsonl \
  --model-name "self-hosted-glm-opencode" \
  --agent-cmd 'opencode --headless --prompt-file {prompt_file} --workdir {task_dir}'
```

The `{prompt_file}`, `{task_dir}`, and `{task_id}` placeholders are replaced by the script.

If you want to invoke the official `tb` or Harbor command directly, use the same metadata convention in your report:

```text
benchmark = Terminal-Bench
model = <model name>
harness = <agent tool>
serving_stack = <gateway/inference engine>
task_set = <task subset>
score = task success rate
```

## Compare Harnesses

Run the same task subset for each stack:

```text
Claude Code + Opus
OpenCode + self-hosted GLM
OpenCode + self-hosted Qwen
```

Compare:

- task success rate
- timeout rate
- command/runtime error rate
- time per task
- tokens per task, if available from harness logs
- failure categories
