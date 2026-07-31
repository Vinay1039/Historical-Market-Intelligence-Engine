# HMIE Operations Runbook (v3.2)

## 1. Subsystem Architecture
HMIE runs as a thin, high-performance REST API backed by Oracle XE 23c database warehouse.

```
       FastAPI Web Server (api/main.py)
                   │
                   ▼
      Oracle Database (Oracle XE 23c)
        ├── STAGING.STOCK_HIST_DATA  (2.4M+ OHLCV records)
        ├── STAGING.RESEARCH_EXECUTIONS (24 Governed Studies)
        └── STAGING.SYNC_LOGS        (EOD Pipeline Logs)
```

---

## 2. EOD Data Ingestion Pipeline & Validation
Daily automated EOD price updates are executed via `scripts/eod_sync_pipeline.py`.

### Automated Validation Suite:
1. **Duplicate Date Check**: Ensures zero duplicate date entries for any symbol.
2. **Price Anomaly Filter**: Detects invalid negative prices or single-day price jumps $>20\%$.
3. **Missing Day Check**: Verifies trading day continuity against the market calendar.

### Executing EOD Data Pipeline:
```bash
c:/Users/vinay/.gemini/.venv/Scripts/python.exe scripts/eod_sync_pipeline.py
```

---

## 3. Real-Time System Health Monitoring API
System health and data freshness can be audited via:
- **Endpoint**: `GET http://127.0.0.1:8000/api/v1/system/status`
- **Dashboard Bar**: Top status header on `http://127.0.0.1:8000/`

### Sample Health Payload:
```json
{
  "timestamp": "2026-07-31 21:08:47 IST",
  "status": "PASS",
  "dataset_version": "v2.0.1",
  "symbols_updated": "856 / 856",
  "total_records": 2429021,
  "last_trading_day": "2026-07-29",
  "data_integrity": "PASS (0 Duplicate Rows, 0 Price Anomalies)",
  "cache_refreshed": true
}
```

---

## 4. Troubleshooting & Server Recovery

### Restarting Server:
```bash
c:/Users/vinay/.gemini/.venv/Scripts/python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### Running Test Suite:
```bash
c:/Users/vinay/.gemini/.venv/Scripts/python.exe -m unittest discover -s tests
```
