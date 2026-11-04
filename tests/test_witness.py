import hashlib, json, subprocess, sys, os
from pathlib import Path

VERIFIER = Path(__file__).resolve().parents[1] / "tools" / "independent_verifier.py"

def write_json(path, data):
    text = json.dumps(data, sort_keys=True)
    path.write_text(text)
    return path.read_bytes()

def run_witness(tmp_path, monkeypatch, evidence, verified, provenance, allow_local=True, env=None):
    monkeypatch.chdir(tmp_path)
    e, v, p, o = tmp_path/"ast.json", tmp_path/"verified.json", tmp_path/"provenance.json", tmp_path/"witness-report.json"
    eb = write_json(e, evidence)
    if verified.get("evidence_sha256") == "PLACEHOLDER":
        verified["evidence_sha256"] = hashlib.sha256(eb).hexdigest()
    write_json(v, verified)
    write_json(p, provenance)
    cmd = [sys.executable, str(VERIFIER), "--evidence", str(e), "--verified", str(v), "--provenance", str(p), "--output", str(o)]
    if allow_local:
        cmd.append("--allow-local")
    run_env = os.environ.copy()
    if env is not None:
        run_env.update(env)
    r = subprocess.run(cmd, capture_output=True, text=True, env=run_env)
    report = json.loads(o.read_text()) if o.exists() else {}
    return r, report

def base_evidence(tmp_path, content=b"print('hi')\n", source="src/example.py"):
    f = tmp_path / source
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(content)
    return {"schema_version": 1, "files": [{"path": source, "sha256": hashlib.sha256(content).hexdigest(), "ast": {"type": "Module"}}]}

def base_verified(commit, sha="PLACEHOLDER"):
    return {"schema_version": 1, "status": "VERIFIED", "evidence_sha256": sha, "commit": commit}

def base_provenance(commit):
    return {"commit": commit, "run_id": "123", "repository": "org/repo"}

def test_local_mode_pass(tmp_path, monkeypatch):
    c = "a" * 40
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified(c), base_provenance(c))
    assert r.returncode == 0, r.stderr
    assert rep["verdict"] == "PASS"
    assert rep["evidence_hash_match"] is True
    assert rep["commit_match"] is True

def test_hash_mismatch_fails(tmp_path, monkeypatch):
    c = "a" * 40
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified(c, "0"*64), base_provenance(c))
    assert r.returncode == 1
    assert rep["verdict"] == "FAIL"
    assert "hash mismatch" in rep["reason"]

def test_commit_mismatch_fails(tmp_path, monkeypatch):
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified("a"*40), base_provenance("b"*40))
    assert r.returncode == 1
    assert "commit mismatch" in rep["reason"]

def test_path_traversal_fails(tmp_path, monkeypatch):
    c = "a" * 40
    ev = {"schema_version": 1, "files": [{"path": "../../etc/passwd", "sha256": "a"*64, "ast": {}}]}
    r, rep = run_witness(tmp_path, monkeypatch, ev, base_verified(c), base_provenance(c))
    assert r.returncode == 1
    assert "unsafe path" in rep["reason"]

def test_missing_source_fails(tmp_path, monkeypatch):
    c = "a" * 40
    ev = {"schema_version": 1, "files": [{"path": "src/does-not-exist.py", "sha256": "a"*64, "ast": {}}]}
    r, rep = run_witness(tmp_path, monkeypatch, ev, base_verified(c), base_provenance(c))
    assert r.returncode == 1
    assert "missing source" in rep["reason"]

def test_provenance_mismatch_recorded_in_local_mode(tmp_path, monkeypatch):
    c = "a" * 40
    pv = base_provenance(c)
    pv["repository"] = "other/repo"
    env = {"GITHUB_SHA": c, "GITHUB_RUN_ID": "123", "GITHUB_REPOSITORY": "org/repo"}
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified(c), pv, allow_local=True, env=env)
    assert r.returncode == 0
    assert rep["provenance_mismatches"]["repository"]["provenance"] == "other/repo"

def test_provenance_mismatch_fails_in_ci_mode(tmp_path, monkeypatch):
    c = "a" * 40
    pv = base_provenance(c)
    pv["repository"] = "other/repo"
    env = {"GITHUB_SHA": c, "GITHUB_RUN_ID": "123", "GITHUB_REPOSITORY": "org/repo"}
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified(c), pv, allow_local=False, env=env)
    assert r.returncode == 1
    assert "provenance does not match workflow env" in rep["reason"]

def test_ci_mode_pass(tmp_path, monkeypatch):
    c = "a" * 40
    env = {"GITHUB_SHA": c, "GITHUB_RUN_ID": "123", "GITHUB_REPOSITORY": "org/repo"}
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), base_verified(c), base_provenance(c), allow_local=False, env=env)
    assert r.returncode == 0, r.stderr
    assert rep["mode"] == "CI"

def test_missing_evidence_sha256_fails(tmp_path, monkeypatch):
    c = "a" * 40
    v = base_verified(c)
    v.pop("evidence_sha256")
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), v, base_provenance(c))
    assert r.returncode == 1
    assert "missing evidence_sha256" in rep["reason"]

def test_unverified_status_fails(tmp_path, monkeypatch):
    c = "a" * 40
    v = base_verified(c)
    v["status"] = "PENDING"
    r, rep = run_witness(tmp_path, monkeypatch, base_evidence(tmp_path), v, base_provenance(c))
    assert r.returncode == 1
    assert "VERIFIED" in rep["reason"]
