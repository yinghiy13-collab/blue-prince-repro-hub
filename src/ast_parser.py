#!/usr/bin/env python3
"""Minimal deterministic AST diagnostic."""
from pathlib import Path
import ast, json, sys

SOURCE_PATH = Path("src/memory_anchor_validator.py")
OUTPUT_PATH = Path("evidence/ast.json")

def main() -> int:
    if not SOURCE_PATH.is_file(): 
        print(f"FAIL-CLOSED: missing {SOURCE_PATH}"); return 1
    try:
        tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    except SyntaxError as error:
        print(f"FAIL-CLOSED: syntax error: {error}"); return 1

    result = {
        "source": str(SOURCE_PATH), "language": "python", "parser": "python-ast",
        "functions": [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)],
        "policy_context": {"requested_capability": "READ_SOURCE", "simulation_only": True}
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: AST diagnostic generated {OUTPUT_PATH}")
    return 0

if __name__ == "__main__": raise SystemExit(main())