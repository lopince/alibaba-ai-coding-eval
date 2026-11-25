#!/usr/bin/env bash
set -u

if [[ -z "${VLLM_BENCH_TOKEN:-}" ]]; then
  echo "VLLM_BENCH_TOKEN is required" >&2
  exit 2
fi

benchmark_root="$(cd "$(dirname "$0")" && pwd)"
results_root="${benchmark_root}/results/deepseek-v4-flash-0731-exp1-64k-out128"
mkdir -p "$results_root"

base_url="http://k8s-kserve-kservein-ccf72f666e-e974e7e4f01815e3.elb.us-east-1.amazonaws.com"
endpoint="/llm-demo/ossv2/v1/completions"
model="deepseek-ai/DeepSeek-V4-Flash-0731"
levels=(1 10 20 30 40 50 60 80 100)

for concurrency in "${levels[@]}"; do
  for repetition in 1 2 3; do
    run_base="deepseek-v4-flash-0731-64k-out128-c${concurrency}-r${repetition}"
    run_satisfied=false

    for existing_path in "${results_root}/${run_base}.json" "${results_root}/${run_base}-retry1.json"; do
      if [[ -f "$existing_path" ]] && [[ "$(jq -r '.completed' "$existing_path")" == "$concurrency" ]] && [[ "$(jq -r '.failed' "$existing_path")" == "0" ]]; then
        echo "RUN_SKIP concurrency=${concurrency} repetition=${repetition} successful_file=$(basename "$existing_path")"
        run_satisfied=true
        break
      fi
    done

    if [[ "$run_satisfied" == true ]]; then
      continue
    fi

    for attempt in 0 1; do
      retry_index=$attempt
      if [[ -f "${results_root}/${run_base}.json" ]]; then
        retry_index=$((attempt + 1))
      fi
      retry_suffix=""
      if [[ $retry_index -gt 0 ]]; then
        retry_suffix="-retry${retry_index}"
      fi
      filename="${run_base}${retry_suffix}.json"
      echo "RUN_START concurrency=${concurrency} repetition=${repetition} attempt=$((attempt + 1)) file=${filename}"

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
        --prefix-repetition-prefix-len 52429 \
        --prefix-repetition-suffix-len 13107 \
        --prefix-repetition-output-len 128 \
        --num-prompts "$concurrency" \
        --max-concurrency "$concurrency" \
        --ignore-eos \
        --temperature 0 \
        --percentile-metrics ttft,tpot,itl,e2el \
        --metric-percentiles 50,75,90,95,99 \
        --save-result \
        --save-detailed \
        --result-dir /results/deepseek-v4-flash-0731-exp1-64k-out128 \
        --result-filename "$filename"

      command_exit=$?
      result_path="${results_root}/${filename}"
      if [[ $command_exit -ne 0 || ! -f "$result_path" ]]; then
        echo "RUN_FAILED docker_exit=${command_exit} missing_result=${result_path}" >&2
        continue
      fi

      completed=$(jq -r '.completed' "$result_path")
      failed=$(jq -r '.failed' "$result_path")
      p95_ttft_ms=$(jq -r '.p95_ttft_ms // 0' "$result_path")
      echo "RUN_DONE concurrency=${concurrency} repetition=${repetition} completed=${completed} failed=${failed} p95_ttft_ms=${p95_ttft_ms}"

      if (( failed * 100 > concurrency * 5 )); then
        echo "RUN_FAILED failure_rate_above_5_percent concurrency=${concurrency} failed=${failed}" >&2
        continue
      fi

      if awk "BEGIN { exit !(${p95_ttft_ms} > 300000) }"; then
        echo "STOP p95_ttft_above_300_seconds concurrency=${concurrency} p95_ttft_ms=${p95_ttft_ms}" >&2
        exit 5
      fi

      run_satisfied=true
      sleep 30
      break
    done

    if [[ "$run_satisfied" != true ]]; then
      echo "STOP repeated_failure concurrency=${concurrency} repetition=${repetition}" >&2
      exit 4
    fi
  done
done

echo "SWEEP_COMPLETE"
