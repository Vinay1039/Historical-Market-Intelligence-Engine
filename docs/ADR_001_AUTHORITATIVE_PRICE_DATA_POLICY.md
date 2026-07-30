# HMIE Architecture Decision Record (ADR-001)

## Authoritative Price Data Policy

### Objective

Define the authoritative source of historical price data throughout the Historical Market Intelligence Engine (HMIE).

This decision is binding for the ETL, Oracle database, FastAPI layer, Market Intelligence Terminal (MIT), and all future AI Agents.

---

## Rule 1 — Raw Historical Data

Table: `STAGING.RAW_STOCK_HISTORY`

Purpose:
- Original downloaded OHLCV data
- No corporate action adjustments
- Historical archive
- ETL input
- Data validation
- Audit and reconciliation

This table represents the original market data exactly as received from the data provider.

---

## Rule 2 — Processed Historical Data

Table: `STAGING.STOCK_HIST_DATA`

Purpose:
- Corporate-action-adjusted price series
- Technical indicator calculations
- Calendar analytics
- Feature engineering
- Seasonality
- Dashboard analytics

This is the **authoritative analytical dataset** used throughout HMIE.

All technical indicators are calculated exclusively from this adjusted series.

---

## Rule 3 — API Contract

### GET /api/v1/history/{symbol}
Source: `STAGING.RAW_STOCK_HISTORY`
Returns:
- Raw OHLCV
- Unadjusted historical prices

> Returns the original unadjusted historical market data. Prices are not adjusted for corporate actions such as stock splits, bonus issues, or dividends.

---

### GET /api/v1/technical/{symbol}
Source: `STAGING.STOCK_HIST_DATA`
Returns:
- Adjusted OHLCV
- Technical indicators
- Derived analytics

All prices returned by this endpoint are corporate-action-adjusted.

---

### GET /api/v1/dashboard/{symbol}
Source: `STAGING.STOCK_HIST_DATA`

Dashboard charts, indicators, and summary statistics must always use the adjusted price series to ensure consistency between price data and calculated indicators.

---

## Rule 4 — MIT Usage

The Market Intelligence Terminal (MIT) shall use `/api/v1/dashboard` or `/api/v1/technical` for all default charts and analytical views.

The endpoint `/api/v1/history` shall only be used when explicitly viewing or exporting the original unadjusted historical dataset.

---

## Rule 5 — AI Agent Usage

All AI Agents (Seasonality Agent, Festival Agent, Holiday Agent, Budget Agent, Similarity Engine, Observation Case Bank, etc.) shall consume adjusted historical prices from `STAGING.STOCK_HIST_DATA` unless the research question explicitly requires the original raw market data.

---

## Architectural Principle

There shall be only one authoritative analytical price series within HMIE: `STAGING.STOCK_HIST_DATA`.

This guarantees:
- Consistent technical indicators
- Consistent charts
- Consistent seasonality calculations
- Consistent AI observations
- Consistent backtesting
- Consistent dashboard metrics
