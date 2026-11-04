#!/usr/bin/env python3
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    raw = Path(a.witness).read_bytes()
    w = json.loads(raw)
    out = Path(a.output)
    prev = "GENESIS"
    if out.exists():
        lines = out.read_text().splitlines()
        if lines:
            prev = json.loads(lines[-1])["entry_sha256"]
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(),
             "prev_entry_sha256": prev,
             "witness_sha256": hashlib.sha256(raw).hexdigest(),
             "verdict": w.get("verdict", "UNKNOWN"),
             "evidence_hash_match": w.get("evidence_hash_match", False),
             "commit_match": w.get("commit_match", False)}
    entry["entry_sha256"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"ledger appended, prev={prev[:12]} entry={entry['entry_sha256'][:12]}")

if __name__ == "__main__":
    main()
