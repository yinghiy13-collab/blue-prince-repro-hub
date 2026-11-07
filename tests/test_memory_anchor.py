import unittest, subprocess, sys, json, hashlib
from pathlib import Path

class MemoryAnchorTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.anchor = self.root / "MEMORY_ANCHOR.lock"
        self.manifest = self.root / "evidence" / "anchor_manifest.json"

    def test_anchor_and_manifest_exist(self):
        self.assertTrue(self.anchor.is_file())
        self.assertTrue(self.manifest.is_file())

    def test_anchor_digest_matches_manifest(self):
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual(hashlib.sha256(self.anchor.read_bytes()).hexdigest(), manifest.get("anchor_sha256"))

    def test_validator_accepts_matching_anchor(self):
        result = subprocess.run([sys.executable, "src/memory_anchor_validator.py"], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 0)

if __name__ == "__main__": unittest.main()