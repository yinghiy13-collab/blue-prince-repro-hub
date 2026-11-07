#!/usr/bin/env python3
"""Fail-closed validator for the governance memory anchor."""
from pathlib import Path
import hashlib, json, sys

ANCHOR_PATH = Path("MEMORY_ANCHOR.lock")
MANIFEST_PATH = Path("evidence/anchor_manifest.json")

def fail(message: str) -> None:
    print(f"FAIL-CLOSED: {message}")
    raise SystemExit(1)

def main() -> int:
    if not ANCHOR_PATH.is_file(): fail("MEMORY_ANCHOR.lock is missing")
    if not MANIFEST_PATH.is_file(): fail("evidence/anchor_manifest.json is missing")
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: fail(f"anchor manifest is unreadable: {error}")
    
    expected_digest = manifest.get("anchor_sha256")
    if not isinstance(expected_digest, str) or len(expected_digest) != 64: fail("invalid SHA-256 digest")
    
    actual_digest = hashlib.sha256(ANCHOR_PATH.read_bytes()).hexdigest()
    if actual_digest != expected_digest: fail("digest does not match manifest")
    
    print(f"PASS: anchor digest verified: {actual_digest}")
    return 0

if __name__ == "__main__": raise SystemExit(main())