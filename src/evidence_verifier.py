#!/usr/bin/env python3
import argparse, hashlib, json, os
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", default="evidence/ast.json")
    ap.add_argument("--out", default="evidence/verified.json")
    args = ap.parse_args()

    evidence_path = Path(args.evidence)
    if not evidence_path.is_file():
        raise SystemExit(f"evidence file missing: {evidence_path}")

    evidence = json.loads(evidence_path.read_text())
    if evidence.get("schema_version") != 1:
        raise SystemExit(f"unsupported evidence schema_version: {evidence.get('schema_version')!r}")

    verified = {
        "schema_version": 1,
        "status": "VERIFIED",
        "evidence_sha256": sha256_file(evidence_path),
        "commit": os.environ.get("GITHUB_SHA", ""),
        "evidence_path": str(evidence_path),
        "timestamp": "2026-01-01T00:00:00Z",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(verified, indent=2, sort_keys=True))
    print(f"Wrote {out_path} (evidence_sha256={verified['evidence_sha256'][:12]}..)")

if __name__ == "__main__":
    main()
