# The HMIE System Constitution (v2.0.0)

This constitution defines the non-negotiable architectural laws governing the **Historical Market Intelligence Engine (HMIE)**.

---

## 📜 Core Architectural Laws

### Law 1: Historical First
All research, indicators, breadth calculations, and strategy performance must be anchored in historical facts stored in Oracle 23c XE.

### Law 2: Source of Truth (Oracle Single-Store)
Oracle 23c XE thick client is the single, authoritative source of truth. No client application or microservice shall maintain external persistent state that diverges from Oracle.

### Law 3: Zero Calculation REST API
FastAPI serves precomputed Oracle data. REST endpoints must perform zero runtime aggregations or complex calculations.

### Law 4: Quality Gate Enforcement
Every release must pass Quality Gate 1 (`verify_hmie.py`) and Quality Gate 2 (`tools/validate_historical_cases.py`) with 0 failures before deployment.

### Law 5: Determinism & Immutability
Historical trade logs, price bars, and precomputed analytical tables are immutable once committed.

### Law 6: Zero Synthetic Data
All analytics are computed exclusively from actual NSE trading bars. No synthetic data generation is permitted.

### Law 7: Evidence Over Opinion
Every market insight, regime classification, and strategy metric must be backed by precomputed evidence tables in Oracle.

### Law 8: AI Never Calculates
AI services function strictly as evidence retrieval and narration layers over precomputed Oracle SQL tables.

### Law 9: Verify Before You Trust
All quantitative metrics, drawdowns, and Sharpe ratios must undergo independent dual-pipeline reconciliation before being published.

### Law 10: Reproducibility Over Convenience
Analytical pipelines must be reproducible across time, environment, and code updates.

### Law 11: The Law of Reproducible Research
Every published research conclusion shall be reproducible from a frozen dataset, a versioned methodology, and an independently validated computation path.
