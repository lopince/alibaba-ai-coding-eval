# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What This Repo Is

An evaluation framework for Alibaba's AI coding ecosystem — benchmarking Qwen models, Qoder CLI, and agent harnesses against the frontier landscape (Codex, DeepSeek, GLM, Kimi). This is primarily a **research and documentation repo**, not an application. There are no build scripts or package managers at the root.

## Repository Layout

- **`README.md`** — the single source of truth. Contains all 5 sections of the evaluation: AliCloud overview, Qoder overview, CLI eval (with session results), Qwen model benchmarks, and harness evaluation methodology. Most edits happen here.
- **`docs/`** — static HTML site rendering the README content across 6 pages (index + 5 sections). Pure HTML/CSS, no JS framework. `style.css` is shared. When updating README content, the corresponding HTML file must be updated to match.
- **`eval-repos/`** — synthetic FastAPI repos used as controlled test environments for CLI evaluation sessions. Each sub-repo (`memory-test-repo`, `eval-cc`, `eval-qoder`) is an independent Python project with its own `pyproject.toml`. These are deliberately seeded with legacy patterns (e.g., `unittest` instead of `pytest`, `marshmallow` instead of `pydantic`) to test whether tools follow existing conventions vs. new instructions.
- **`eval-results/`** — JSON output from evaluation sessions, organized as `session{N}/{tool}-step{N}.json`. Files are Codex `result`-type JSON with timing, token usage, cost, and the model's text output.
- **`vibe_images/`** — screenshots of Alibaba AI products (AgentBay, ADK, Model Studio, etc.) referenced in the README.

## Eval-Repo Conventions

The eval-repos are test fixtures, not production code:

- `memory-test-repo/` — the canonical synthetic repo with 5 planted "memory seeds" (M1–M5) used to test whether CLI tools retain and apply instructions across a session.
- `eval-cc/` and `eval-qoder/` — copies used for separate Codex and Qoder CLI evaluation runs, so results aren't contaminated by the other tool's edits.
- Tests use `python -m unittest discover tests/` (legacy `unittest` style). `pytest` is listed as an optional dependency but tests are written in `unittest`.
- The README's "Auth" section mentions Bearer tokens, but no actual auth middleware exists — this is intentional scaffolding for eval tasks.

## Running Eval-Repos Locally

```bash
cd eval-repos/<repo>
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
uvicorn app.main:app --reload        # run the API
python -m unittest discover tests/   # run tests
```

## Key Evaluation Concepts

- **Memory eval** — plant instructions in a session, then test if the tool applies them later. M1–M4 are explicit; M5 is implicit (never stated, tests if the tool infers from existing patterns).
- **Harness effect** — the same model scores differently depending on the CLI tool wrapping it. Always report model+harness together.
- **Fair comparison** — fix the harness and swap only the LLM backend, or fix the model and swap harnesses. Never vary both at once.
- Both tools in Session 1 used **qwen3.7-max** as the underlying model for a controlled comparison.

## Tool-Specific Config

- `.Codex/settings.local.json` — Codex project settings
- `.qoder/settings.local.json` — Qoder CLI project settings
- Both directories are `.gitignore`'d at the tool level; only `settings.local.json` is tracked here.
