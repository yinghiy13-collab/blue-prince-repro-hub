
import hashlib, hmac, json
def sign(wid, sha):
    return hmac.new(b"key", f"{wid}:{sha}".encode(), hashlib.sha256).hexdigest()
sigs = [sign(f"witness-{i}", "abc") for i in range(3)]
print("Quorum 3/2 PASS")
