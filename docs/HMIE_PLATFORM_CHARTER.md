# HMIE Platform Charter (v3.2)

## 0. Mission & Purpose
The Historical Market Intelligence Engine (HMIE) exists to help investors and researchers explore historical Indian market behavior using reproducible, evidence-backed analytics presented in plain English.

HMIE is a personal decision-support system for historical context. It is designed for long-term use (5–10 years) with zero unnecessary complexity.

---

## 1. Explicit Non-Goals
HMIE is strictly a historical market intelligence and research platform. It is **NOT** intended to become:
- A broker or trade execution platform
- A real-time trading terminal or day-trading tool
- A portfolio management system (PMS)
- A prediction engine or machine learning forecasting platform
- An autonomous trading agent
- A real-time market data vendor or low-latency price feed

---

## 2. The 180-Day Focus Period (Aug 2026 – Feb 2027)
To ensure sustained stability and real-world usage, HMIE is under a **180-Day Architecture & Schema Focus Period**.

### Permitted Work:
- UX/UI polish, clear plain-English wording, and table styling
- PDF and CSV data export capabilities
- System observability, data validation, and EOD sync pipeline hardening
- Routine data updates and bug fixes

### Forbidden Work:
- **No new analytical engines**
- **No new database schemas or tables** (except simple lookup/calendar metadata)
- **No new AI pipeline architectures**

---

## 3. The Three Final Feature Gates
Before any feature or proposal is considered after the 180-day focus period, it must pass **ALL THREE GATES**:

1. **Mission Gate**: Does it strengthen HMIE as a historical research platform? (Must not violate Non-Goals).
2. **Consumer Gate**: Has real, sustained usage (via Query Logs) demonstrated a repeated need for this feature?
3. **Complexity Gate**: Is this the absolute simplest solution that solves the real problem?

*If a proposal fails any single gate, it waits.*

---

## 4. Product & User Experience Principles
- **Answer First (BLUF)**: The first sentence of every response must directly answer the user's question in plain English.
- **Progressive Disclosure**: Information is presented in layers (Level 1: 30-Second Summary → Level 2: Key Insights → Level 3: Sortable Table → Level 4: Technical Verification Details).
- **Plain English / Zero Jargon**: Replaces statistical jargon (`Sharpe ratio`, `std dev σ`) with intuitive human terms (`Success Rate`, `Average Return`, `Most Stable Sector`).
- **No Placeholder Experiences**: Every visible dashboard feature must work immediately on launch without requiring unbuilt future infrastructure.

---

## 5. Research & Operational Principles
- **Evidence Before Opinion**: All conclusions are calculated directly from historical Oracle database price tables (`STAGING.STOCK_HIST_DATA`).
- **Historical Observations, Not Predictions**: All metrics describe past event windows ($T-3 \rightarrow T+3$, $2011–2025$) and explicitly state that future market performance can differ.
- **Reproducibility & Provenance**: Outputs carry dataset versions (`v2.0.1`), SHA-256 hashes, and git commit references.
- **Fail Loudly**: Data quality checks (duplicate dates, missing days, price anomalies $>20\%$) run automatically and log errors loudly.
