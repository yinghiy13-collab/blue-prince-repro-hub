import unittest
import subprocess
import os
import shutil
import tempfile
import json
import hashlib

class TestMemoryAnchorFailClosed(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "src"))
        
        # ดึง Validator จาก Repo หลักมาทดสอบ
        shutil.copy("src/memory_anchor_validator.py", os.path.join(self.test_dir, "src"))
        
        self.spec_path = os.path.join(self.test_dir, "SPEC.md")
        with open(self.spec_path, "w") as f:
            f.write("BPRH Architecture v1.0")
            
        spec_hash = hashlib.sha256(b"BPRH Architecture v1.0").hexdigest()
        self.lock_data = {
            "anchorVersion": "BPRH-ANCHOR-v1",
            "specFile": "SPEC.md",
            "specDigest": f"sha256:{spec_hash}",
            "createdBy": "HUMAN_ARCHITECT",
            "status": "LOCKED"
        }
        self.lock_path = os.path.join(self.test_dir, "MEMORY_ANCHOR.lock")
        with open(self.lock_path, "w") as f:
            json.dump(self.lock_data, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def run_validator(self):
        result = subprocess.run(
            ["python", "src/memory_anchor_validator.py"],
            cwd=self.test_dir, capture_output=True, text=True
        )
        return result.returncode

    def test_MA_001_missing_lock(self):
        os.remove(self.lock_path)
        self.assertEqual(self.run_validator(), 1)

    def test_MA_002_tampered_spec(self):
        with open(self.spec_path, "w") as f: f.write("HACKED")
        self.assertEqual(self.run_validator(), 1)

    def test_MA_003_status_changed(self):
        self.lock_data["status"] = "UNLOCKED"
        with open(self.lock_path, "w") as f: json.dump(self.lock_data, f)
        self.assertEqual(self.run_validator(), 1)

    def test_MA_004_ai_created(self):
        self.lock_data["createdBy"] = "AI_BOT"
        with open(self.lock_path, "w") as f: json.dump(self.lock_data, f)
        self.assertEqual(self.run_validator(), 1)

    def test_MA_006_invalid_digest_format(self):
        self.lock_data["specDigest"] = "md5:123456"
        with open(self.lock_path, "w") as f: json.dump(self.lock_data, f)
        self.assertEqual(self.run_validator(), 1)

    def test_MA_007_valid_anchor(self):
        self.assertEqual(self.run_validator(), 0)

if __name__ == '__main__':
    unittest.main()
