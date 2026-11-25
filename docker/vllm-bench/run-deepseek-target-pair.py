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


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--warmup-seconds", type=int, default=180)
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--request-rate", type=float, default=0.2)
    parser.add_argument("--concurrency-cap", type=int, default=100)
    parser.add_argument("--input-length", type=int, default=65536)
    parser.add_argument("--output-length", type=int, default=15020)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()

    token = os.environ.get("VLLM_BENCH_TOKEN")
    if not token:
        raise SystemExit("VLLM_BENCH_TOKEN is required")

    total_seconds = args.warmup_seconds + args.duration
    prompt_count = int(total_seconds * args.request_rate) + 10
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    dataset = RandomDataset(random_seed=17)
    print(f"PREPARE generating={prompt_count} input_tokens={args.input_length}", flush=True)
    prompts = dataset.sample(
        tokenizer=tokenizer,
        num_requests=prompt_count,
        input_len=args.input_length,
        output_len=args.output_length,
        range_ratio="0.0",
        prefix_len=0,
        request_id_prefix="target-pair-",
    )
    print("PREPARE_DONE", flush=True)

    run_started = time.monotonic()
    measure_started = run_started + args.warmup_seconds
    deadline = measure_started + args.duration
    started_wall = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    interval = 1 / args.request_rate
    semaphore = asyncio.Semaphore(args.concurrency_cap)
    tasks = set()
    windows = defaultdict(lambda: defaultdict(float))
    counters = defaultdict(int)
    errors = defaultdict(int)
    active = 0
    peak_active = 0

    def measured_window(timestamp):
        if timestamp < measure_started or timestamp >= deadline:
            return None
        return int((timestamp - measure_started) // 30)

    async def request(session, sample, submitted_at):
        nonlocal active, peak_active
        async with semaphore:
            active += 1
            peak_active = max(peak_active, active)
            first_token = None
            output_parts = []
            streamed_estimate = 0
            try:
                body = {
                    "model": args.model,
                    "prompt": sample.prompt,
                    "max_tokens": args.output_length,
                    "temperature": 0,
                    "ignore_eos": True,
                    "stream": True,
                }
                async with session.post(
                    args.base_url.rstrip("/") + args.endpoint,
                    headers={"Authorization": f"Bearer {token}"},
                    json=body,
                ) as response:
                    if response.status != 200:
                        errors[f"http_{response.status}"] += 1
                        counters["failed"] += 1
                        window = measured_window(time.monotonic())
                        if window is not None:
                            windows[window]["failed"] += 1
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
                            if not text:
                                continue
                            now = time.monotonic()
                            window = measured_window(now)
                            if first_token is None:
                                first_token = now
                                if window is not None:
                                    windows[window]["prefill_tokens"] += sample.prompt_len
                                    windows[window]["ttft_sum"] += now - submitted_at
                                    windows[window]["ttft_count"] += 1
                            output_parts.append(text)
                            estimated = len(tokenizer.encode(text, add_special_tokens=False))
                            streamed_estimate += estimated
                            if window is not None:
                                windows[window]["decode_tokens"] += estimated
                    finished = time.monotonic()
                    exact_output = len(tokenizer.encode("".join(output_parts), add_special_tokens=False))
                    window = measured_window(finished)
                    if window is not None:
                        windows[window]["decode_tokens"] += exact_output - streamed_estimate
                        windows[window]["completed"] += 1
                    counters["completed"] += 1
            except asyncio.CancelledError:
                counters["cancelled_at_deadline"] += 1
                raise
            except Exception as exc:
                errors[type(exc).__name__] += 1
                counters["failed"] += 1
                window = measured_window(time.monotonic())
                if window is not None:
                    windows[window]["failed"] += 1
            finally:
                active -= 1

    timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=None)
    connector = aiohttp.TCPConnector(limit=args.concurrency_cap)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        print(
            f"RUN_START utc={started_wall} warmup={args.warmup_seconds} measured={args.duration} "
            f"request_rate={args.request_rate} concurrency_cap={args.concurrency_cap}",
            flush=True,
        )
        next_submission = run_started
        prompt_index = 0
        next_report = run_started + 30
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now >= next_submission:
                task = asyncio.create_task(request(session, prompts[prompt_index], now))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
                counters["submitted"] += 1
                prompt_index += 1
                next_submission += interval
            if now >= next_report:
                if now < measure_started:
                    print(f"WARMUP elapsed={int(now-run_started)} active={active} completed={counters['completed']} failed={counters['failed']}", flush=True)
                else:
                    index = int((now - measure_started) // 30) - 1
                    if index >= 0:
                        window = windows[index]
                        print(
                            f"WINDOW seconds={index*30}-{(index+1)*30} prefill_tok_s={window['prefill_tokens']/30:.2f} "
                            f"decode_tok_s={window['decode_tokens']/30:.2f} completed={int(window['completed'])} "
                            f"failed={int(window['failed'])} active={active}",
                            flush=True,
                        )
                next_report += 30
            await asyncio.sleep(min(0.1, max(0, next_submission - time.monotonic())))

        for task in list(tasks):
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
            "mean_ttft_seconds": window["ttft_sum"] / window["ttft_count"] if window["ttft_count"] else None,
        })
    result = {
        "date": started_wall,
        "warmup_seconds": args.warmup_seconds,
        "duration_seconds": args.duration,
        "request_rate": args.request_rate,
        "concurrency_cap": args.concurrency_cap,
        "input_length": args.input_length,
        "output_length": args.output_length,
        "target_prefill_tokens_per_second": args.input_length * args.request_rate,
        "target_decode_tokens_per_second": args.output_length * args.request_rate,
        "submitted": counters["submitted"],
        "completed": counters["completed"],
        "failed": counters["failed"],
        "cancelled_at_deadline": counters["cancelled_at_deadline"],
        "peak_active": peak_active,
        "errors": dict(errors),
        "windows": result_windows,
    }
    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"RUN_DONE result={result_path} completed={result['completed']} failed={result['failed']} peak_active={peak_active}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
