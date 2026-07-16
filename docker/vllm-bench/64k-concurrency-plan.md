# vLLM 64k Concurrency Benchmark Plan

## Goal

Test whether the remote vLLM-compatible endpoint can handle 64k-token prompts, then observe latency and throughput as concurrency increases.

This plan runs each concurrency level separately so the operator can inspect results before moving to the next step.

## Fixed Test Settings

- Backend: `vllm`
- API base URL: `http://k8s-kserve-kservein-ccf72f666e-e974e7e4f01815e3.elb.us-east-1.amazonaws.com`
- Endpoint: `/llm-demo/oss/v1/completions`
- Model: `nvidia/GLM-5.2-NVFP4`
- Dataset: `random`
- Input length: `65536` tokens
- Output length: `128` tokens
- Percentile metrics: `ttft,tpot,itl,e2el`
- Metric percentiles: `50,75,90,95,99`
- Save aggregate and detailed results
- Keep tqdm progress bar enabled

Note: the current local `local/vllm-bench:arm64` image does not support `--request-timeout`, so the benchmark commands omit that flag.

## Concurrency Matrix

Use one request wave per concurrency level:

| Run | `--max-concurrency` | `--num-prompts` | Result file |
| --- | ---: | ---: | --- |
| Baseline | 1 | 1 | `64k-c1.json` |
| Step 1 | 10 | 10 | `64k-c10.json` |
| Step 2 | 20 | 20 | `64k-c20.json` |
| Step 3 | 25 | 25 | `64k-c25.json` |
| Step 4 | 30 | 30 | `64k-c30.json` |

## Stop Conditions

Stop before the next concurrency step if any run shows:

- Any repeated timeout errors
- HTTP 429, 500, 502, 503, or 504 errors
- Failed requests above 5%
- End-to-end latency is already too high for the intended production use case
- The endpoint or cluster shows signs of saturation outside the benchmark

## Environment Setup

Set these variables once before running benchmark commands:

```bash
export VLLM_BENCH_TOKEN='<bearer-token>'
export VLLM_BENCH_BASE_URL='http://k8s-kserve-kservein-ccf72f666e-e974e7e4f01815e3.elb.us-east-1.amazonaws.com'
export VLLM_BENCH_MODEL='nvidia/GLM-5.2-NVFP4'
export VLLM_BENCH_RESULTS='/Users/lopince/workspace/alibaba-ai-coding-eval/docker/vllm-bench/results'
```

## Command Template

Replace `<C>` with the concurrency level and `<N>` with the matching prompt count from the matrix.

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts <N> \
  --max-concurrency <C> \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c<C>.json
```

## Separate Run Commands

### Concurrency 1

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts 1 \
  --max-concurrency 1 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c1.json
```

### Concurrency 10

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts 10 \
  --max-concurrency 10 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c10.json
```

### Concurrency 20

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts 20 \
  --max-concurrency 20 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c20.json
```

### Concurrency 25

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts 25 \
  --max-concurrency 25 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c25.json
```

### Concurrency 30

```bash
docker run --rm \
  -v vllm-bench_huggingface-cache:/root/.cache/huggingface \
  -v "$VLLM_BENCH_RESULTS:/results" \
  local/vllm-bench:arm64 \
  bench serve \
  --backend vllm \
  --base-url "$VLLM_BENCH_BASE_URL" \
  --endpoint /llm-demo/oss/v1/completions \
  --header "Authorization=Bearer ${VLLM_BENCH_TOKEN}" \
  --model "$VLLM_BENCH_MODEL" \
  --dataset-name random \
  --random-input-len 65536 \
  --random-output-len 128 \
  --num-prompts 30 \
  --max-concurrency 30 \
  --percentile-metrics ttft,tpot,itl,e2el \
  --metric-percentiles 50,75,90,95,99 \
  --save-result \
  --save-detailed \
  --result-dir /results \
  --result-filename 64k-c30.json
```

## Results To Compare

After each run, compare:

- Successful requests
- Failed requests
- Request throughput
- Output token throughput
- Total token throughput
- TTFT p50/p75/p90/p95/p99
- TPOT p50/p75/p90/p95/p99
- ITL p50/p75/p90/p95/p99
- E2EL p50/p75/p90/p95/p99

The most important signals for this 64k test are TTFT, end-to-end latency, failure rate, and the point where throughput stops scaling.
