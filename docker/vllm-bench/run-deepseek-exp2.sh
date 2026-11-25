#!/usr/bin/env bash
set -u
trap 'echo "STOP interrupted" >&2; exit 130' INT TERM

if [[ -z "${VLLM_BENCH_TOKEN:-}" ]]; then
  echo "VLLM_BENCH_TOKEN is required" >&2
  exit 2
fi

benchmark_root="$(cd "$(dirname "$0")" && pwd)"
results_root="${benchmark_root}/results/deepseek-v4-flash-0731-exp2-context-c10"
mkdir -p "$results_root"

base_url="http://k8s-kserve-kservein-ccf72f666e-e974e7e4f01815e3.elb.us-east-1.amazonaws.com"
endpoint="/llm-demo/ossv2/v1/completions"
model="deepseek-ai/DeepSeek-V4-Flash-0731"

labels=(8k 16k 32k 64k 128k 256k 512k near1m)
inputs=(8192 16384 32768 65536 131072 262144 524288 999871)
prefixes=(6554 13107 26214 52429 104858 209715 419430 799897)
suffixes=(1638 3277 6554 13107 26214 52429 104858 199974)

for index in "${!labels[@]}"; do
  label="${labels[$index]}"
  input="${inputs[$index]}"
  prefix="${prefixes[$index]}"
  suffix="${suffixes[$index]}"

  for repetition in 1 2 3; do
    run_base="deepseek-v4-flash-0731-exp2-${label}-r${repetition}"
    run_satisfied=false

    for existing_path in "${results_root}/${run_base}.json" "${results_root}/${run_base}-retry1.json"; do
      if [[ -f "$existing_path" ]] && [[ "$(jq -r '.completed' "$existing_path")" == "10" ]] && [[ "$(jq -r '.failed' "$existing_path")" == "0" ]]; then
        echo "RUN_SKIP context=${label} repetition=${repetition} successful_file=$(basename "$existing_path")"
        run_satisfied=true
        break
      fi
    done

    if [[ "$run_satisfied" == true ]]; then
      continue
    fi

    for attempt in 0 1; do
      retry_suffix=""
      if [[ $attempt -gt 0 || -f "${results_root}/${run_base}.json" ]]; then
        retry_suffix="-retry1"
      fi
      filename="${run_base}${retry_suffix}.json"
      echo "RUN_START context=${label} input=${input} repetition=${repetition} attempt=$((attempt + 1)) file=${filename}"

      docker run --rm \
        -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
        -v "${benchmark_root}/results:/results" \
        local/vllm-bench:arm64 \
        bench serve \
        --backend vllm \
        --base-url "$base_url" \
        --endpoint "$endpoint" \
        --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
        --model "$model" \
        --dataset-name prefix_repetition \
        --prefix-repetition-num-prefixes 1 \
        --prefix-repetition-prefix-len "$prefix" \
        --prefix-repetition-suffix-len "$suffix" \
        --prefix-repetition-output-len 128 \
        --num-prompts 10 \
        --max-concurrency 10 \
        --ignore-eos \
        --temperature 0 \
        --percentile-metrics ttft,tpot,itl,e2el \
        --metric-percentiles 50,75,90,95,99 \
        --save-result \
        --save-detailed \
        --result-dir /results/deepseek-v4-flash-0731-exp2-context-c10 \
        --result-filename "$filename"

      command_exit=$?
      result_path="${results_root}/${filename}"
      if [[ $command_exit -ne 0 || ! -f "$result_path" ]]; then
        echo "RUN_FAILED docker_exit=${command_exit} missing_result=${result_path}" >&2
        continue
      fi

      completed="$(jq -r '.completed' "$result_path")"
      failed="$(jq -r '.failed' "$result_path")"
      p95_ttft_ms="$(jq -r '.p95_ttft_ms // 0' "$result_path")"
      echo "RUN_DONE context=${label} repetition=${repetition} completed=${completed} failed=${failed} p95_ttft_ms=${p95_ttft_ms}"

      if [[ "$completed" != "10" || "$failed" != "0" ]]; then
        echo "RUN_REJECTED context=${label} repetition=${repetition}" >&2
        continue
      fi

      if awk "BEGIN { exit !(${p95_ttft_ms} > 600000) }"; then
        echo "STOP p95_ttft_above_600_seconds context=${label} p95_ttft_ms=${p95_ttft_ms}" >&2
        exit 5
      fi

      run_satisfied=true
      sleep 30
      break
    done

    if [[ "$run_satisfied" != true ]]; then
      echo "STOP repeated_failure context=${label} repetition=${repetition}" >&2
      exit 4
    fi
  done
done

echo "SWEEP_COMPLETE"
