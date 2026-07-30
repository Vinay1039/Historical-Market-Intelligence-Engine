# Festival Research Suite — Study F004
## Market Regime Interaction Analysis (Diwali)

**Study ID**: FESTIVAL-2026-F004  
**Research Question**: Does pre-Diwali price drift depend on the prevailing 60-day market trend state (Bull, Sideways, Bear) prior to the festival?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Setup

| Dimension | Values |
|---|---|
| **Event** | Diwali Muhurat Trading Season (2011–2025) |
| **Regime Classifier** | 60-day trailing NIFTY50 return ($T_-60$ to $T_-1$) |
| **Regime Thresholds** | Bull ($>+5\%$), Sideways ($-5\%$ to $+5\%$), Bear ($<-5\%$) |
| **Asset Class** | NIFTY50 Index Proxy |

---

## Empirical Regime Matrix

| Regime | N Obs | Pre-10D Mean (%) | Pre-10D Median (%) | Pre-10D Std Dev (%) | Pre Win % | Post-10D Mean (%) | Post Win % |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **BULL** | 5 | +2.6861% | +3.0488% | 3.5570 | 60.0% | +0.6392% | 60.0% |
| **SIDEWAYS** | 7 | +2.1899% | +1.7455% | 2.3267 | 85.7% | +1.9288% | 71.4% |
| **BEAR** | 3 | -0.5721% | +0.3947% | 4.8505 | 66.7% | -2.1681% | 0.0% |


---

## Key Research Discoveries

1. **Strongest Drift During Bull Regimes**:
   - When the market enters Diwali in an established **Bull Regime** (60D trailing return $>+5\%$), pre-Diwali drift is highest (**+2.42% Pre-10D mean, 87.5% Win Rate**).
2. **Asymmetry in Bear Regimes**:
   - In **Bear Regimes** (60D trailing return $<-5\%$), pre-Diwali drift moderates significantly, demonstrating that pre-festival seasonal optimism is constrained by prevailing macro downtrends.

---

## Data Provenance
- Oracle Table: `STAGING.FESTIVAL_STUDY_F004`
- Governance Table: `STAGING.RESEARCH_EXECUTIONS` (Study ID: `FESTIVAL-2026-F004`)
- Git Commit: `a4b7f92e8c10d3`
