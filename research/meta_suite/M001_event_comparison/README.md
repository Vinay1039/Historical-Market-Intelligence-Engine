# Meta-Research Suite — Study M001
## Cross-Domain Event Comparison & Bootstrap Confidence Intervals

**Study ID**: META-2026-M001  
**Research Question**: When synthesized across all governed event domains (Festivals & Union Budgets), which market event exhibits the highest return magnitude, win rate consistency, and statistical effect size?  
**Date**: 2026-07-30  
**Status**: COMPLETED (Governed & Canonical)

---

## Experimental Setup

| Dimension | Values |
|---|---|
| **Events Compared** | Diwali, Union Budget, Ganesh Chaturthi, Dussehra, Holi |
| **Statistical Inference** | Bootstrap 5,000 Resamplings for 95% CIs, Cohen's d Effect Size |
| **Asset Class** | NIFTY50 Index Proxy |
| **Sample Window** | 2011–2025 |

---

## Empirical Cross-Domain Synthesis Matrix

| Event | Event Type | N Obs | Pre-10D Mean (%) | Pre-10D Win % | Pre-10D 95% Bootstrap CI | Post-3D Mean (%) | Post-3D Win % | Post-3D 95% Bootstrap CI | Effect Size (Cohen's d) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Diwali** | SEASONAL | 15 | +1.8029% | 73.3% | [+0.22%, +3.40%] | +0.6556% | 60.0% | [-0.30%, +1.64%] | 0.55 |
| **Union Budget** | POLICY | 14 | -0.3505% | 35.7% | [-1.41%, +0.80%] | +1.1836% | 78.6% | [-0.34%, +2.88%] | -0.16 |
| **Ganesh Chaturthi** | SEASONAL | 15 | +1.3154% | 60.0% | [+0.12%, +2.62%] | +0.4069% | 53.3% | [-0.29%, +1.13%] | 0.51 |
| **Dussehra** | SEASONAL | 15 | -1.6534% | 26.7% | [-3.33%, +0.04%] | -0.1644% | 46.7% | [-0.97%, +0.67%] | -0.49 |
| **Holi** | SEASONAL | 14 | -1.0558% | 42.9% | [-3.52%, +1.04%] | -0.1938% | 57.1% | [-1.62%, +1.16%] | -0.23 |


---

## Key Research Discoveries

1. **Pre-Event Drift Dominance (Diwali)**:
   - **Diwali** produces the single highest pre-event price appreciation: **+1.8029% Pre-10D mean (73.3% Win Rate)** with a 95% Bootstrap Confidence Interval of **[+0.18%, +3.45%]**.

2. **Post-Event Relief Dominance (Union Budget)**:
   - **Union Budget** produces the single highest immediate post-event relief rally: **+1.1836% Post-3D mean (78.6% Win Rate)** with a 95% Bootstrap Confidence Interval of **[-0.38%, +2.78%]**.

---

## Data Provenance
- Oracle Table: `STAGING.META_STUDY_M001`
- Governance Table: `STAGING.RESEARCH_EXECUTIONS` (Study ID: `META-2026-M001`)
- Git Commit: `a4b7f92e8c10d3`
