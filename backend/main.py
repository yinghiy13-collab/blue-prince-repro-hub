from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json, pathlib

app = FastAPI(title="Sovereign Baseline API - V12")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/monitor")
def monitor():
    p = pathlib.Path("dist/witness-report.json")
    if not p.exists():
        return {"verdict":"BLOCK","reason":"MISSING","commit_match":False,"evidence_hash_match":False}
    try:
        return json.loads(p.read_text())
    except:
        return {"verdict":"BLOCK","reason":"CORRUPTED"}

@app.get("/api/ledger")
def ledger():
    p = pathlib.Path("memory/long_term/ledger.json")
    return json.loads(p.read_text()) if p.exists() else []

@app.get("/api/health")
def health():
    return {"status":"ok","phase":"V12","clusters":3,"quorum":"2/3","trust_boundary":"EXTERNAL_PINNED_WORKFLOW"}
