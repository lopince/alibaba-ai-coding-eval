# vLLM benchmark environment (Apple Silicon / ARM64 CPU)

This setup runs vLLM inside Docker's Linux ARM64 VM. It uses the Mac CPU, not
the Apple GPU. Results are useful for validating the benchmark workflow, but
they are not representative of CUDA/ROCm production performance.

## Start the server

```bash
cd docker/vllm-bench
cp .env.example .env
docker compose build
docker compose up -d server
docker compose logs -f server
```

The first start downloads the model. Wait until the health check passes:

```bash
docker compose ps
curl http://localhost:8000/health
```

## Run a small online-serving benchmark

```bash
docker compose --profile tools run --rm bench serve \
  --backend vllm \
  --host server \
  --port 8000 \
  --endpoint /v1/completions \
  --model Qwen/Qwen3-0.6B \
  --dataset-name random \
  --random-input-len 32 \
  --random-output-len 16 \
  --num-prompts 10 \
  --max-concurrency 1 \
  --save-result \
  --result-dir /results
```

Benchmark output is written to `results/`. For another model, update both
`VLLM_MODEL` in `.env` and `--model` in the benchmark command.

## Inspect commands and stop

```bash
docker compose --profile tools run --rm bench --help
docker compose --profile tools run --rm bench serve --help
docker compose down
```
