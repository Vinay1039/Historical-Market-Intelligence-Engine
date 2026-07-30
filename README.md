# Historical Market Intelligence Engine (HMIE v3.0) 🏛️📊

> **A Governed Evidence-First AI Quantitative Research Platform for Indian Equity Markets**

HMIE combines 15 years of daily NSE market price data ($2011–2026$), automated strategy and event analytical engines, cryptographic execution governance, a 24-study canonical knowledge base, and an explainable AI evidence engine with an interactive web dashboard.

---

## Key Features

- 🏛️ **Oracle Data Warehouse**: 856 symbols, 180 months of price history stored in Oracle 11g/23c XE (`STAGING.STOCK_HIST_DATA`).
- 🛡️ **Research Governance Layer**: Single Canonical Execution Policy, SHA-256 Dual-Hashing (`EXECUTION_HASH` + `RESULT_HASH`), and Git Commit Tagging (`v3.0.0`).
- 📚 **24 Governed Canonical Executions**: Covering 6 Research Domains:
  1. **Momentum Research Suite** (Studies 001–004)
  2. **Festival Research Suite** (Studies F001–F004)
  3. **Union Budget Research Suite** (Studies B001–B004)
  4. **RBI Monetary Policy Suite** (Studies R001–R004)
  5. **General Lok Sabha Elections Suite** (Studies E001–E004)
  6. **Meta-Research Suite** (Studies M001–M003)
- 👤 **Plain English Intent AI Engine**: Classifies intent (`COUNT`, `LIST`, `STATISTICS`, `COMPARISON`, `PATTERN`) and returns human-friendly responses with Dual Indicators (`Evidence Quality` + `Sample Size`).
- 🎨 **Interactive Web Dashboard**: Accessible directly at `http://127.0.0.1:8000/`.

---

## Quick Start

### 1. Launch Platform Server
Double-click `start_hmie.bat` or run:
```powershell
c:\Users\vinay\.gemini\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### 2. Open Web Dashboard
Navigate your browser to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

### 3. Run Automated Evaluation Test
```powershell
c:\Users\vinay\.gemini\.venv\Scripts\python.exe tests/eval_harness.py
```

---

## System Architecture

```
                    User
                      │
                      ▼
       HMIE 3.0 Evidence Dashboard UI (http://127.0.0.1:8000/)
                      │
                      ▼
         FastAPI REST Backend (/api/v1/research/query)
                      │
                      ▼
         HMIE 3.0 Intent AI Evidence Engine
                      │
                      ▼
        Oracle Research Governance Store (STAGING.RESEARCH_EXECUTIONS)
```

---

## License & Provenance
Registered under Git Commit `v3.0.0` • Dataset Version `v2.0.0`.
