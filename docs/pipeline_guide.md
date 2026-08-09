# 📊 HMIE Data Pipeline & Management Guide (`Fyers_Hist/data_pipeline`)

This guide explains where all historical data fetching, database table creation, ingestion, and pipeline processing scripts are located within `C:\Users\vinay\.gemini\Fyers_Hist`.

---

## 📁 1. Data Fetchers (`data_pipeline/fetchers/`)
Contains API integration and data retrieval tools:
* 📄 **`fetch_15y_data.py`**: Fetches 15-year historical index & market data from the Fyers API.
* 📄 **`fetch_top_stocks.py`**: Fetches stock history across F&O and equity universes.
* 📄 **`fyers_login.py`**: Handles Fyers OAuth 2.0 authentication and session token generation.

---

## 🧱 2. SQL Schema Creation (`data_pipeline/schema_ddl/`)
Contains Oracle SQL table DDL scripts:
* 📄 **`create_table_fyers_hist_data.sql`**: DDL for `STAGING.STOCK_HIST_DATA`.
* 📄 **`create_table_raw_stock_history.sql`**: DDL for raw stock history staging tables.
* 📄 **`create_tables_stage10.sql`** & **`create_tables_stage3_*.sql`**: DDL for analytical stage tables (Stage 1 through 10).

---

## 🚀 3. Data Ingestion & Sync (`data_pipeline/ingestion/`)
Contains data loading, insertion, updating, and daily EOD sync pipelines:
* 📄 **`upload_stocks_to_db.py`**: Bulk uploads historical stock CSVs into Oracle.
* 📄 **`sync_eod_data.py`**: Daily EOD market price sync script.

---

## ⚡ 4. Processing Stages (`data_pipeline/stages/`)
Contains quantitative research pipeline stages (Stages 3 to 10):
* 📄 **`stage3_market_structure.py`**: Market structure and regime classification.
* 📄 **`stage4_historical_evidence.py`**: Event study calculator.
* 📄 **`stage6_strategy_lab.py`**: Strategy backtesting engine.
* 📄 **`stage10_plausibility_engine.py`**: Data quality & plausibility validator.

---

## 📁 5. Datasets & Files (`data_pipeline/data_files/`)
Contains exported raw data CSVs:
* 📄 **`HIST_DATA.csv`**, **`HIST_STOCK_DATA.csv`**, **`Fyers_Indices.csv`**, **`columns_definition.txt`**.
