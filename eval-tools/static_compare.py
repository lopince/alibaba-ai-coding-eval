#!/usr/bin/env python3
"""Static comparison helper for self-host LLM evals."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    if path.is_dir():
        chunks = []
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix in {".py", ".kt", ".java", ".md", ".rst"}:
                chunks.append(f"\n# {child}\n{child.read_text(encoding='utf-8', errors='ignore')}")
        return "\n".join(chunks)
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def python_symbols(text: str) -> dict:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {"syntax_error": str(exc), "functions": {}, "classes": {}}
    functions = {}
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = {
                "args": [arg.arg for arg in node.args.args],
                "async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif isinstance(node, ast.ClassDef):
            classes[node.name] = sorted(
                item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
    return {"functions": functions, "classes": classes}


def jvm_symbols(text: str) -> dict:
    class_names = sorted(set(re.findall(r"\b(?:class|interface|object|enum)\s+([A-Z][A-Za-z0-9_]*)", text)))
    method_names = sorted(set(re.findall(r"\b(?:fun|public|private|protected|static|\s)+\s*([a-z][A-Za-z0-9_]*)\s*\(", text)))
    packages = sorted(set(re.findall(r"^\s*package\s+([A-Za-z0-9_.]+)", text, re.MULTILINE)))
    imports = sorted(set(re.findall(r"^\s*import\s+([A-Za-z0-9_.*]+)", text, re.MULTILINE)))
    return {"packages": packages, "imports": imports, "classes": class_names, "methods": method_names}


def docs_facts(text: str) -> dict:
    headings = re.findall(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    code_blocks = re.findall(r"```([A-Za-z0-9_-]*)\n(.*?)```", text, re.DOTALL)
    return {
        "headings": [title.strip() for _, title in headings],
        "links": links,
        "code_blocks": [{"language": lang, "lines": len(body.splitlines())} for lang, body in code_blocks],
    }


def missing_items(reference_items: list[str], candidate_items: list[str]) -> list[str]:
    return sorted(set(reference_items) - set(candidate_items))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--task-family", required=True, choices=["python", "kotlin-java", "docs"])
    parser.add_argument("--scope", required=True)
    args = parser.parse_args()

    ref_path = Path(args.reference)
    cand_path = Path(args.candidate)
    ref_text = read_text(ref_path)
    cand_text = read_text(cand_path)

    result = {
        "reference": str(ref_path),
        "candidate": str(cand_path),
        "task_family": args.task_family,
        "scope": args.scope,
        "exists": {"reference": ref_path.exists(), "candidate": cand_path.exists()},
        "size": {
            "reference_lines": len(ref_text.splitlines()),
            "candidate_lines": len(cand_text.splitlines()),
        },
        "findings": [],
    }

    if args.task_family == "python":
        ref = python_symbols(ref_text)
        cand = python_symbols(cand_text)
        result["symbols"] = {"reference": ref, "candidate": cand}
        if "syntax_error" in cand:
            result["findings"].append({"severity": "high", "message": f"Candidate Python syntax error: {cand['syntax_error']}"})
        missing_funcs = missing_items(list(ref.get("functions", {}).keys()), list(cand.get("functions", {}).keys()))
        missing_classes = missing_items(list(ref.get("classes", {}).keys()), list(cand.get("classes", {}).keys()))
        if missing_funcs:
            result["findings"].append({"severity": "medium", "message": f"Candidate missing functions: {missing_funcs}"})
        if missing_classes:
            result["findings"].append({"severity": "medium", "message": f"Candidate missing classes: {missing_classes}"})
    elif args.task_family == "kotlin-java":
        ref = jvm_symbols(ref_text)
        cand = jvm_symbols(cand_text)
        result["symbols"] = {"reference": ref, "candidate": cand}
        missing_classes = missing_items(ref["classes"], cand["classes"])
        missing_methods = missing_items(ref["methods"], cand["methods"])
        if missing_classes:
            result["findings"].append({"severity": "medium", "message": f"Candidate missing JVM classes: {missing_classes}"})
        if missing_methods:
            result["findings"].append({"severity": "medium", "message": f"Candidate missing JVM methods: {missing_methods}"})
    else:
        ref = docs_facts(ref_text)
        cand = docs_facts(cand_text)
        result["docs"] = {"reference": ref, "candidate": cand}
        if not cand["headings"]:
            result["findings"].append({"severity": "medium", "message": "Candidate documentation has no Markdown headings."})
        broken_internal = [link for link in cand["links"] if link.startswith("#") and len(link) <= 1]
        if broken_internal:
            result["findings"].append({"severity": "low", "message": f"Suspicious internal links: {broken_internal}"})

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
