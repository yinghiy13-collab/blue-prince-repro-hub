#!/usr/bin/env python3
import argparse, hashlib, json, os, re, sys
from pathlib import Path

SCHEMA_VERSION = 1
REQUIRED_FILE_FIELDS = {"path", "sha256", "ast"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OUTPUT_PATH = None
REPORT = {}
ALLOW_LOCAL = False

def fail(msg, partial=None):
    print(f"::error::WITNESS FAIL: {msg}", file=sys.stderr)
    final = {"schema_version": SCHEMA_VERSION, "verdict": "FAIL", "reason": msg, **REPORT, **(partial or {})}
    if OUTPUT_PATH:
        try:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_PATH.write_text(json.dumps(final, indent=2, sort_keys=True))
        except Exception as e:
            print(f"report write error: {e}", file=sys.stderr)
    sys.exit(1)

def load_and_hash(path):
    if not path.is_file():
        fail(f"required file missing: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"invalid JSON in {path}: {e}")
    if not isinstance(data, dict):
        fail(f"root of {path} not an object")
    return data, digest

def safe_path(raw):
    if not isinstance(raw, str) or not raw.strip():
        fail(f"unsafe path: {raw!r}")
    p = Path(raw)
    if p.is_absolute() or ".." in p.parts:
        fail(f"unsafe path: {raw!r}")
    try:
        r = (Path.cwd() / p).resolve()
        r.relative_to(Path.cwd().resolve())
    except ValueError:
        fail(f"path escapes repo: {raw!r}")
    return r

def valid_sha(s, ctx):
    if not isinstance(s, str) or not SHA256_RE.fullmatch(s.lower()):
        fail(f"{ctx} invalid sha256: {s!r}")

def main():
    global OUTPUT_PATH, REPORT, ALLOW_LOCAL
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--verified", required=True)
    ap.add_argument("--provenance", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--allow-local", action="store_true")
    a = ap.parse_args()
    ALLOW_LOCAL = a.allow_local
    OUTPUT_PATH = Path(a.output)

    ev, ev_sha = load_and_hash(Path(a.evidence))
    vf, vf_sha = load_and_hash(Path(a.verified))
    pv, pv_sha = load_and_hash(Path(a.provenance))
    REPORT = {"evidence_sha256": ev_sha, "verified_sha256": vf_sha, "provenance_sha256": pv_sha, "allow_local": ALLOW_LOCAL}

    if ev.get("schema_version") != SCHEMA_VERSION:
        fail(f"bad evidence schema_version: {ev.get('schema_version')!r}")
    if vf.get("schema_version") != SCHEMA_VERSION:
        fail(f"bad verified schema_version: {vf.get('schema_version')!r}")

    claimed = vf.get("evidence_sha256")
    if not isinstance(claimed, str) or not claimed:
        fail("verified.json missing evidence_sha256")
    valid_sha(claimed, "verified.evidence_sha256")
    if claimed.lower() != ev_sha.lower():
        fail(f"evidence hash mismatch: claimed {claimed}, computed {ev_sha}")

    expected = {"commit": os.environ.get("GITHUB_SHA", ""), "run_id": os.environ.get("GITHUB_RUN_ID", ""), "repository": os.environ.get("GITHUB_REPOSITORY", "")}
    if not ALLOW_LOCAL:
        missing = [k for k, v in expected.items() if not v]
        if missing:
            fail(f"missing workflow env: {missing}")
    mismatches = {k: {"provenance": str(pv.get(k, "")), "expected": v} for k, v in expected.items() if v and str(pv.get(k, "")) != v}
    if mismatches:
        if ALLOW_LOCAL:
            print(f"::warning::LOCAL mismatch tolerated: {mismatches}", file=sys.stderr)
        else:
            fail(f"provenance does not match workflow env: {mismatches}")

    vp = vf.get("provenance")
    v_commit = vp.get("commit") if isinstance(vp, dict) else vf.get("commit")
    p_commit = pv.get("commit")
    if not v_commit:
        fail("verified.json missing commit")
    if not p_commit:
        fail("provenance.json missing commit")
    if v_commit != p_commit:
        fail(f"commit mismatch: verified={v_commit}, provenance={p_commit}")

    files = ev.get("files")
    if not isinstance(files, list) or not files:
        fail("evidence.files must be non-empty list")
    for i, item in enumerate(files):
        if not isinstance(item, dict):
            fail(f"files[{i}] not an object")
        miss = REQUIRED_FILE_FIELDS - item.keys()
        if miss:
            fail(f"files[{i}] missing {sorted(miss)}")
        if not isinstance(item.get("ast"), dict):
            fail(f"files[{i}].ast not an object")
        valid_sha(item.get("sha256", ""), f"files[{i}]")
        sp = safe_path(item["path"])
        if not sp.is_file():
            fail(f"files[{i}] missing source: {item['path']}")
        real = hashlib.sha256(sp.read_bytes()).hexdigest()
        if real.lower() != item["sha256"].lower():
            fail(f"files[{i}] sha256 mismatch {item['path']}")
    if vf.get("status") != "VERIFIED":
        fail(f"status != VERIFIED: {vf.get('status')!r}")

    out = {"schema_version": SCHEMA_VERSION, "verdict": "PASS", "evidence_sha256": ev_sha,
           "claimed_evidence_sha256": claimed, "evidence_hash_match": True,
           "verified_sha256": vf_sha, "provenance_sha256": pv_sha,
           "files_checked": len(files), "commit": p_commit,
           "commit_match": True, "provenance_mismatches": mismatches,
           "trust_boundary": "SAME_COMMIT", "mode": "LOCAL" if ALLOW_LOCAL else "CI"}
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"WITNESS PASS hash={ev_sha[:12]} files={len(files)}")
    sys.exit(0)

if __name__ == "__main__":
    main()
