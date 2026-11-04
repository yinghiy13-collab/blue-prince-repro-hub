#!/usr/bin/env python3
import json, pathlib

def advisory():
    w_path = pathlib.Path("evidence/witness-report.json")
    advice = {"advisory": [], "block_release": False, "mode": "advisory-only"}
    if not w_path.exists():
        advice["advisory"].append("witness-report.json missing - run witness first")
        pathlib.Path("memory/short_term/advisory.md").write_text("# Advisory\nMissing witness report\n")
        return advice
    w = json.loads(w_path.read_text())
    if w.get("verdict") != "PASS":
        advice["advisory"].append(f"Witness verdict {w.get('verdict')}: {w.get('reason')}")
    else:
        advice["advisory"].append("Witness PASS - no action needed")
    advice["block_release"] = False
    md = f"# Ollama Advisory (Phase 2)\n\nVerdict: {w.get('verdict')}\n\n" + "\n".join([f"- {a}" for a in advice["advisory"]]) + "\n\n> Advisory only - does not block release\n"
    pathlib.Path("memory/short_term/advisory.md").write_text(md)
    print(f"Advisory: {len(advice['advisory'])} items, block_release={advice['block_release']}")
    for a in advice["advisory"]:
        print(f"  - {a}")
    return advice

if __name__ == "__main__":
    advisory()
