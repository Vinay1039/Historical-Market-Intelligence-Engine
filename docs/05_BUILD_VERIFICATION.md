# Quality Gate 1 — Build Verification Specification (v1.0.0)

**Tool Location**: `verify_hmie.py`

Quality Gate 1 verifies structural and build correctness after every database schema modification or ETL pipeline run.

---

## 🔍 Automated Verification Checks

1. **Oracle Database Pool Connectivity**: Validates Oracle 23c XE thick connection client.
2. **Reference Universe vs Active Universe Validation**:
   - Reference Master (`HR.STOCKS`): 6,587 securities.
   - Analytical Equities Universe (`STAGING.STOCK_HIST_DATA`): 2,234 active NSE stocks.
3. **Table & Row Count Thresholds**:
   - `STOCK_HIST_DATA`: $\ge 2,000,000$ rows
   - `SECTOR_DAILY`: $\ge 70,000$ rows
   - `INDUSTRY_DAILY`: $\ge 300,000$ rows
   - `MARKET_BREADTH_DAILY`: $\ge 3,500$ rows
   - `STOCK_RANKINGS`: $\ge 2,000,000$ rows
   - `MARKET_REGIMES`: $\ge 3,500$ rows
4. **Mandatory Column & Index Integrity**: Checks existence of `EMA_20`, `EMA_50`, `EMA_200`, `RSI_14`, `VWAP`, `SECTOR_RANK`, `REGIME_NAME`.
5. **FastAPI REST Service Response**: Verifies `POST /api/v1/market-structure/ai/narrate` returns valid zero-hallucination markdown briefings.

---

## 📊 Live Verification Status (v1.0.0)

```text
VERIFICATION SUMMARY: 18 Passed, 0 Failed.
Status: 🟩 ALL SYSTEM ENGINES VERIFIED & OPERATIONAL
```
