#!/usr/bin/env python3
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "MEMORY_ANCHOR.lock"

def fail(msg: str) -> int:
    print(f"ANCHOR_DENY: {msg}", file=sys.stderr)
    return 1

def main() -> int:
    if not LOCK_PATH.exists():
        return fail("MEMORY_ANCHOR.lock missing")

    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return fail(f"lock JSON invalid: {e}")

    for k in ["anchorVersion", "specFile", "specVersion", "specDigest", "createdBy", "status"]:
        if k not in lock or not lock[k]:
            return fail(f"lock missing field: {k}")

    if lock.get("anchorVersion") != "BPRH-ANCHOR-v1":
        return fail(f"unsupported anchorVersion: {lock.get('anchorVersion')}")
    if lock.get("status") != "LOCKED":
        return fail(f"anchor status != LOCKED: {lock.get('status')}")
    if str(lock.get("createdBy","")).upper().startswith(("BOT", "AI", "GITHUB-ACTIONS")):
        return fail(f"anchor must be Human-only, got createdBy={lock.get('createdBy')}")

    digest = str(lock.get("specDigest",""))
    if not digest.startswith("sha256:") or len(digest) != 7 + 64:
        return fail(f"bad specDigest format: {digest}")

    spec_path = ROOT / str(lock["specFile"])
    if not spec_path.exists():
        return fail(f"spec file missing: {spec_path}")

    actual = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    expected = digest.split(":", 1)[1]
    if actual != expected:
        return fail(f"spec digest mismatch: expected={expected} actual={actual}")

    print(f"ANCHOR_VERIFIED: {lock['specFile']} {digest}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
