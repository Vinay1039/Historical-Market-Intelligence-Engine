# Momentum Research Suite — Study 002
## Trailing Momentum Lookback Sensitivity Analysis

**Study ID**: MOMENTUM-2026-002  
**Research Question**: How does trailing lookback duration (3M, 6M, 9M, 12M) impact return, risk, turnover, and implementation friction tolerance?  
**Date**: 2026-07-30  
**Status**: COMPLETED

---

## Experimental Setup

| Parameter | Value |
|---|---|
| **Tested Variable** | Trailing lookback duration ($L \in \{3, 6, 9, 12\}$ months) |
| **Fixed Parameters** | Minimum history = 60M, Top 95th percentile cut, Equal-weighted, Monthly rebalance |
| **Universe** | Full warehouse equity universe (`STAGING.STOCK_HIST_DATA`) |
| **Benchmark** | NIFTY50 proxy |

---

## Results Matrix

| Lookback | CAGR (%) | Max Drawdown (%) | Sharpe Ratio | Avg Monthly Turnover (%) | Mean HHI | Unique Symbols | Break-Even Fee (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **3 Months** | +21.00% | -43.70% | 0.65 | 54.5% | 0.0344 | 586 | 0.5657% |
| **6 Months** (Baseline) | **+24.82%** | **-35.42%** | **0.76** | **39.6%** | **0.0344** | **530** | **0.8289%** |
| **9 Months** | +29.64% | -32.24% | 0.93 | 32.7% | 0.0344 | 472 | 1.1502% |
| **12 Months** | +32.86% | -39.50% | 1.00 | 28.9% | 0.0344 | 433 | 1.3583% |

---

## Empirical Findings

1. **Turnover Decay with Longer Lookbacks**: Short lookbacks (3M) exhibit the highest monthly turnover (54.5%), which decays steadily as lookback extends to 12M (28.9%). Longer lookbacks produce more stable, persistent momentum baskets.
2. **Return Profile Curve**: CAGR spread across lookbacks is 11.87%.
3. **Fee Tolerance Sensitivity**: Break-even fee thresholds scale inversely with turnover — lower turnover strategies preserve more net alpha after implementation frictions.

---

## Research Conclusion

Within the tested range (3–12 months), the strategy exhibits structural momentum persistence across all horizons. Longer lookbacks (6M–12M) offer superior implementation efficiency due to lower turnover, while shorter lookbacks (3M) capture faster price acceleration at the cost of higher portfolio churn.

---

## Data Provenance
- Oracle table: `STAGING.SENSITIVITY_STUDY_002`
- Engine: `research/momentum_suite/002_lookback_sensitivity/run_experiment.py`
