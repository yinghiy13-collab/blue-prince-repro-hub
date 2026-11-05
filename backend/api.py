#!/usr/bin/env python3
"""Sovereign Baseline API - read-only, fail-closed, no secrets"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json, pathlib

app = FastAPI(title="Sovereign Baseline API", version="2.1.0")

def load_json(path, default=None):
    p = pathlib.Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text())

@app.get("/api/monitor")
def monitor():
    data = load_json("memory/episodic/monitor.json", {"overall": "UNKNOWN", "checks": []})
    return {"status": "read-only", "data": data}

@app.get("/api/witness")
def witness():
    w = load_json("evidence/witness-report.json", {})
    safe = {k: w.get(k) for k in ["verdict","trust_boundary","commit_match",
                                    "evidence_hash_match","files_checked","mode"]}
    return {"status": "read-only", "data": safe}

@app.get("/api/dashboard")
def dashboard():
    d = load_json("memory/short_term/dashboard.json", {})
    return {"status": "read-only", "data": d}

app.mount("/dashboard", StaticFiles(directory="docs", html=True), name="dashboard")

@app.get("/")
def root():
    return FileResponse("docs/index.html")
