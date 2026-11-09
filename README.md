# BPRH / SEOS v3.0 — Sovereign Meta-Kernel

Executable AI Governance Platform enforcing "No Evidence → No Claim → No Trust → No Release".

## 🚀 Quick Start
1. `docker compose up -d --build`
2. `make ci-local` (Run verification & tests)
3. Open Dashboard at `http://localhost`

## 🏗️ Architecture
- **L0:** eBPF Tracer (Syscall monitoring)
- **L1:** TLA+ Formal Verification & Miron IR (CFG)
- **L2:** OPA Policy & FastAPI Backend
- **L3:** React Auditor Dashboard

*Human is the Final Authority.*
