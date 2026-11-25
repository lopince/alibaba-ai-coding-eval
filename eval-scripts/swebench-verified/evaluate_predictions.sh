#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <predictions.jsonl> <run_id> [max_workers]" >&2
  exit 2
fi

PREDICTIONS_PATH="$1"
RUN_ID="$2"
MAX_WORKERS="${3:-4}"

python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path "${PREDICTIONS_PATH}" \
  --run_id "${RUN_ID}" \
  --max_workers "${MAX_WORKERS}"
