# Historical Market Intelligence Engine (HMIE v1.0.0) 🏛️

> **An Oracle-backed historical market research terminal for Indian equity markets.**

---

## 🎯 Mission Statement
HMIE's mission is to transform historical Indian market data into reproducible, evidence-based research that is understandable to both experienced investors and newcomers. Every published insight must be traceable to verified historical data (`STAGING.STOCK_HIST_DATA`) and presented with clarity rather than complexity.

> **Operating Model**: HMIE v1.0.0 freezes the platform architecture—not the research. New historical studies, data updates, and evidence validation continue within the existing architecture. Every published research note independently passes all 5 CAR Quality Gates before entering the library.

---

## 📖 Table of Contents
1. [What HMIE Does](#-what-hmie-does)
2. [Current Status](#-current-status)
3. [Beginner's Step-by-Step Installation & Execution Guide](#-beginners-step-by-step-installation--execution-guide)
4. [CAR Quality Gates](#-car-quality-gates-canonical-acceptance-review)
5. [The Three-Layer Architecture](#-the-three-layer-architecture)
6. [Deliberately Excluded Features](#-deliberately-excluded-from-hmie-v1)
7. [Core Principles](#-core-principles)

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

## 🛠️ Beginner's Step-by-Step Installation & Execution Guide

If you are cloning this repository for the first time without any prior knowledge of HMIE, follow these exact 5 steps:

### Prerequisites
- **Python**: Version 3.10 or higher
- **Database**: Oracle XE 11g / 21c / 23c (or local Oracle instance)
- **Fyers Account** *(Optional for live EOD sync)*: Free Fyers Developer API App Client ID & Secret

---

### Step 1: Clone Repository & Setup Virtual Environment

```bash
# 1. Clone the repository from GitHub
git clone https://github.com/YOUR_USERNAME/HMIE.git
cd HMIE

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Set Up Oracle Database Schema

Ensure Oracle XE is running on your machine, then run the master DDL script to create all required tables (`STAGING.STOCK_HIST_DATA`, `SECTOR_MASTER`, `EVIDENCE_CORRECTIONS`, etc.):

```bash
# Connect to SQL*Plus as STAGING user and execute DDL script:
sqlplus staging/password@localhost:1521/XE @database_schema/master_schema.sql
```

---

### Step 3: Configure API Credentials (Optional for Live Ingestion)

Copy the template `fyers.env.example` to `fyers.env`:

```bash
# Copy template file
cp fyers.env.example fyers.env
```

Open `fyers.env` in any text editor and paste your Fyers App credentials:
```ini
FYERS_CLIENT_ID=YOUR_CLIENT_ID_HERE-100
FYERS_SECRET_KEY=YOUR_SECRET_KEY_HERE
FYERS_REDIRECT_URI=https://127.0.0.1/
```

---

### Step 4: Run Data Pipeline & Analytical Engines

Execute the sequential analytical engines to populate stock history, sector rotation, and precomputed historical event evidence:

```bash
# 1. Authenticate & Ingest 15-Year EOD Stock History into Oracle DB:
python data_pipeline/fetchers/fyers_login.py
python data_pipeline/ingestion/upload_stocks_to_db.py

# 2. Run Market Structure & Sector Rotation Engine:
python data_pipeline/stages/stage3_market_structure.py

# 3. Run Historical Evidence Engine (Drawdowns & Macro Event Windows):
python data_pipeline/stages/stage4_historical_evidence.py

# 4. Run Strategy & Plausibility Validation Suite:
python data_pipeline/stages/stage6_strategy_lab.py
python data_pipeline/stages/stage10_plausibility_engine.py

# 5. Run Automated CAR Quality Gate Test Suite:
python -m unittest discover -s tests -p "test_*.py"
```

---

### Step 5: Launch Research Terminal Web Portal

```bash
# Launch FastAPI REST backend & terminal server
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:  
👉 **[http://127.0.0.1:8000/library.html](http://127.0.0.1:8000/library.html)**

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

## 📜 Core Principles
1. **Historical Evidence Over Prediction**: All insights grounded in empirical Oracle database EOD data.
2. **Simplicity Over Unnecessary Complexity**: Simple, shallow code architectures; earn complexity through proven need.
3. **Plain-English Explanations**: Accessible to beginners without compromising institutional rigor.
4. **100% Reproducible Research**: Immutable quality gates (`CAR-1` to `CAR-5`) for every published note.
