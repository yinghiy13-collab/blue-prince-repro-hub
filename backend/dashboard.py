#!/usr/bin/env python3
import json, pathlib, datetime

def build_dashboard():
    ast_path = pathlib.Path("evidence/ast.json")
    witness_path = pathlib.Path("evidence/witness-report.json")
    registry_path = pathlib.Path("skills/registry.json")
    
    dashboard = {"version": "v2.1.0", "generated_at": datetime.datetime.utcnow().isoformat() + "Z", "sovereign": {}, "skills": {}, "memory": {}}
    
    if ast_path.exists():
        ast_data = json.loads(ast_path.read_text())
        # FIX 1: ใช้ len(files) แทน total_files
        dashboard["sovereign"]["files"] = len(ast_data.get("files", []))
        dashboard["sovereign"]["schema_version"] = ast_data.get("schema_version")
    
    if witness_path.exists():
        w = json.loads(witness_path.read_text())
        dashboard["sovereign"]["verdict"] = w.get("verdict")
        dashboard["sovereign"]["trust_boundary"] = w.get("trust_boundary")
        dashboard["sovereign"]["commit_match"] = w.get("commit_match")
        dashboard["sovereign"]["evidence_hash_match"] = w.get("evidence_hash_match")
        dashboard["sovereign"]["commit"] = w.get("commit", "")[:12]
    
    if registry_path.exists():
        reg = json.loads(registry_path.read_text())
        dashboard["skills"]["total"] = len(reg.get("skills", []))
        dashboard["skills"]["done"] = len([s for s in reg["skills"] if "DONE" in s.get("status","")])
        dashboard["skills"]["todo"] = len([s for s in reg["skills"] if "TODO" in s.get("status","")])
    
    pathlib.Path("memory/short_term").mkdir(parents=True, exist_ok=True)
    pathlib.Path("memory/short_term/dashboard.json").write_text(json.dumps(dashboard, indent=2))
    
    html = f"<html><head><title>Sovereign v2.1.0</title><style>body{{font-family:monospace;padding:20px}} .pass{{color:green}} .fail{{color:red}} .card{{border:1px solid #ccc;padding:10px;margin:10px 0}}</style></head><body><h1>Sovereign Baseline v2.1.0 REAL</h1><div class=\"card\"><h3>Witness: <span class=\"{'pass' if dashboard['sovereign'].get('verdict')=='PASS' else 'fail'}\">{dashboard['sovereign'].get('verdict')}</span></h3><p>Trust: {dashboard['sovereign'].get('trust_boundary')} | Commit: {dashboard['sovereign'].get('commit')} | Files: {dashboard['sovereign'].get('files')}</p></div><pre>{json.dumps(dashboard, indent=2)}</pre></body></html>"
    pathlib.Path("memory/short_term/dashboard.html").write_text(html)
    print(f"✅ Dashboard: verdict={dashboard['sovereign'].get('verdict')} files={dashboard['sovereign'].get('files')}")
    return dashboard

if __name__ == "__main__":
    build_dashboard()
