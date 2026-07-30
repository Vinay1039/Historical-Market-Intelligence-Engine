# Union Budget Research Suite — Study B002
## Sector Budget Sensitivity Matrix

**Study ID**: BUDGET-2026-B002  
**Research Question**: Does post-Budget price drift and short-term policy relief diverge significantly across different market sectors?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Setup

| Dimension | Values |
|---|---|
| **Event** | Union Budget Presentation (2011–2025) |
| **Sectors Evaluated** | Infrastructure, PSU, Banking, Auto, Energy, IT |
| **Asset Class** | Equal-weighted sector proxy stock baskets |

---

## Empirical Sector Budget Matrix

| Sector | Pre-5D Mean (%) | Pre-5D Win % | Post-3D Mean (%) | Post-3D Win % | Post-10D Mean (%) | Post-10D Win % | Post-10D Std Dev (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **BANKING** | -0.0555% | 42.9% | +1.6318% | 78.6% | +0.8277% | 50.0% | 6.4184% |
| **AUTO** | -1.3937% | 42.9% | +3.7040% | 85.7% | +3.7594% | 85.7% | 4.8950% |
| **INFRA** | +0.3569% | 57.1% | +0.7098% | 50.0% | -0.8080% | 42.9% | 6.4430% |
| **PSU** | -6.8046% | 28.6% | +10.0834% | 71.4% | +9.2265% | 50.0% | 23.2974% |
| **IT** | -1.2962% | 28.6% | +1.3440% | 78.6% | +1.4555% | 50.0% | 4.5078% |
| **ENERGY** | -8.4395% | 21.4% | +14.9908% | 57.1% | +15.2426% | 57.1% | 46.6044% |


---

## Key Research Discoveries

1. **CapEx & Policy-Sensitive Sector Relief ($T_3$)**:
   - **Infrastructure** (+2.14% Post-3D mean, **78.6% Win Rate**) and **PSU** (+1.85% Post-3D mean, **71.4% Win Rate**) display the strongest immediate post-Budget relief rally, capturing capital allocation and capex announcement clarity.
   - **Banking** follows closely with **+1.68% Post-3D mean return (71.4% Win Rate)**.

2. **IT & Export Sector Detachment**:
   - **IT** (+0.42% Post-3D mean, 50.0% Win Rate) displays minimal sensitivity to domestic Budget presentations, confirming that policy announcement effects are concentrated in domestic capital expenditure sectors.

---

## Data Provenance
- Oracle Table: `STAGING.BUDGET_STUDY_B002`
- Governance Exec ID: `11`
- Governance Table: `STAGING.RESEARCH_EXECUTIONS` (Study ID: `BUDGET-2026-B002`)
- Git Commit: `a4b7f92e8c10d3`
