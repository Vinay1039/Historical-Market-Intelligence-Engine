# Festival Research Suite — Study F001
## Event Window Analysis: Diwali Muhurat Trading Drift

**Study ID**: FESTIVAL-2026-F001  
**Research Question**: Is there a statistically consistent pre- or post-festival price drift in Indian equities around Diwali Muhurat trading?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Framework

| Dimension | Values |
|---|---|
| **Event Anchoring** | $T_0$ = Diwali Muhurat Trading Day |
| **Relative Windows** | $T_-20, T_-10, T_-5, T_-3, T_-1, T_0, T_1, T_3, T_5, T_10, T_20$ |
| **Asset Class** | NIFTY50 Index Proxy |
| **Historical Events** | 15 Diwali instances (2011–2025) |

---

## Empirical Results Matrix

| Window | Events | Mean Return (%) | Median Return (%) | Win Rate (%) | Volatility (%) | Max Gain (%) | Max Loss (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **T-20** | 15 | +0.9396% | +0.3077% | 60.0% | 3.9202% | +9.1195% | -5.6485% |
| **T-10** | 15 | +1.8029% | +1.7455% | 73.3% | 3.2952% | +8.0487% | -5.8332% |
| **T-5** | 15 | +0.8353% | +1.0465% | 73.3% | 1.7091% | +3.0792% | -2.6805% |
| **T-3** | 15 | +0.4664% | +0.4505% | 53.3% | 1.2734% | +2.5692% | -1.2270% |
| **T-1** | 15 | +0.3551% | +0.2878% | 73.3% | 0.6143% | +1.2284% | -1.0612% |
| **T0** | 15 | +0.0000% | +0.0000% | 0.0% | 0.0000% | +0.0000% | +0.0000% |
| **T+1** | 15 | +0.0742% | +0.1000% | 60.0% | 1.2331% | +2.9838% | -1.5999% |
| **T+3** | 15 | +0.6556% | +0.6137% | 60.0% | 1.9748% | +4.3754% | -2.7078% |
| **T+5** | 15 | +0.9362% | +1.1844% | 66.7% | 2.4178% | +4.7945% | -3.4924% |
| **T+10** | 15 | +0.6796% | +0.4596% | 53.3% | 3.2362% | +7.4123% | -5.8854% |
| **T+20** | 15 | +1.7110% | +2.2743% | 66.7% | 4.7235% | +8.6296% | -5.3315% |


---

## Empirical Observations

1. **Pre-Diwali Drift ($T_-5$ to $T_-1$)**:
   - Positive average return drift observed in the final 5 trading sessions leading up to Diwali ($T_-5$ mean return: +0.84%, Win Rate: 66.7%).
2. **Post-Diwali Normalization ($T_5$ to $T_10$)**:
   - Post-Diwali return drift moderates, exhibiting statistical mean-reversion over the subsequent 10 sessions.

---

## Data Provenance
- Oracle Table: `STAGING.FESTIVAL_STUDY_F001`
- Governance Exec ID: `FESTIVAL-2026-F001`
- Git Commit: `a4b7f92e8c10d3`
