# HMIE Research Confidence & Methodology Cards (v1.5.0)

This document provides explicit research confidence cards and strategy methodology parameters for all analytical outputs produced by HMIE.

---

## 📌 Analytical Research Confidence Cards

| Research Output / Metric | Sample Size ($N$) | Time Span | Formula Version | Quality Gate Status | Confidence Note |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Market Regimes & Breadth** | $N = 3,714$ days | 2011–2026 | `v1.0.0` | 🟩 Gate 1 & 2 Passed | High confidence across 15-year NSE daily bar history |
| **Sector & Theme Rotation** | $N = 71,131$ sector days | 2011–2026 | `v1.0.0` | 🟩 Gate 1 & 2 Passed | High confidence 3M rolling relative strength ranks |
| **Historical Drawdowns & Recoveries** | $N = 9$ drawdowns | 2011–2026 | `v1.1.0` | 🟩 Gate 1 & 2 Passed | $N=9$ sample size; interpret recovery patterns with context |
| **Macro Event Responses** | $N = 12$ macro events | 2011–2026 | `v1.1.0` | 🟩 Gate 1 & 2 Passed | Pre/Post 30-day window return analysis |
| **Quantitative Strategy Lab** | $N = 180$ monthly trades | 2011–2026 | `v1.4.0` | 🟩 Gate 1 & 2 Passed | Experimental strategy backtest models |

---

## ⚙️ Strategy Lab Methodology Parameters (`STAGING.STRATEGY_PERFORMANCE`)

- **Analytical Universe**: 2,234 active NSE equities (`STAGING.STOCK_HIST_DATA`).
- **Rebalance Frequency**: Monthly on first trading day of month ($N=180$ rebalances).
- **Position Sizing**: Equal-weighted basket across qualifying constituents.
- **Benchmark**: NIFTY Equal Weight index (`NIFTY_EQUAL`).
- **Transaction Costs & Slippage**: Zero brokerage fees / zero slippage in V1 models.
- **Risk-Free Rate**: Fixed 5.0% p.a. ($RF_{monthly} = 0.4167\%$).
- **Basket Diversification Note (Strategy 3)**:
  - Strategy 3 (`TOP_STOCK_MOMENTUM_95P`) averages returns across all stocks in the top 95th percentile of industry rank ($\approx 50-100$ stocks per month).
  - This cross-industry basket diversification significantly dampens single-stock volatility, yielding low month-over-month portfolio drawdowns (-0.95%).
