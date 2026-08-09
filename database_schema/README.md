# HMIE Database Schema Documentation 🗄️

This directory contains the authoritative Oracle Database DDL scripts and schema definitions for the **Historical Market Intelligence Engine (HMIE v1.0.0)**.

---

## 📂 Directory Structure

```
database_schema/
├── README.md                      # This documentation guide
├── master_schema.sql              # Master DDL script creating all STAGING & ANALYSIS tables
└── table_inventory.md             # Detailed column-by-column inventory and descriptions
```

---

## 🗃️ Core Table Summary

| Table Name | Schema | Description | Primary Key |
|:---|:---:|:---|:---|
| **`RAW_STOCK_HISTORY`** | `STAGING` | Stores un-processed OHLCV price series | `(SYMBOL, DATETIME)` |
| **`STOCK_HIST_DATA`** | `STAGING` | 40-column enriched price series (EMAs, RSI, VWAP) | `(SYMBOL, DATETIME)` |
| **`SECTOR_MASTER`** | `STAGING` | Sector index symbols, categories & weights | `SECTOR_CODE` |
| **`SECTOR_ROTATION`** | `STAGING` | Sector momentum, relative strength & ranks | `(DATETIME, SECTOR_CODE)` |
| **`MARKET_REGIMES`** | `STAGING` | Daily market regime (Bull, Bear, Consolidation) | `DATETIME` |
| **`EVIDENCE_CORRECTIONS`** | `STAGING` | Historical market drawdowns & recoveries | `EVENT_ID` |
| **`EVIDENCE_MACRO_EVENTS`** | `STAGING` | Macro events (RBI, Budgets, Festivals, Elections) | `EVENT_ID` |
| **`EVENT_ANALOG_CASES`** | `ANALYSIS` | Precalculated analog case similarity rankings | `CASE_ID` |
| **`SYNC_LOGS`** | `STAGING` | EOD pipeline execution logs & data integrity status | `LOG_ID` |

---

## ⚡ Execution Instructions

To execute the DDL scripts and create the database schema in Oracle XE:

```sql
-- Connect to Oracle SQL*Plus or SQL Developer as STAGING user:
sqlplus staging/password@localhost:1521/XE

-- Execute the master schema creation script:
@master_schema.sql
```
