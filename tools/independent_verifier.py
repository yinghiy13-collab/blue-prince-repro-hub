
import json, pathlib, hashlib, sys
b=json.loads(pathlib.Path("evidence/ast.json").read_text())
fresh={str(f):hashlib.sha256(f.read_text(errors="ignore").encode()).hexdigest() for f in pathlib.Path("src").rglob("*.py")}
for e in b["files"]:
    if e["path"] in fresh and fresh[e["path"]]!=e["sha256"]:
        print("DENY MISMATCH", e["path"]); sys.exit(1)
for p in pathlib.Path(".github/workflows").rglob("*.yml"):
    if "echo '{\"ast\"" in p.read_text() or 'echo '{"ast"' in p.read_text():
        print(f"DENY Mock in {p}"); sys.exit(1)
print(f"PASS {len(fresh)} files Zero Mock PASS")
pathlib.Path("evidence/verified.json").write_text(json.dumps({"verifier":"independent","status":"PASS","files":len(fresh)},sort_keys=True,indent=2))
