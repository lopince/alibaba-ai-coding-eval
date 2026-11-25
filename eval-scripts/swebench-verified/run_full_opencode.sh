#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <run_id> <run_dir> <model> [limit] [timeout_seconds]" >&2
  exit 2
fi

RUN_ID="$1"
RUN_DIR="$2"
MODEL="$3"
LIMIT="${4:-500}"
TIMEOUT_SECONDS="${5:-900}"

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/tmp/swebench-verified-venv312/bin/python}"

mkdir -p "${RUN_DIR}"

{
  echo "RUN_ID=${RUN_ID}"
  echo "RUN_DIR=${RUN_DIR}"
  echo "MODEL=${MODEL}"
  echo "LIMIT=${LIMIT}"
  echo "TIMEOUT_SECONDS=${TIMEOUT_SECONDS}"
  echo "STARTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${RUN_DIR}/run.info"

cd "${REPO_DIR}"

"${PYTHON_BIN}" eval-scripts/swebench-verified/run_agent.py \
  --limit "${LIMIT}" \
  --workdir "${RUN_DIR}/work" \
  --out "${RUN_DIR}/predictions.jsonl" \
  --model-name "${RUN_ID}" \
  --timeout "${TIMEOUT_SECONDS}" \
  --agent-cmd "opencode run --model ${MODEL} --dir {repo_dir} --file {prompt_file} --dangerously-skip-permissions \"Solve the attached SWE-bench issue. Modify the repository, run relevant tests if practical, do not commit changes, and leave the final solution as working tree changes.\"" \
  > "${RUN_DIR}/generate.log" 2>&1

echo "GENERATION_DONE_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${RUN_DIR}/run.info"

"${PYTHON_BIN}" -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path "${RUN_DIR}/predictions.jsonl" \
  --run_id "${RUN_ID}" \
  --max_workers 2 \
  > "${RUN_DIR}/evaluate.log" 2>&1

echo "EVALUATION_DONE_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${RUN_DIR}/run.info"
