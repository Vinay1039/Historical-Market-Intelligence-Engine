# HMIE Quantitative Strategy Lab Methodology Specification (v2.0.0)

This document defines the complete quantitative methodology, math formulas, transaction friction models, and execution rules for Stage 6 & Stage 9 Strategy Lab models (`STAGING.STRATEGY_PERFORMANCE`, `STAGING.STRATEGY_FEE_SENSITIVITY`).

---

## 📐 1. Transaction Fee & Slippage Model Specification

The round-trip friction fee level $f$ models the combined drag of:
1. **STT (Securities Transaction Tax)**: $0.10\%$ on equity delivery sell orders.
2. **Brokerage & Exchange Turn-over Fees**: $\sim 0.03\%$ combined.
3. **SEBI, GST & Stamp Duty**: $\sim 0.02\%$.
4. **Execution Market Impact & Bid-Ask Slippage**: $0.05\%$ – $0.35\%$.

### Friction Sensitivity Levels ($f$)

| Friction Level ($f$) | Total Round-Trip Drag ($2 \times f$) | Target Real-World Trading Environment |
| :---: | :---: | :--- |
| **0.00%** | $0.00\%$ | Theoretical Gross Baseline |
| **0.10%** | $0.20\%$ | Low-cost Institutional / Zero Brokerage Delivery |
| **0.25%** | $0.50\%$ | Standard Retail Trading with Moderate Slippage |
| **0.50%** | $1.00\%$ | High Slippage / Illiquid Equity Rebalancing |

---

## 🧮 2. Empirical Threshold Fee Definitions

1. **Break-Even Fee Percentage ($f_{\text{break-even}}$)**:
   The maximum per-rebalance transaction cost % at which the strategy's Net CAGR equals the benchmark `NIFTY50` index CAGR ($11.28\%$).

2. **Zero-Survival Fee Percentage ($f_{\text{zero}}$)**:
   The survival zero-point transaction cost % at which the strategy's Net CAGR drops to $0.00\%$ (capital erosion boundary).

---

## 📊 3. Audited Threshold & Sensitivity Results (2011–2026)

| Strategy Code | Strategy Name | Gross CAGR (0.0%) | Net CAGR (0.10%) | Net CAGR (0.25%) | Net CAGR (0.50%) | Break-Even Fee vs NIFTY50 | Survival Zero-Point Fee |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `SECTOR_ROTATION_TOP3` | Sector Rotation Top 3 | **16.15%** | **13.42%** | **9.43%** | **3.08%** | **0.180%** | **0.627%** |
| `THEME_MOMENTUM_TOP1` | Custom Theme Leadership | **20.74%** | **17.91%** | **13.77%** | **7.16%** | **0.343%** | **0.788%** |
| `TOP_STOCK_MOMENTUM_95P` | Top Stock Momentum | **11.28%** | **8.66%** | **4.84%** | **-1.27%** | **0.001%** | **0.447%** |

---

## 📜 4. Validation History Audit Trail

- **v1.4 Bug Discovered**: Legacy Strategy 3 averaged raw daily percentage gains (`AVG(AVG_CHANGE_PCT)`), resulting in an implausible $-0.95\%$ Max Drawdown.
- **v1.5 Fix Applied**: Reconstructed monthly entry-to-exit price returns ($P_{month\_close} / P_{month\_open} - 1$), uncovering the true continuous 15-year COVID Max Drawdown of **-26.02%** and 15-year CAGR of **11.28%**.
- **v2.0 Reconciliation**: Verified **0.00% exact match** across independent trade log reconstruction (Pipeline B) and stored performance tables (Pipeline A).
