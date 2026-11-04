
import json, pathlib, hashlib, sys
print("=== INDEPENDENT VERIFIER ===")
b=json.loads(pathlib.Path("evidence/ast.json").read_text())
fresh={}
for f in pathlib.Path("src").rglob("*.py"):
    fresh[str(f)]=hashlib.sha256(f.read_text(errors="ignore").encode()).hexdigest()
mismatch=[]
for e in b["files"]:
    p=e["path"]
    if p in fresh and fresh[p]!=e["sha256"]:
        mismatch.append(p)
if mismatch:
    print("DENY", mismatch)
    sys.exit(1)
# Zero Mock Policy
for wf in pathlib.Path(".github/workflows").rglob("*.yml"):
    txt=wf.read_text()
    if "echo '{\" + '"ast' in txt:
        print(f"DENY Mock in {wf}")
        sys.exit(1)
    if 'echo '{"ast"' in txt:
        print(f"DENY Mock in {wf}")
        sys.exit(1)
print(f"PASS {len(fresh)} files, Zero Mock PASS")
pathlib.Path("evidence/verified.json").write_text(json.dumps({"verifier":"independent","status":"PASS","files":len(fresh)},sort_keys=True,indent=2))
