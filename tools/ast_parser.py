import json, pathlib, sys
src = pathlib.Path(".")
out = pathlib.Path("dist/ast.json")
if "--src" in sys.argv:
    src = pathlib.Path(sys.argv[sys.argv.index("--src")+1])
if "--out" in sys.argv:
    out = pathlib.Path(sys.argv[sys.argv.index("--out")+1])
files = [str(p) for p in src.rglob("*.py") if "__pycache__" not in str(p)][:30]
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"files": files, "count": len(files)}, indent=2))
print(f"AST OK {len(files)} files {out.stat().st_size} bytes")
