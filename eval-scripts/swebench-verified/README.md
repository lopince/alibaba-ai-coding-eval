# SWE-bench Verified Sample Runner

This sample is for a small PoC run of **SWE-bench Verified** against a coding agent stack such as:

- `Claude Code + Opus`
- `OpenCode + self-hosted LLM`
- another CLI harness + model endpoint

SWE-bench itself evaluates final patches. To test a harness, use the harness to generate `model_patch` values, then run the official SWE-bench evaluator on those patches.

## What This Tests

SWE-bench Verified can test **model + harness together** if the prediction file is produced by the harness.

```text
SWE-bench task
  -> CLI harness reads issue and repo
  -> harness edits code
  -> git diff becomes model_patch
  -> SWE-bench Docker evaluator applies patch and runs tests
```

The official evaluator does not care whether the patch came from a raw LLM call, OpenCode, Claude Code, SWE-agent, OpenHands, or a custom script. The score is therefore only meaningful if you record the full combination:

```text
model + harness + prompt + runtime settings
```

## Files

```text
run_agent.py              Generate predictions.jsonl by calling a CLI agent
evaluate_predictions.sh   Run official SWE-bench evaluation on predictions
```

## Install

Use a clean Python environment.

```bash
pip install datasets
pip install swebench
```

Docker must be running for official evaluation.

SWE-bench recommends an x86_64 machine with roughly 120GB free storage, 16GB RAM, and 8 CPU cores for evaluation.

## Generate A Small Prediction File

Start with 1-3 instances before scaling up.

```bash
python eval-scripts/swebench-verified/run_agent.py \
  --limit 3 \
  --workdir /tmp/swebench-verified-work \
  --out /tmp/swebench-verified-predictions.jsonl \
  --model-name "self-hosted-glm-opencode" \
  --agent-cmd 'opencode --headless --prompt-file {prompt_file} --workdir {repo_dir}'
```

The `{prompt_file}` and `{repo_dir}` placeholders are replaced by the script.

If your CLI uses a different command shape, keep the placeholders and adjust the command:

```bash
--agent-cmd 'your-agent run --cwd {repo_dir} --input {prompt_file}'
```

## Evaluate Predictions

```bash
eval-scripts/swebench-verified/evaluate_predictions.sh \
  /tmp/swebench-verified-predictions.jsonl \
  self-hosted-glm-opencode-smoke
```

This runs:

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path <predictions.jsonl> \
  --run_id <run_id>
```

## Compare Harnesses

Run the same instance set for each stack:

```text
Claude Code + Opus
OpenCode + self-hosted GLM
OpenCode + self-hosted Qwen
```

Compare:

- `% resolved`
- time per task
- tokens per task, if available from the harness logs
- cost per task
- failure categories

