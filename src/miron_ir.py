
from dataclasses import dataclass
from typing import List
import json, hmac, hashlib
@dataclass
class MironModule:
    file: str
    sha256: str
    functions: List[str]
    def to_json(self):
        return json.dumps({"file": self.file, "sha256": self.sha256}, sort_keys=True, separators=(',',':'))
    def evidence(self):
        return hmac.new(b"seos-core", self.to_json().encode(), hashlib.sha256).hexdigest()
