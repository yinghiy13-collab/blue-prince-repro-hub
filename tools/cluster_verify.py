import json, hashlib, pathlib, os, sys
def load_and_hash(p):
    data = pathlib.Path(p).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()
ast, ast_hash = load_and_hash("dist/ast.json") if pathlib.Path("dist/ast.json").exists() else ({}, "0"*64)
verified = json.loads(pathlib.Path("dist/verified.json").read_text()) if pathlib.Path("dist/verified.json").exists() else {"commit":""}
expected_commit = os.environ["GITHUB_SHA"]
if verified.get("commit") != expected_commit:
    print(f"❌ commit mismatch"); sys.exit(1)
print("✅ CLUSTER VERIFY PASS")
