# HMIE (Historical Market Intelligence Engine)
# Master Architecture & Development Specification v1.0

---

## 1. Project Vision

HMIE (Historical Market Intelligence Engine) is a personal long-term historical market research platform built to understand how Indian financial markets have behaved over long periods.

This project exists because I want to become a better long-term investor by understanding historical market behaviour through evidence rather than opinions.

The objective is not to build another Bloomberg Terminal, FactSet, Morningstar, TradingView, Screener, or portfolio tracker.

It is not a commercial product.
It is not an enterprise platform.
It is not intended for multiple developers or large teams.

It is a personal research platform that will be designed, developed, and maintained by a single developer over many years.

The architecture should optimize for:

- **Simplicity**
- **Correctness**
- **Maintainability**
- **Explainability**
- **Incremental evolution**
- **Historical accuracy**

Avoid enterprise complexity unless it provides clear long-term value.

---

## 2. Project Goals

The purpose of HMIE is to answer historical research questions such as:

- Which sectors consistently outperform?
- Which industries perform best after Union Budget?
- Which sectors lead during bull markets?
- Which industries recover fastest after corrections?
- How broad was a historical rally?
- Which events historically affected markets the most?
- Which companies consistently outperform their peers?

The system should answer these questions using **historical evidence rather than prediction**.

---

## 3. Core Design Philosophy

These principles are the **constitution of HMIE**.

Every future design decision must follow them.

---

### Principle 1 — Historical First

Everything begins with historical data.

Never predictions. Never opinions. Never speculation.

---

### Principle 2 — ETL Owns Intelligence

Business logic belongs inside ETL.

```
ETL performs calculations.
Oracle stores analytical results.
FastAPI exposes precomputed data.
MIT visualizes.
AI summarizes.
```

No calculations inside APIs.
No calculations inside the UI.

---

### Principle 3 — Complexity Must Be Earned

Prefer deterministic algorithms over sophisticated models.
Avoid unnecessary enterprise patterns.
Do not introduce complexity until historical research proves it is needed.

---

### Principle 4 — Incremental Evolution

Design for future expansion.
Implement one analytical engine at a time.
Never build future modules before they have a consumer.

---

### Principle 5 — Version Everything

Every analytical calculation must be reproducible.

Support versioning for:
- Formula
- ETL
- Calculation Date
- Data Source

---

### Principle 6 — Research Before Features

Every analytical engine must answer at least one meaningful research question.

Do not build features because they are interesting.
Build them because they improve research capability.

---

### Principle 7 — Every Table Must Have a Consumer

Before creating a database table ask:

- Who will consume it?
- Dashboard?
- API?
- AI?

If nothing consumes it, do not build it yet.

---

### Principle 8 — AI Never Calculates

The AI Assistant retrieves analytical results.
It never performs calculations.
It never invents numbers.
It only summarizes evidence.

---

## 4. Technical Architecture

```
Data Sources
  Fyers
  Yahoo Finance
  TradingView
       │
       ▼
Python ETL
  Stage 1 — Historical Market Data
       │
       ▼
  Stage 2 — Technical Indicators
       │
       ▼
  Stage 3 — Market Structure Intelligence
       │
       ▼
Oracle Database
       │
       ▼
FastAPI (Read Only)
       │
       ▼
Market Intelligence Terminal (MIT)
       │
       ▼
Future AI Research Assistant
```

---

## 5. Database Philosophy

Database should evolve incrementally.
Do not create future tables until the corresponding analytical engine exists.

Organize the database into logical schemas:

| Schema | Purpose |
| :--- | :--- |
| `MASTER` | Reference Data (Stocks, Sectors, Industries, Events) |
| `STAGING` | Raw Historical Data (as ingested from data providers) |
| `ANALYSIS` | Analytical Results (precomputed by ETL engines) |
| `CONFIG` | Versioned Configuration |
| `LOG` | Execution Logs |

---

## 6. Analytical Engines

HMIE will evolve by adding independent analytical engines.

Examples include:

- Market Structure
- Breadth
- Rotation
- Rankings
- Themes
- Historical Regimes
- Event Analysis
- Seasonality

Each engine must:

