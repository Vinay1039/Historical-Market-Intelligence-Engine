# Momentum Research Suite — Study 001
## Eligibility Threshold Sensitivity Analysis

**Study ID**: MOMENTUM-2026-001  
**Research Question**: Is TOP_STOCK_MOMENTUM_95P robust to the minimum history threshold?  
**Date**: 2026-07-30  
**Status**: COMPLETED

---

## Design

| Dimension | Values |
|---|---|
| **Variable** | Minimum history threshold (months) |
| **Values tested** | 36, 48, 60 months |
| **Fixed** | Momentum lookback = 6M, Percentile = 95th, Monthly rebalance |
| **Universe** | All STAGING.STOCK_HIST_DATA symbols (same warehouse for all runs) |
| **Benchmark** | NIFTY50 proxy (for Break-Even Fee calculation) |

**Research hypothesis**: If strategy conclusions change materially with threshold, the methodology is fragile. If they remain stable, the 60-month default is defensible.

---

## Results

| Threshold | CAGR | Max DD | Sharpe | Avg Basket | Avg Turnover | Unique Symbols | Break-Even Fee |
|---|---|---|---|---|---|---|---|
| 36 months | +26.53% | -37.56% | 0.82 | 31.0 | 39.6% | 601 | 0.9319% |
| 48 months | +23.42% | -37.04% | 0.72 | 30.2 | 39.6% | 565 | 0.7597% |
| **60 months** (default) | **+24.82%** | **-35.42%** | **0.76** | **29.5** | **39.6%** | **530** | **0.8289%** |

**CAGR range across thresholds**: 3.11%  
**Sharpe range across thresholds**: 0.10

---

## Robustness Verdict

**MODERATELY ROBUST — meaningful variation exists but direction is consistent.**

---

## Methodology Notes

- The 36-month threshold admits newer IPOs into the eligible universe earlier, increasing basket diversity but potentially including stocks with insufficient history to form reliable momentum signals.
- The 60-month threshold is the most conservative: only stocks with 5+ years of data qualify. This reduces the universe in early backtest years but produces more stable momentum rankings.
- All three thresholds produce the same momentum signal (6-month trailing return), the same ranking methodology (top 95th percentile), and the same equal-weighted portfolio construction.

---

## Data Provenance

- Oracle table: `STAGING.SENSITIVITY_STUDY_001`
- Source data: `STAGING.STOCK_HIST_DATA`
- Pipeline version: Stage 6 v1.5.0 (Algorithmic)
- Quality Gate: QG3 PASSED (61 rules, 0 FAIL, 1 WARNING) prior to this study
- All computations performed in Python — zero REST-layer calculations.

---

## Next Studies

- **Study 002**: Momentum Lookback Sensitivity (3M / 6M / 9M / 12M)
- **Study 003**: Selection Threshold Sensitivity (Top 90% / 95% / 97.5%)
- **Study 004**: Rebalance Frequency Sensitivity (Monthly vs Quarterly)
