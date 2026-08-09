# HMIE Oracle Table Inventory & Schema Reference

> **Database Engine**: Oracle 11g / 21c / 23c XE  
> **Primary Schemas**: `STAGING`, `ANALYSIS`

---

## 1. `STAGING.STOCK_HIST_DATA` (Enriched Daily Price Series)

Stores the 40-column enriched daily price history across 856 NSE symbols (2011–2026).

| Column Name | Data Type | Constraint | Description |
|:---|:---:|:---:|:---|
| `SYMBOL` | `VARCHAR2(50)` | `NOT NULL` | NSE Stock Ticker Symbol (e.g. `SBIN`, `INFY`, `RELIANCE`) |
| `DATETIME` | `DATE` | `NOT NULL` | Daily EOD Trading Session Date |
| `OPEN` | `NUMBER(12,4)` | | Session Opening Price |
| `HIGH` | `NUMBER(12,4)` | | Session High Price |
| `LOW` | `NUMBER(12,4)` | | Session Low Price |
| `CLOSE` | `NUMBER(12,4)` | | Session Closing Price |
| `CHANGE` | `NUMBER(12,4)` | | Single-Day Price Change |
| `CHANGE_PERCENT` | `NUMBER(8,4)` | | Single-Day Price Change Percentage |
| `VOLUME` | `NUMBER(15,0)` | | Total Traded Volume |
| `VWAP` | `NUMBER(12,4)` | | Volume Weighted Average Price |
| `EMA_20` | `NUMBER(12,4)` | | 20-Period Exponential Moving Average |
| `EMA_50` | `NUMBER(12,4)` | | 50-Period Exponential Moving Average |
| `EMA_200` | `NUMBER(12,4)` | | 200-Period Exponential Moving Average |
| `RSI_14` | `NUMBER(8,4)` | | 14-Period Relative Strength Index |
| `MACD` | `NUMBER(12,4)` | | Moving Average Convergence Divergence Line |
| `MACD_SIGNAL` | `NUMBER(12,4)` | | MACD Signal Line |

*Primary Key*: `(SYMBOL, DATETIME)`

---

## 2. `STAGING.EVIDENCE_CORRECTIONS` (Market Correction Events)

Stores precomputed historical market drawdowns ($\ge 10\%$) and recovery timelines.

| Column Name | Data Type | Constraint | Description |
|:---|:---:|:---:|:---|
| `EVENT_ID` | `NUMBER(6,0)` | `PRIMARY KEY` | Unique Correction Event Identifier |
| `EVENT_NAME` | `VARCHAR2(80)` | `NOT NULL` | Descripton (e.g., `Correction (Oct 2016 - -12.7%)`) |
| `PEAK_DATE` | `DATE` | `NOT NULL` | Peak Nifty 50 Closing Date before decline |
| `TROUGH_DATE` | `DATE` | `NOT NULL` | Maximum Drawdown Trough Closing Date |
| `RECOVERY_DATE` | `DATE` | | Full Recovery Closing Date (New Peak) |
| `MAX_DRAWDOWN_PCT` | `NUMBER(6,2)` | | Max Drawdown Depth Percentage (e.g., `-12.66%`) |
| `CORRECTION_DAYS` | `NUMBER(6,0)` | | Elapsed Days from Peak to Trough |
| `RECOVERY_DAYS` | `NUMBER(6,0)` | | Elapsed Days from Trough to Full Recovery |
| `RECOVERY_TYPE` | `VARCHAR2(30)` | | Pattern Classification (`V_SHAPED`, `U_SHAPED`) |
| `TOP_SECTOR_60D` | `VARCHAR2(50)` | | Leading Outperforming Sector in Post-Trough Window |

---

## 3. `STAGING.EVIDENCE_MACRO_EVENTS` (Macro & Seasonal Events)

Stores precomputed macro event windows (RBI Policy Meetings, Union Budgets, Festivals, Elections).

| Column Name | Data Type | Constraint | Description |
|:---|:---:|:---:|:---|
| `EVENT_ID` | `NUMBER(6,0)` | `PRIMARY KEY` | Unique Macro Event Identifier |
| `EVENT_NAME` | `VARCHAR2(100)` | `NOT NULL` | Event Name (e.g. `Union Budget 2017`, `RBI Policy Feb 2023`) |
| `EVENT_CATEGORY` | `VARCHAR2(30)` | `NOT NULL` | Classification (`BUDGET`, `RBI`, `FESTIVAL`, `ELECTION`) |
| `EVENT_DATE` | `DATE` | `NOT NULL` | Announcement / Event Date ($T_0$) |
| `PRE_30D_MARKET_RETURN` | `NUMBER(6,2)` | | Nifty 50 Index Return in $T-30 \rightarrow T_0$ Window |
| `POST_30D_MARKET_RETURN` | `NUMBER(6,2)` | | Nifty 50 Index Return in $T_0 \rightarrow T+30$ Window |
| `TOP_SECTOR_POST_30D` | `VARCHAR2(50)` | | Outperforming Sector in $T+30$ Window |

---

## 4. `STAGING.MARKET_REGIMES` (Daily Market Structure Regimes)

Stores daily aggregate market breadth, regime classification, and EMA trend coverage.

| Column Name | Data Type | Constraint | Description |
|:---|:---:|:---:|:---|
| `DATETIME` | `DATE` | `PRIMARY KEY` | Session Date |
| `REGIME_NAME` | `VARCHAR2(50)` | `NOT NULL` | Regime (`BULL_EXPANSION`, `BEAR_CAPITULATION`, `LATERAL`) |
| `REGIME_DURATION_DAYS` | `NUMBER(5,0)` | | Consecutive Trading Days in Current Regime |
| `PCT_ABOVE_EMA20` | `NUMBER(5,2)` | | % of Universe Trading Above 20 EMA |
| `PCT_ABOVE_EMA50` | `NUMBER(5,2)` | | % of Universe Trading Above 50 EMA |
| `PCT_ABOVE_EMA200` | `NUMBER(5,2)` | | % of Universe Trading Above 200 EMA |
| `BREADTH_RATIO` | `NUMBER(6,3)` | | Advances to Declines Ratio |
| `NET_ADVANCES` | `NUMBER(5,0)` | | Net Advancing Stocks |
