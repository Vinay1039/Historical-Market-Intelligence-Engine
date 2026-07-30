# HMIE Research Compendium v2.0 (Final Release)
## Governed Canonical Empirical Studies & Synthesis (2011–2026)

**Engine Version**: HMIE Core v1.5.0  
**Governance Layer**: v2.1 (Dual-Hash Cryptographic Registry & Single Canonical Policy)  
**Dataset Version**: `v2.0.0` (856 symbols, 118,229 monthly bars, 180 months)  
**Git Commit**: `a4b7f92e8c10d3`  
**Date**: 2026-07-30  
**Status**: ARCHITECTURALLY FROZEN, GOVERNED & PUBLISHED

---

## Executive Summary

The **Historical Market Intelligence Engine (HMIE)** has established a governed empirical research platform for Indian equity markets comprising **16 Governed Canonical Executions** registered in Oracle (`STAGING.RESEARCH_EXECUTIONS`) across four distinct research programs:
1. **Momentum Research Suite (HMIE v1.1)**: 5 Studies (`MOMENTUM-2026-001` to `004`)
2. **Festival Research Suite (HMIE v1.2)**: 4 Studies (`FESTIVAL-2026-F001` to `F004`)
3. **Union Budget Research Suite (HMIE v1.3)**: 4 Studies (`BUDGET-2026-B001` to `B004`)
4. **Meta-Research & Synthesis Suite (HMIE v1.4)**: 3 Studies (`META-2026-M001` to `M003`)

---

## Complete Canonical Study Registry

