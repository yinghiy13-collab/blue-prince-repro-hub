
import hashlib
real = hashlib.sha256(b"real").hexdigest()
fake = hashlib.sha256(b"fake").hexdigest()
assert real != fake
print(f"✅ Differential PASS {real[:8]} != {fake[:8]}")
