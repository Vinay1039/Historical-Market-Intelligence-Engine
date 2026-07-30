# HMIE Master Architecture (v1.5.0)

**Status**: Baseline Scope Implemented & Verified Against Current Test Suite  
**Compliance**: HMIE Constitution Laws 1–10  

---

## 📐 System Layers & Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HMIE SYSTEM ARCHITECTURE                         │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│ ANALYTICAL ENGINES       │ APPLICATIONS             │ INFRASTRUCTURE        │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ 🟩 Data Ingestion        │ 🟩 Historical Evidence   │ 🟩 Oracle Database 23c│
│ 🟩 Technical Indicators  │ 🟩 Research Explorer UI  │ 🟩 FastAPI REST API   │
│ 🟩 Market Structure      │ 🟩 Strategy Lab (Exper.) │ 🟩 Quality Gate 1     │
│ 🟩 Breadth & Rotation    │ 🟩 Visual Dashboard      │ 🟩 Quality Gate 2     │
│ 🟩 Stock Rankings        │ 🟩 AI Evidence Narrator  │ 🟩 EOD FYERS Sync     │
│ 🟩 Themes & Regimes      │                          │                       │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## 📊 Analytical Universe vs Reference Universe

- **Reference Universe**: **6,587 securities** stored in `HR.STOCKS` (NSE + BSE reference master).
- **Active Analytical Universe (v1.0.0+)**: **2,234 active NSE equities** stored in `STAGING.STOCK_HIST_DATA`. All indicators, market structure aggregations, themes, regimes, and backtests are computed on active NSE equities.

---

## 🗄️ Database Table Inventory (`STAGING` Schema)

| Table Name | Description | Rows | Primary Key | Refresh Frequency |
| :--- | :--- | :---: | :--- | :--- |
| `HR.STOCKS` | Master Stock Directory | 6,587 | `SYMBOL` | On Re-seed |
| `STAGING.STOCK_HIST_DATA` | Daily OHLCV + Indicators | 2,429,021 | `(SYMBOL, DATETIME)` | Daily EOD |
| `STAGING.SECTOR_MASTER` | Sector Master Definitions | 20 | `SECTOR_CODE` | Static |
| `STAGING.INDUSTRY_MASTER` | Industry Master Definitions | 118 | `INDUSTRY_CODE` | Static |
| `STAGING.SECTOR_DAILY` | Sector Daily Aggregates | 71,131 | `(SECTOR_CODE, DATETIME)` | Daily EOD |
| `STAGING.INDUSTRY_DAILY` | Industry Daily Aggregates | 348,181 | `(INDUSTRY_CODE, DATETIME)` | Daily EOD |
| `STAGING.SECTOR_PERFORMANCE` | Monthly, Quarterly, Annual Sector Stats | 240 | `(SECTOR_CODE, PERIOD)` | Daily EOD |
| `STAGING.INDUSTRY_PERFORMANCE` | Monthly, Quarterly, Annual Industry Stats | 1,224 | `(INDUSTRY_CODE, PERIOD)` | Daily EOD |
| `STAGING.MARKET_BREADTH_DAILY` | Daily Advance/Decline & EMA Breadth | 3,714 | `DATETIME` | Daily EOD |
| `STAGING.SECTOR_ROTATION` | Sector Relative Strength & Ranks | 71,131 | `(SECTOR_CODE, DATETIME)` | Daily EOD |
| `STAGING.INDUSTRY_ROTATION` | Industry Relative Strength & Ranks | 348,181 | `(INDUSTRY_CODE, DATETIME)` | Daily EOD |
| `STAGING.STOCK_RANKINGS` | Intra-Industry & Market Stock Ranks | 2,429,021 | `(SYMBOL, DATETIME)` | Daily EOD |
| `STAGING.THEME_MASTER` | Custom Theme Basket Definitions | 5 | `THEME_CODE` | Static |
| `STAGING.THEME_DAILY` | Theme Daily Aggregates | 18,565 | `(THEME_CODE, DATETIME)` | Daily EOD |
| `STAGING.THEME_ROTATION` | Theme Relative Strength & Ranks | 18,565 | `(THEME_CODE, DATETIME)` | Daily EOD |
| `STAGING.MARKET_REGIMES` | Macro Market Regimes & Duration | 3,714 | `DATETIME` | Daily EOD |
| `STAGING.EVIDENCE_CORRECTIONS` | Historical Drawdowns & Recoveries ($N=9$) | 9 | `EVENT_ID` | On ETL Rebuild |
| `STAGING.EVIDENCE_MACRO_EVENTS` | Budget, Election & Crisis Events ($N=12$) | 12 | `EVENT_ID` | On ETL Rebuild |
| `STAGING.STRATEGY_PERFORMANCE` | Backtest Metrics Summary (Experimental) | 3 | `STRATEGY_ID` | On Backtest Exec |
| `STAGING.STRATEGY_TRADES` | Backtest Rebalance Trade Logs | 537 | `TRADE_ID` | On Backtest Exec |
