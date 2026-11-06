#!/usr/bin/env python3
import ast, json, hashlib, pathlib, sys

src_root = pathlib.Path("src")
evidence_dir = pathlib.Path("evidence")
evidence_dir.mkdir(exist_ok=True)

out = {"version": "v2.1.0-fail-closed", "schema_version": 1, "files": []}

for py_file in sorted(src_root.rglob("*.py")):
    if "__pycache__" in str(py_file):
        continue
        
    code_text = py_file.read_text(encoding="utf-8", errors="ignore")
    
    try:
        tree = ast.parse(code_text, filename=str(py_file))
        funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    except SyntaxError as e:
        print(f"FATAL: AST Parsing failed for {py_file}")
        print(f"Reason: {e}")
        sys.exit(1)  # ทำให้ GitHub Actions แดงทันที

    sha = hashlib.sha256(code_text.encode("utf-8")).hexdigest()
    out["files"].append({
        "path": str(py_file),
        "sha256": sha,
        "ast": {"type": "Module", "functions": funcs, "classes": classes, "parse_ok": True},
        "loc": len(code_text.splitlines()),
        "size": len(code_text)
    })

out["total_files"] = len(out["files"])
out["total_loc"] = sum(f["loc"] for f in out["files"])

path = evidence_dir / "ast.json"
path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

print(f"✅ AST OK: {out['total_files']} files parsed successfully.")
sys.exit(0)
