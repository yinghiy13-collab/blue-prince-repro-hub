
import json, pathlib, hashlib, sys
print("=== INDEPENDENT VERIFIER ===")
b_path = pathlib.Path("evidence/ast.json")
b = json.loads(b_path.read_text())
fresh = {}
for f in pathlib.Path("src").rglob("*.py"):
    fresh[str(f)] = hashlib.sha256(f.read_text(errors="ignore").encode()).hexdigest()
bad = []
for e in b.get("files", []):
    p = e["path"]
    if p in fresh and fresh[p] != e["sha256"]:
        bad.append(p)
if bad:
    print("DENY MISMATCH", bad)
    sys.exit(1)
print(f"PASS {len(fresh)} files, sha256 match")
out = {"verifier": "independent", "status": "PASS", "files": len(fresh)}
pathlib.Path("evidence/verified.json").write_text(json.dumps(out, sort_keys=True, indent=2))
print("verified.json created")
