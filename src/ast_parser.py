
import ast, json, pathlib, hashlib
src_root = pathlib.Path("src")
out={"version":"v2.1.0-real","files":[]}
for f in src_root.rglob("*.py"):
    code=f.read_text(errors="ignore")
    tree=ast.parse(code)
    funcs=[n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    out["files"].append({"path":str(f),"sha256":hashlib.sha256(code.encode()).hexdigest(),"functions":funcs,"loc":len(code.splitlines())})
out["total_files"]=len(out["files"])
pathlib.Path("evidence/ast.json").write_text(json.dumps(out,sort_keys=True,indent=2))
print(f"AST OK {len(out['files'])} files")
