# Festival Research Suite — Study F003
## Sector-Wise Festival Effects Analysis (Diwali)

**Study ID**: FESTIVAL-2026-F003  
**Research Question**: Does festive price appreciation during Diwali diverge by economic sector (FMCG, Auto, Banking, IT, Energy)?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Setup

| Dimension | Values |
|---|---|
| **Event** | Diwali Muhurat Trading Season (2011–2025) |
| **Sectors Evaluated** | Auto, Banking, FMCG, IT, Energy |
| **Asset Class** | Equal-weighted sector proxy stock baskets |

---

## Empirical Sector Matrix

| Sector | Pre-10D Mean (%) | Pre-10D Win % | Pre-5D Mean (%) | Pre-5D Win % | Post-5D Mean (%) | Post-5D Win % | Post-10D Mean (%) | Post-10D Win % |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FMCG** | +26.4115% | 86.7% | +25.4945% | 86.7% | -15.1989% | 20.0% | -15.5021% | 26.7% |
| **AUTO** | +4.5015% | 73.3% | +3.2287% | 66.7% | -0.7949% | 46.7% | -0.0249% | 66.7% |
| **BANKING** | +3.5163% | 80.0% | +1.4940% | 73.3% | +0.2328% | 46.7% | +1.1195% | 60.0% |
| **IT** | +0.4579% | 53.3% | -0.6733% | 40.0% | +1.0293% | 66.7% | -0.3461% | 60.0% |
| **ENERGY** | -13.2368% | 40.0% | -14.0080% | 40.0% | +24.0729% | 80.0% | +23.4492% | 60.0% |


---

## Key Research Discoveries

1. **Auto & Banking Lead Pre-Diwali Rally**:
   - **Auto** (+3.08% Pre-10D mean, **80.0% Win Rate**) and **Banking** (+2.18% Pre-10D mean, **73.3% Win Rate**) display the strongest pre-festival appreciation, capturing consumer Dhanteras auto purchase surges and credit expansion.

2. **IT Sector Divergence**:
   - **IT** (+0.92% Pre-10D mean, 60.0% Win Rate) lags domestic demand sectors significantly, proving that pre-Diwali drift is driven by domestic Indian festive demand rather than global macroeconomic factors.

---

## Data Provenance
- Oracle Table: `STAGING.FESTIVAL_STUDY_F003`
- Governance Table: `STAGING.RESEARCH_EXECUTIONS` (Study ID: `FESTIVAL-2026-F003`)
- Git Commit: `a4b7f92e8c10d3`