| Exec ID | Study ID | Suite | Methodology | Dataset | Primary Empirical Observation | Execution Hash | Result Hash | Status |
|:---:|---|---|:---:|:---:|---|:---:|:---:|:---:|
| 1 | `MOMENTUM-2026-001` | Momentum | v1.5.0 | v2.0.0 | Strategy performance is robust across history gates (CAGR spread 3.11%). Unrounded turnover remains invariant (~39.6%). | `aef0fcffecff...` | `2ea7b5ea8a0e...` | Canonical ✅ |
| 2 | `MOMENTUM-2026-002` | Momentum | v1.5.0 | v2.0.0 | Monotonic turnover decay observed (54.5% -> 28.9%). 12M lookback exhibits highest Sharpe (1.00) in sample. | `e1ddcff71dbd...` | `a4d33ebc83eb...` | Canonical ✅ |
| 3 | `MOMENTUM-2026-002A` | Momentum | v1.5.0 | v2.0.0 | Positive active alpha coincides across all 3 macro sub-periods (+13.38%, +15.79%, +23.54%). | `959faedcaebd...` | `6da9aebc198f...` | Canonical ✅ |
| 4 | `MOMENTUM-2026-003` | Momentum | v1.5.0 | v2.0.0 | Top 95.0% (29 stocks) marks the concentration sweet spot in sample (Sharpe 1.00). | `b00ebcd194e1...` | `de5c5f49d37a...` | Canonical ✅ |
| 5 | `MOMENTUM-2026-004` | Momentum | v1.5.0 | v2.0.0 | Retail discount net CAGR = +31.26%. Remains economically viable under 50 bps slippage (+10.51% net alpha). | `8eb51d6bc107...` | `eda1f28b491a...` | Canonical ✅ |
| 6 | `FESTIVAL-2026-F001` | Festival | v1.0.0 | v2.0.0 | Pre-Diwali T-10 exhibits positive mean drift (+1.80%, 73.3% Win Rate) in sample; post-Diwali returns mean-revert. | `8ab6f89bc341...` | `347eb1ed3210...` | Canonical ✅ |
| 7 | `FESTIVAL-2026-F002` | Festival | v1.0.0 | v2.0.0 | Pre-event positive drift is selective to Diwali (+1.80%) & Ganesh (+1.32%). Holi coincides with negative drift (-1.06%). | `b15154e13e40...` | `76cfb4358e12...` | Canonical ✅ |
| 8 | `FESTIVAL-2026-F003` | Festival | v1.0.0 | v2.0.0 | Domestic demand sectors (Auto +4.50%, Banking +3.52%) exhibit stronger pre-Diwali drift than IT (+0.46%) in sample. | `6fc8e5154320...` | `a7c071d3c789...` | Canonical ✅ |
| 9 | `FESTIVAL-2026-F004` | Festival | v1.0.0 | v2.0.0 | Pre-Diwali drift is highest in Bull regimes (+2.69%) and most consistent during Sideways regimes (85.7% Win Rate). | `8dced61e7910...` | `e31eebe02e45...` | Canonical ✅ |
| 10 | `BUDGET-2026-B001` | Budget | v1.0.0 | v2.0.0 | Pre-Budget caution (-0.59% T-5) is followed by T+3 relief rally (+1.18% mean, 78.6% Win Rate) in sample. | `4e116054d789...` | `8dece9fa2e10...` | Canonical ✅ |
| 11 | `BUDGET-2026-B002` | Budget | v1.0.0 | v2.0.0 | Auto exhibits the strongest clean post-Budget relief (+3.70%, 85.7% Win Rate) alongside Banking (+1.63%). | `4e0f6ecddc12...` | `acd59c62b456...` | Canonical ✅ |
| 12 | `BUDGET-2026-B003` | Budget | v1.0.0 | v2.0.0 | Sideways regimes coincide with the highest post-Budget relief consistency (85.7% Win Rate) in sample. | `c0dfc94a5901...` | `1a3190cdd876...` | Canonical ✅ |
| 13 | `BUDGET-2026-B004` | Budget | v1.0.0 | v2.0.0 | Expansionary Budgets in this sample coincide with stronger post-Budget relief (+2.96%, 80.0% Win Rate) than Tightening (-0.21%). | `8791202f9345...` | `8f8743306890...` | Canonical ✅ |
| 14 | `META-2026-M001` | Meta | v1.0.0 | v2.0.0 | 95% Bootstrap CIs for Diwali (+1.80%, CI [+0.22%, +3.40%]) and Ganesh (+1.32%, CI [+0.12%, +2.62%]) exclude zero in sample. | `800a6b925512...` | `0d40c1c5bd34...` | Canonical ✅ |
| 15 | `META-2026-M002` | Meta | v1.0.0 | v2.0.0 | Classifies sectors into HIGHLY_RESPONSIVE_DUAL (Auto, Banking) vs DEFENSIVE_DETACHED (IT) via objective win-rate rules. | `0336e3cf0678...` | `826c993c2e12...` | Canonical ✅ |
| 16 | `META-2026-M003` | Meta | v1.0.0 | v2.0.0 | Sideways consolidation consistently coincides with 85.7% event relief win rates across both Festival and Budget domains. | `e573b0920134...` | `025141791456...` | Canonical ✅ |

---

## Domain Ontologies & Meta-Syntheses

1. **Event Archetype Taxonomy**:
   - **Seasonal Accumulation Archetype** (Diwali, Ganesh Chaturthi): Characterized by pre-event positive accumulation drift, moderate effect size, and statistically non-zero 95% Bootstrap CIs.
   - **Policy Uncertainty Resolution Archetype** (Union Budget): Characterized by pre-event caution/de-risking followed by immediate short-term post-event relief rally ($T_{+3}$ Win Rate 78.6%).

2. **Sector Sensitivity Ontology**:
   - **`HIGHLY_RESPONSIVE_DUAL`** (Auto, Banking): High win rate consistency ($\ge 73\%$) across both seasonal festive demand and policy relief events.
   - **`DEFENSIVE_DETACHED`** (IT): Low responsiveness across domestic events due to export-oriented revenue streams.

3. **Macro Regime Resolution**:
   - **Sideways Consolidation** is the most consistent regime state for event resolution, coinciding with **85.7% win rate consistency** across both Festival and Budget domains.
   - **Factor Momentum Investing** is macro-resilient, generating positive active alpha (+13.38% to +23.54%) across all observed market regimes.

---
*HMIE Research Compendium v2.0 Final Release Published & Locked.*
