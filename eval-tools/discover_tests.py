#!/usr/bin/env python3
"""Discover candidate tests or validation checks for self-host LLM evals."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def split_scope(scope: str) -> tuple[str, str]:
    if ":" not in scope:
        return scope, ""
    left, right = scope.split(":", 1)
    return left.strip(), right.strip()


def repo_files(root: Path) -> list[Path]:
    ignored = {
        ".git", ".venv", "venv", "node_modules", "build", "dist", "target", ".gradle",
        ".uv-cache", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache",
    }
    out: list[Path] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
        for name in files:
            out.append(Path(base) / name)
    return out


def find_project_root(reference: Path) -> Path:
    start = reference.resolve().parent if reference.exists() else Path.cwd()
    markers = {
        "pyproject.toml", "setup.py", "setup.cfg", "tox.ini",
        "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "pom.xml",
        "README.md", ".git",
    }
    current = start
    cwd = Path.cwd().resolve()
    while True:
        if any((current / marker).exists() for marker in markers):
            return current
        if current == cwd or current.parent == current:
            return cwd
        current = current.parent


def confidence(reason_hits: int) -> float:
    return min(0.98, 0.45 + reason_hits * 0.17)


def discover_python(root: Path, reference: Path, scope_target: str) -> list[dict]:
    ref_stem = reference.stem
    symbols = [s for s in re.split(r"[^A-Za-z0-9_]+", scope_target) if s and s not in {"function", "method"}]
    tests = [
        p for p in repo_files(root)
        if p.suffix == ".py" and (p.name.startswith("test_") or p.name.endswith("_test.py") or "tests" in p.parts)
    ]
    results = []
    for path in tests:
        text = read_text(path)
        reasons = []
        if ref_stem in text:
            reasons.append(f"mentions reference module `{ref_stem}`")
        for symbol in symbols:
            if symbol and symbol in text:
                reasons.append(f"mentions scope symbol `{symbol}`")
        if reference.parent.name and reference.parent.name in str(path):
            reasons.append("path is near the reference package")
        if not reasons and ref_stem.lower() in path.stem.lower():
            reasons.append("test filename matches reference module")
        if reasons:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            module_name = str(rel.with_suffix("")).replace("/", ".")
            results.append({
                "path": str(rel),
                "kind": "unit-test",
                "confidence": round(confidence(len(reasons)), 2),
                "reason": "; ".join(reasons),
                "suggested_command": f"python -m unittest {module_name}",
            })
    return sorted(results, key=lambda item: item["confidence"], reverse=True)


def discover_jvm(root: Path, reference: Path, scope_target: str) -> list[dict]:
    ref_stem = reference.stem
    class_or_method = scope_target.split("::")[-1].split(".")[0]
    tests = [
        p for p in repo_files(root)
        if p.suffix in {".kt", ".java"} and (
            "src/test" in p.as_posix()
            or p.name.endswith(("Test.kt", "Tests.kt", "IT.kt", "Test.java", "Tests.java", "IT.java"))
        )
    ]
    results = []
    for path in tests:
        text = read_text(path)
        reasons = []
        if ref_stem in text or ref_stem in path.stem:
            reasons.append(f"matches reference class/file `{ref_stem}`")
        if class_or_method and class_or_method in text:
            reasons.append(f"mentions scope target `{class_or_method}`")
        if "src/test" in path.as_posix():
            reasons.append("located under JVM test source tree")
        if reasons:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            test_filter = path.stem
            results.append({
                "path": str(rel),
                "kind": "unit-test",
                "confidence": round(confidence(len(reasons)), 2),
                "reason": "; ".join(reasons),
                "suggested_command": f"./gradlew test --tests '*{test_filter}*'",
            })
    return sorted(results, key=lambda item: item["confidence"], reverse=True)


def discover_docs(root: Path, reference: Path, candidate: Path) -> list[dict]:
    checks = [
        {
            "path": str(candidate),
            "kind": "doc-check",
            "confidence": 0.9,
            "reason": "verify candidate documentation against reference source truth",
            "suggested_command": f"python3 eval-tools/static_compare.py --task-family docs --reference {reference} --candidate {candidate} --scope docs",
        },
        {
            "path": str(candidate),
            "kind": "llm-judge",
            "confidence": 0.85,
            "reason": "score documentation accuracy, completeness, clarity, and usefulness with evidence",
            "suggested_command": "LLM judge using documentation rubric",
        },
    ]
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--task-family", required=True, choices=["python", "kotlin-java", "docs"])
    parser.add_argument("--scope", required=True)
    args = parser.parse_args()

    reference = Path(args.reference)
    candidate = Path(args.candidate)
    root = find_project_root(reference)
    scope_type, scope_target = split_scope(args.scope)

    if args.task_family == "python":
        candidates = discover_python(root, reference, scope_target)
    elif args.task_family == "kotlin-java":
        candidates = discover_jvm(root, reference, scope_target)
    else:
        candidates = discover_docs(root, reference, candidate)

    print(json.dumps({
        "reference": str(reference),
        "candidate": str(candidate),
        "task_family": args.task_family,
        "scope_type": scope_type,
        "scope_target": scope_target,
        "candidates": candidates,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
