# Historical Market Intelligence Engine (HMIE v1.0.0) 🏛️

> **An Oracle-backed historical market research terminal for Indian equity markets.**

---

## 🎯 Mission Statement
HMIE's mission is to transform historical Indian market data into reproducible, evidence-based research that is understandable to both experienced investors and newcomers. Every published insight must be traceable to verified historical data (`STAGING.STOCK_HIST_DATA`) and presented with clarity rather than complexity.

> **Operating Model**: HMIE v1.0.0 freezes the platform architecture—not the research. New historical studies, data updates, and evidence validation continue within the existing architecture. Every published research note independently passes all 5 CAR Quality Gates before entering the library.

---

## 📚 What HMIE Does
- **Produces Reproducible Research**: All studies adhere to 100% reproducible Oracle database EOD replay.
- **Publishes Canonical Research Notes (CRN)**: Single-domain historical baselines (RBI Policy, Diwali, Budget, Market Corrections, Independence Day).
- **Publishes Integrated Research Studies (IRS)**: Multi-domain cross-evidence synthesis (e.g. Union Budget during Market Correction).
- **Enforces Non-Predictive Research**: Focuses strictly on historical evidence and observation (no black-box predictions).

---

## 🚀 Current Status
- ✅ **Version 1.0.0** — Feature Complete | Architecture Frozen | Research Library Continuously Growing
- ✅ **Specification**: CRN v1.1 Refined & IRS v1.0 Standard
- ✅ **Quality Audits**: CAR-1 through CAR-5 Verified
- ✅ **Dataset Baseline**: Oracle XE EOD Replay (`v2.0.1`)

---

## 🛡️ CAR Quality Gates (Canonical Acceptance Review)
Every published research note independently passes 5 mandatory quality gates before entering the library:
- **`CAR-1` Source Consistency**: Verified against authoritative `STAGING.STOCK_HIST_DATA` & `STAGING.SECTOR_MASTER`.
- **`CAR-2` Math Reproducibility**: 100% accurate percentage, mean, and win rate calculations.
- **`CAR-3` Aggregate Reconciliation**: Discrepancies between macro aggregates and stock-level details reconciled.
- **`CAR-4` Method Transparency**: Quantitative methodology parameters locked and published before analysis.
- **`CAR-5` Plain-English Validation**: Complex financial terms accompanied by 1-line plain-English takeaways.

---

## 🏛️ The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ LAYER 3: USER EXPERIENCE & VISUAL STORYTELLING                            │
│    • Research Library Terminal (library.html) • High-density CRN/IRS cards   │
│    • Visual "Answer First" Cards • Contextual "Why should I care?" callouts  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┴──────────────────────────────────────┐
│ 🔬 LAYER 2: INSTITUTIONAL RESEARCH ENGINE & GOVERNANCE                      │
│    • Canonical Research Notes (CRN v1.1) • Integrated Research Studies (IRS) │
│    • CAR-1 to CAR-5 Acceptance Reviews    • Combinatorial Guardrail Rule     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┴──────────────────────────────────────┐
│ 🗄️ LAYER 1: DATA FOUNDATION & REPLAY ENGINE                                 │
│    • Oracle XE Database Pool • Precomputed Event Tables • EOD Replay Pipeline│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚫 Deliberately Excluded from HMIE v1
To protect the platform from feature creep and unearned architectural bloat:
- ❌ No RAG, Vector Search, or Embedding Engines
- ❌ No Microservices or Graph Databases
- ❌ No Real-Time Streaming or Day-Trading Execution APIs
- ❌ No Autonomous LLM Research Generators or Unverified Predictive AI

---

## ⚡ Quick Start

### 1. Launch Platform Server
Double-click `start_hmie.bat` or run:
```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### 2. Open Research Library Terminal
Navigate your browser to: **[http://127.0.0.1:8000/library.html](http://127.0.0.1:8000/library.html)**

---

## 📜 Core Principles
1. **Historical Evidence Over Prediction**: All insights grounded in empirical Oracle database EOD data.
2. **Simplicity Over Unnecessary Complexity**: Simple, shallow code architectures; earn complexity through proven need.
3. **Plain-English Explanations**: Accessible to beginners without compromising institutional rigor.
4. **100% Reproducible Research**: Immutable quality gates (`CAR-1` to `CAR-5`) for every published note.
