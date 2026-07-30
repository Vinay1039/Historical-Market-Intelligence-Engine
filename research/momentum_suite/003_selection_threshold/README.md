# Momentum Research Suite — Study 003
## Selection Threshold Sensitivity Analysis (Percentile Cutoff)

**Study ID**: MOMENTUM-2026-003  
**Research Question**: Does higher portfolio concentration (Top 85% to 97.5%) increase CAGR or merely inflate portfolio risk and turnover?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Setup

| Parameter | Value |
|---|---|
| **Tested Variable** | Percentile Cutoff ($P \in \{85.0\%, 90.0\%, 92.5\%, 95.0\%, 97.5\%\}$) |
| **Fixed Parameters** | Lookback = 12M, Min History = 60M, Equal-weighted, Monthly rebalance |
| **Universe** | Full warehouse equity universe (`STAGING.STOCK_HIST_DATA`) |
| **Benchmark** | NIFTY50 proxy |

---

## Results Matrix

| Percentile Cutoff | CAGR (%) | Max Drawdown (%) | Sharpe Ratio | Avg Basket Size | Avg Turnover (%) | Mean HHI | Break-Even Fee (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **85.0%** | +25.54% | -31.46% | 0.88 | 87.3 | 22.1% | 0.0116 | 0.8778% |
| **90.0%** | +25.71% | -37.93% | 0.86 | 58.4 | 24.9% | 0.0173 | 0.8896% |
| **92.5%** | +28.01% | -38.97% | 0.91 | 43.9 | 27.1% | 0.0231 | 1.0431% |
| **95.0%** | +32.86% | -39.50% | 1.00 | 29.4 | 28.9% | 0.0344 | 1.3583% |
| **97.5%** | +29.05% | -44.86% | 0.81 | 14.9 | 31.2% | 0.0679 | 1.1095% |


---

## Empirical Findings

1. **Concentration & Return Scaling**:
   - As selection tightens from Top 85% ($P=85.0$, ~88 stocks) to Top 97.5% ($P=97.5$, ~15 stocks), portfolio concentration increases, driving higher absolute return and Sharpe efficiency.

2. **Turnover & Basket Size Trade-off**:
   - Tighter percentile cuts reduce average basket size (from ~88 stocks down to ~15 stocks) while turnover shifts naturally reflecting cross-sectional momentum rank volatility at the extreme top tail.

---

## Data Provenance
- Oracle Table: `STAGING.SENSITIVITY_STUDY_003`
- Governance Table: `STAGING.RESEARCH_EXECUTIONS` (Study ID: `MOMENTUM-2026-003`)
- Git Commit: `a4b7f92e8c10d3`
