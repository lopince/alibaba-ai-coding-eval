#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from transformers import AutoTokenizer
from vllm.benchmarks.datasets import RandomDataset


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--concurrency", type=int, default=100)
    parser.add_argument("--input-length", type=int, default=65536)
    parser.add_argument("--output-length", type=int, default=4096)
    parser.add_argument("--prompt-pool", type=int, default=300)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()

    token = os.environ.get("VLLM_BENCH_TOKEN")
    if not token:
        raise SystemExit("VLLM_BENCH_TOKEN is required")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    dataset = RandomDataset(random_seed=0)
    print(f"PREPARE generating={args.prompt_pool} input_tokens={args.input_length}", flush=True)
    prompts = dataset.sample(
        tokenizer=tokenizer,
        num_requests=args.prompt_pool,
        input_len=args.input_length,
        output_len=args.output_length,
        range_ratio="0.0",
        prefix_len=0,
        request_id_prefix="mixed-",
    )
    print("PREPARE_DONE", flush=True)

    started_wall = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    started = time.monotonic()
    deadline = started + args.duration
    next_prompt = 0
    counters = defaultdict(int)
    windows = defaultdict(lambda: defaultdict(float))
    ttfts = []
    e2es = []
    errors = defaultdict(int)

    def window_index(timestamp):
        return max(0, min(args.duration // 30 - 1, int((timestamp - started) // 30)))

    async def execute_request(session, sample):
        request_started = time.monotonic()
        first_token_at = None
        output_parts = []
        streamed_estimate = 0
        body = {
            "model": args.model,
            "prompt": sample.prompt,
            "max_tokens": args.output_length,
            "temperature": 0,
            "ignore_eos": True,
            "stream": True,
        }
        try:
            async with session.post(
                args.base_url.rstrip("/") + args.endpoint,
                headers={"Authorization": f"Bearer {token}"},
                json=body,
            ) as response:
                if response.status != 200:
                    errors[f"http_{response.status}"] += 1
                    counters["failed"] += 1
                    await response.read()
                    return
                buffer = ""
                async for chunk in response.content.iter_any():
                    buffer += chunk.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        payload = line[5:].strip()
                        if not payload or payload == "[DONE]":
                            continue
                        try:
                            event = json.loads(payload)
                            text = event.get("choices", [{}])[0].get("text", "")
                        except (json.JSONDecodeError, IndexError, TypeError):
                            continue
                        if text:
                            now = time.monotonic()
                            if first_token_at is None:
                                first_token_at = now
                                ttfts.append(now - request_started)
                                windows[window_index(now)]["prefill_tokens"] += sample.prompt_len
                            output_parts.append(text)
                            estimated = len(tokenizer.encode(text, add_special_tokens=False))
                            streamed_estimate += estimated
                            windows[window_index(now)]["decode_tokens"] += estimated
                finished = time.monotonic()
                exact_output = len(tokenizer.encode("".join(output_parts), add_special_tokens=False))
                windows[window_index(finished)]["decode_tokens"] += exact_output - streamed_estimate
                counters["output_tokens"] += exact_output
                counters["completed"] += 1
                if first_token_at is not None:
                    counters["input_tokens"] += sample.prompt_len
                    e2es.append(finished - request_started)
                windows[window_index(finished)]["completed"] += 1
        except asyncio.CancelledError:
            counters["cancelled_at_deadline"] += 1
            exact_output = len(tokenizer.encode("".join(output_parts), add_special_tokens=False))
            windows[window_index(time.monotonic())]["decode_tokens"] += exact_output - streamed_estimate
            counters["output_tokens"] += exact_output
            if first_token_at is not None:
                counters["input_tokens"] += sample.prompt_len
            raise
        except Exception as exc:
            errors[type(exc).__name__] += 1
            counters["failed"] += 1
            windows[window_index(time.monotonic())]["failed"] += 1

    async def worker(session):
        nonlocal next_prompt
        while time.monotonic() < deadline:
            sample = prompts[next_prompt % len(prompts)]
            next_prompt += 1
            counters["submitted"] += 1
            await execute_request(session, sample)

    timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=None)
    connector = aiohttp.TCPConnector(limit=args.concurrency)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [asyncio.create_task(worker(session)) for _ in range(args.concurrency)]
        print(f"RUN_START utc={started_wall} duration={args.duration} concurrency={args.concurrency}", flush=True)
        for second in range(30, args.duration + 1, 30):
            await asyncio.sleep(max(0, started + second - time.monotonic()))
            index = second // 30 - 1
            window = windows[index]
            print(
                f"WINDOW seconds={second-30}-{second} prefill_tok_s={window['prefill_tokens']/30:.2f} "
                f"decode_tok_s={window['decode_tokens']/30:.2f} completed={int(window['completed'])} "
                f"failed={int(window['failed'])}",
                flush=True,
            )
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    result_windows = []
    for index in range(args.duration // 30):
        window = windows[index]
        result_windows.append({
            "start_second": index * 30,
            "end_second": (index + 1) * 30,
            "prefill_tokens_per_second": window["prefill_tokens"] / 30,
            "decode_tokens_per_second": window["decode_tokens"] / 30,
            "completed": int(window["completed"]),
            "failed": int(window["failed"]),
        })
    result = {
        "date": started_wall,
        "duration_seconds": args.duration,
        "concurrency": args.concurrency,
        "input_length": args.input_length,
        "output_length": args.output_length,
        "unique_prompt_pool": len(prompts),
        "completed": counters["completed"],
        "failed": counters["failed"],
        "cancelled_at_deadline": counters["cancelled_at_deadline"],
        "input_tokens": counters["input_tokens"],
        "output_tokens": counters["output_tokens"],
        "average_prefill_tokens_per_second": counters["input_tokens"] / args.duration,
        "average_decode_tokens_per_second": counters["output_tokens"] / args.duration,
        "peak_prefill_tokens_per_second": max(w["prefill_tokens_per_second"] for w in result_windows),
        "peak_decode_tokens_per_second": max(w["decode_tokens_per_second"] for w in result_windows),
        "ttft_seconds": {
            "p50": percentile(ttfts, 0.50),
            "p95": percentile(ttfts, 0.95),
            "p99": percentile(ttfts, 0.99),
        },
        "e2e_seconds": {
            "p50": percentile(e2es, 0.50),
            "p95": percentile(e2es, 0.95),
            "p99": percentile(e2es, 0.99),
        },
        "errors": dict(errors),
        "windows": result_windows,
    }
    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"RUN_DONE result={result_path} completed={result['completed']} failed={result['failed']}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
