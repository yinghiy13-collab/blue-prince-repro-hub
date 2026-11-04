#!/usr/bin/env python3
import json, pathlib

def check_status():
    report = {"checks": [], "overall": "PASS"}
    ast_path = pathlib.Path("evidence/ast.json")
    if ast_path.exists():
        data = json.loads(ast_path.read_text())
        ok = data.get("schema_version")==1 and len(data.get("files",[])) > 0
        report["checks"].append({"name":"ast_parser","status":"PASS" if ok else "FAIL","files":len(data.get("files",[]))})
    else:
        report["checks"].append({"name":"ast_parser","status":"FAIL"})
    
    w_path = pathlib.Path("evidence/witness-report.json")
    if w_path.exists():
        w = json.loads(w_path.read_text())
        ok = w.get("verdict")=="PASS" and w.get("commit_match") and w.get("evidence_hash_match")
        report["checks"].append({"name":"witness_v14","status":"PASS" if ok else "FAIL","verdict":w.get("verdict")})
    else:
        report["checks"].append({"name":"witness_v14","status":"FAIL"})
    
    reg_path = pathlib.Path("skills/registry.json")
    if reg_path.exists():
        reg = json.loads(reg_path.read_text())
        ids = [s["id"] for s in reg["skills"]]
        dup = len(ids) != len(set(ids))
        report["checks"].append({"name":"skill_registry","status":"FAIL" if dup else "PASS","total":len(ids),"duplicates":dup})
    
    report["overall"] = "PASS" if all(c["status"]=="PASS" for c in report["checks"]) else "FAIL"
    pathlib.Path("memory/episodic").mkdir(parents=True, exist_ok=True)
    pathlib.Path("memory/episodic/monitor.json").write_text(json.dumps(report, indent=2))
    print(f"Monitor: {report['overall']} - {len(report['checks'])} checks")
    for c in report["checks"]:
        print(f"  {'✅' if c['status']=='PASS' else '❌'} {c['name']}: {c['status']}")
    return report

if __name__ == "__main__":
    check_status()
