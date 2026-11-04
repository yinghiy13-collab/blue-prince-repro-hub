import json, pathlib, sys, subprocess, os
def get_runs(limit=20):
    env = os.environ.copy()
    env["GH_TOKEN"] = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN") or ""
    try:
        r = subprocess.run(["gh","run","list","--limit",str(limit),"--json","databaseId,status,conclusion,displayTitle"], capture_output=True, text=True, check=True, env=env)
        return json.loads(r.stdout)
    except Exception as e:
        print(f"⚠️ gh not available: {e}")
        return []

if __name__ == "__main__":
    print("=== GitHub Actions Runs ===")
    for run in get_runs(20):
        print(f"{run.get('databaseId')} {run.get('status')} {run.get('conclusion')} {run.get('displayTitle')}")
    witness_path = pathlib.Path("dist/witness-report.json")
    if not witness_path.exists():
        print("🚫 MONITOR BLOCK - MISSING"); sys.exit(1)
    try:
        w = json.loads(witness_path.read_text())
    except:
        print("🚫 MONITOR BLOCK - CORRUPTED"); sys.exit(1)
    if w.get("verdict") != "PASS" or not w.get("commit_match") or not w.get("evidence_hash_match"):
        print(f"🚫 BLOCK {w}"); sys.exit(1)
    print(f"✅ MONITOR PASS - {w.get('trust_boundary')} files={w.get('files_checked')}")
