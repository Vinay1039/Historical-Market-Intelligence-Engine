# HMIE Research Scope & Model Limitations (v1.5.0)

This document explicitly defines the operational boundaries, data constraints, research assumptions, and sample size disclosures for the Historical Market Intelligence Engine (HMIE).

---

## 📌 Data Universe Scope

1. **Exchange & Equity Universe**:
   - Primary active analytical universe: **2,234 active NSE equities** stored in `STAGING.STOCK_HIST_DATA`.
   - Reference universe (`HR.STOCKS` containing 6,587 securities) includes BSE equities used for symbol reference mapping only.

2. **Sector & Industry Taxonomy**:
   - Sectors (20) and Industries (118) adhere to current GICS taxonomy classifications. Historical sector reclassifications prior to ingestion are mapped to current industry masters.

---

## 📊 Sample Size Disclosures ($N$)

All aggregate statistical claims in HMIE documentation and AI Evidence Narrator briefings MUST include explicit sample size disclosures:

- **Historical Market Drawdowns & Recoveries**: **$N = 9$ drawdown events** (2011–2026).
- **Macro Event Pre/Post Performance**: **$N = 12$ macro event windows** (5 Union Budgets, 3 General Elections, 4 Macro Crises).
- **Macro Regimes Classification**: **$N = 3,714$ trading days** (2011–2026).

---

## 📈 Quantitative Strategy Lab Assumptions & Limitations

Strategy backtest models in `STAGING.STRATEGY_PERFORMANCE` (`v1.4.0` / `v1.5.0`) are experimental research models and subject to the following assumptions:

1. **Transaction Costs & Slippage**:
   - V1 backtest models assume zero brokerage fees, zero securities transaction tax (STT), and zero execution slippage.

2. **Rebalance Mechanics**:
   - Strategies rebalance monthly on the first trading day of each month based on equal weighting across constituents.

3. **Survivorship Bias**:
   - Stock percentiles are evaluated on active trading universe equities. Delisted companies prior to 2011 are excluded.

4. **Risk-Free Rate**:
   - Sharpe Ratios assume a fixed annual risk-free rate of **5.0% p.a.** ($RF_{monthly} = 0.4167\%$).