- Answer specific research questions.
- Own its ETL logic.
- Expose read-only APIs.
- Evolve independently.
- Be versioned independently.

Each engine should be **independently recomputable within the same ETL process** — not implemented as a separate microservice.

---

## 7. Development Workflow

Before building any engine, create a short **Module Specification** containing:

1. Research question(s) this engine answers.
2. Required database tables.
3. ETL logic summary.
4. API endpoints.
5. Dashboard consumers.
6. AI consumers.
7. Definition of Done.

**Do not write code before this specification exists.**

---

## 8. Current Scope (Version 1)

The current focus is historical analytics.

- No live trading.
- No forecasting.
- No recommendations.
- No optimization engines.
- No machine learning.
- No black-box models.

Future capabilities will only be added when justified by real research needs.

---

## 9. Known Simplifications

Version 1 intentionally favors simplicity.

| Simplification | Note |
| :--- | :--- |
| Current stock-to-sector membership used (not point-in-time) | Sufficient for long-term research |
| Rule-based market regimes, not ML | More explainable, easier to maintain |
| Deterministic scoring formulas | Reproducible and auditable |
| Single Oracle database | Right size for personal platform |
| Single Python ETL pipeline | No microservices, no queue overhead |
| Single FastAPI application | All routers under one server |

These are **conscious architectural decisions**, not limitations.
Future versions may refine them if research demonstrates clear value.

---

## 10. Authoritative Price Data Policy (ADR-001)

| Table | Purpose | Used By |
| :--- | :--- | :--- |
| `STAGING.RAW_STOCK_HISTORY` | Original unadjusted OHLCV from provider | Data audit, validation, `/api/v1/history` |
| `STAGING.STOCK_HIST_DATA` | Adjusted OHLCV + 40+ pre-computed indicators | All analytics, dashboards, AI, `/api/v1/technical`, `/api/v1/dashboard` |

**Rule**: All analytical engines (Stage 3+), dashboards, and AI always consume `STAGING.STOCK_HIST_DATA`.  
Raw data is for audit and data lineage only.

---

## 11. Success Criteria

HMIE succeeds if it helps answer historical market questions accurately, reproducibly, and transparently.

Success is measured by:

- **Historical insight** — Does it answer meaningful research questions?
- **Correctness** — Are calculations accurate and verifiable?
- **Explainability** — Can results be traced back to their source data?
- **Maintainability** — Can a single developer understand and extend it years later?
- **Ease of extension** — Can new engines be added without rearchitecting?
- **Research value** — Does each new module earn its place?

Not by architectural sophistication.

---

## 12. Instructions for the AI Assistant

When reviewing or extending HMIE:

1. Respect the project philosophy above all else.
2. Do not introduce enterprise architecture without strong justification.
3. Recommend the simplest solution that satisfies the research objective.
4. Preserve backward compatibility whenever practical.
5. Challenge assumptions when appropriate.
6. Explain trade-offs clearly.
7. Prefer modular, deterministic, and versioned designs.
8. If multiple solutions exist, recommend the one a solo developer can realistically build and maintain over many years.

---

## 13. Current Status

| Component | Status |
| :--- | :--- |
| Stage 1 ETL — Raw OHLCV Ingestion | ✅ Complete |
| Stage 2 ETL — Technical Indicators (40+ columns) | ✅ Complete |
| Oracle `STAGING.RAW_STOCK_HISTORY` | ✅ Live (1.4M+ rows) |
| Oracle `STAGING.STOCK_HIST_DATA` | ✅ Live (2.4M+ rows, 900 stocks) |
| FastAPI REST Layer | ✅ Live (Port 8000) |
| ADR-001 Authoritative Price Data Policy | ✅ Documented |
| Market Intelligence Terminal (MIT) v1 | ✅ Live |
| Stage 3 ETL — Market Structure Intelligence | 🔲 Planned |
| Market Structure Module | 🔲 Planned |
| Breadth Engine | 🔲 Planned |
| Rotation Engine | 🔲 Planned |
| AI Research Assistant | 🔲 Future |

---

*Document Version: 1.0*
*Created: 2026-07-30*
*Owner: Single Developer Personal Project*
