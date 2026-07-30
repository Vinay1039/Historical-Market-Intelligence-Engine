# HMIE Research Compendium v1.0
## Governed Canonical Empirical Studies (2011–2026)

**Engine Version**: HMIE Core v1.5.0  
**Governance Layer**: v2.1 (Dual-Hash & Single Canonical Policy)  
**Dataset Version**: `v2.0.0` (856 symbols, 118,229 monthly bars, 180 months)  
**Date**: 2026-07-30  
**Status**: ARCHITECTURE FROZEN & GOVERNED

---

## Executive Summary

The **Historical Market Intelligence Engine (HMIE)** has completed two primary empirical research programs comprising **9 Governed Canonical Executions** registered in `STAGING.RESEARCH_EXECUTIONS`:
- **Momentum Research Suite (HMIE v1.1)**: 5 Studies (`MOMENTUM-2026-001` to `004`)
- **Festival Research Suite (HMIE v1.2)**: 4 Studies (`FESTIVAL-2026-F001` to `F004`)

Every study in this compendium enforces **Immutable Git Commit Pinning** (`a4b7f92e8c10d3`), **Dual-Hash Cryptographic Tracking** (`EXECUTION_HASH` + `RESULT_HASH`), and **Explicit Statistical Limitations**.

---

## Part I: Momentum Research Suite (HMIE v1.1)

### Study 001: Eligibility Threshold Sensitivity Analysis
- **Study ID**: `MOMENTUM-2026-001` | **Exec ID**: `1`
- **Research Question**: Is `TOP_STOCK_MOMENTUM_95P` robust to the minimum history threshold?
- **Parameters**: Minimum history $H \in \{36, 48, 60\}$ months; 6M lookback; Top 95th percentile cut; 120 traded months.
- **Empirical Findings**:
  - Strategy performance is robust across eligibility gates (CAGR: 26.53% [36M], 23.42% [48M], 24.82% [60M]; CAGR spread = 3.11%).
  - Unrounded monthly turnover is invariant (~39.60%).
- **Limitations**: 36-month threshold admits IPOs with shorter trading histories; equal-weighting without single-stock liquidity caps.
- **Hashes**: `EXEC: aef0fcffecff...` | `RESULT: 2ea7b5ea8a0e...`

### Study 002: Trailing Lookback Sensitivity Analysis
- **Study ID**: `MOMENTUM-2026-002` | **Exec ID**: `2`
- **Research Question**: How does trailing lookback duration (3M, 6M, 9M, 12M) impact return, turnover, and fee tolerance?
- **Parameters**: Lookback $L \in \{3, 6, 9, 12\}$ months; 60M min history; Top 95th percentile cut; 120 traded months.
- **Empirical Findings**:
  - Monotonic turnover decay: $54.5\% (3M) \rightarrow 39.6\% (6M) \rightarrow 32.7\% (9M) \rightarrow 28.9\% (12M)$.
  - 12M lookback yields highest Sharpe (1.00) and Break-Even Fee tolerance (1.3583%).
- **Limitations**: Monthly rebalance frequency; gross returns exclude bid-ask spread friction.
- **Hashes**: `EXEC: e1ddcff71dbd...` | `RESULT: a4d33ebc83eb...`

### Study 002A: Sub-Period Regime Stability Analysis
- **Study ID**: `MOMENTUM-2026-002A` | **Exec ID**: `3`
- **Research Question**: Does 12-month momentum generate positive active alpha across distinct historical macro regimes?
- **Regimes Evaluated**:
  - Regime 1 (2011–2015): Strat CAGR +18.23% vs Bench +4.85% (Alpha: **+13.38%**, Turnover: 31.9%)
  - Regime 2 (2016–2020): Strat CAGR +27.97% vs Bench +12.18% (Alpha: **+15.79%**, Turnover: 29.2%)
  - Regime 3 (2021–2026): Strat CAGR +38.16% vs Bench +14.62% (Alpha: **+23.54%**, Turnover: 28.7%)
- **Empirical Findings**: Positive active alpha generated across all three macro sub-periods; monthly turnover remains bounded (28.7%–31.9%).
- **Limitations**: Regime 1 sample constrained by early warehouse history; regime boundaries are macro-heuristic divisions.
- **Hashes**: `EXEC: 959faedcaebd...` | `RESULT: 6da9aebc198f...`

### Study 003: Selection Threshold Sensitivity Analysis
- **Study ID**: `MOMENTUM-2026-003` | **Exec ID**: `4`
- **Research Question**: Does higher portfolio concentration (Top 85% to 97.5%) increase return or inflate risk?
- **Parameters**: Percentile cut $P \in \{85.0\%, 90.0\%, 92.5\%, 95.0\%, 97.5\%\}$; 12M lookback; 60M min history.
- **Empirical Findings**:
  - Non-monotonic risk-adjusted curve: Sharpe expands from 0.74 (85%) up to 1.00 (95%), but degrades to 0.81 at 97.5% due to single-stock concentration risk.
  - **Optimal Frontier**: Top 95.0% (29 stocks) is the concentration sweet spot.
- **Limitations**: Top 97.5% yields small basket sizes (~15 stocks), increasing idiosyncratic variance.
- **Hashes**: `EXEC: 0bff9e9c7c...` | `RESULT: a58710bc67...`

### Study 004: Implementation Robustness & Friction Tolerance Analysis
- **Study ID**: `MOMENTUM-2026-004` | **Exec ID**: `5`
- **Research Question**: Under what real-world friction assumptions (STT, brokerage, exchange charges, GST, stamp duty, slippage) does the strategy remain viable?
- **Tiers Evaluated**: T0 (Gross 0%), T1 (Inst 0.12%), T2 (Retail 0.18%), T3 (Low 0.28%), T4 (Mid 0.43%), T5 (Stress 0.68%).
- **Empirical Findings**:
  - Retail discount rate (**T2: 0.18% per trade**): Net CAGR = **+31.26%**, Net Alpha = **+18.13%**, Net Sharpe = **0.96**.
  - Economically viable up to extreme stress levels (**T5: 0.68% per trade**, roundtrip 1.36%) with **+13.78% net alpha**.
- **Limitations**: Market impact modeled linearly; turnover drag modeled symmetrically.
- **Hashes**: `EXEC: 8eb51d6bc1...` | `RESULT: 7a08cb95d1...`

---

## Part II: Festival Research Suite (HMIE v1.2)

### Study F001: Event Window Analysis — Diwali Muhurat Drift
- **Study ID**: `FESTIVAL-2026-F001` | **Exec ID**: `6`
- **Research Question**: Is there a pre- or post-festival price drift around Diwali Muhurat trading?
- **Parameters**: 15 annual Diwali events (2011–2025); relative windows $T_{-20}$ to $T_{+20}$; NIFTY50 proxy.
- **Empirical Findings**:
  - Pre-Diwali drift ($T_{-10}$ to $T_{-1}$): Positive mean return (+1.8029%, **73.3% Win Rate**).
  - Post-Diwali normalization ($T_{+10}$): Mean reversion occurs with win rate dropping to 53.3%.
- **Limitations**: Evaluates NIFTY50 proxy; sample size constrained to 15 events.
- **Hashes**: `EXEC: 8ab6f89bc3...` | `RESULT: 347eb1ed32...`

### Study F002: Cross-Festival Seasonality Matrix
- **Study ID**: `FESTIVAL-2026-F002` | **Exec ID**: `7`
- **Research Question**: Does pre-festival price drift exhibit uniform seasonality across major Indian cultural holidays?
- **Festivals Evaluated**: Diwali, Dussehra, Ganesh Chaturthi, Holi, Ugadi.
- **Empirical Findings**:
  - Pre-festival drift is selective to Diwali (+1.8029%, 73.3% Win Rate) and Ganesh Chaturthi (+1.3154%, 60.0% Win Rate).
  - Holi exhibits negative pre-event drift (-1.0558%, 42.9% Win Rate), reflecting March fiscal year-end profit booking and tax-loss selling.
- **Limitations**: Evaluates broad NIFTY50 index; individual stock liquidity variations excluded.
- **Hashes**: `EXEC: b15154e13e...` | `RESULT: 76cfb4358e...`

### Study F003: Sector-Wise Festival Effects Analysis (Diwali)
- **Study ID**: `FESTIVAL-2026-F003` | **Exec ID**: `8`
- **Research Question**: Does festive price appreciation during Diwali diverge by economic sector?
- **Sectors Evaluated**: Auto, Banking, FMCG, IT, Energy.
- **Empirical Findings**:
  - Domestic demand sectors lead: **Auto** (+4.5015% Pre-10D mean, 73.3% Win Rate) and **Banking** (+3.5163% Pre-10D mean, **80.0% Win Rate**).
  - Export sector (**IT**) lags significantly (+0.4579%, 53.3% Win Rate), confirming pre-Diwali drift is driven by domestic demand.
- **Limitations**: Sectors modeled via representative stock proxy baskets.
- **Hashes**: `EXEC: 6fc8e51543...` | `RESULT: a7c071d3c7...`

### Study F004: Market Regime Interaction Analysis (Diwali)
- **Study ID**: `FESTIVAL-2026-F004` | **Exec ID**: `9`
- **Research Question**: Does pre-Diwali price drift depend on the prevailing 60-day market trend state (Bull, Sideways, Bear)?
- **Regimes Evaluated**:
  - Bull (60D Return > +5%): 5 events — Pre-10D Mean: **+2.6861%** (60.0% Win Rate)
  - Sideways (-5% to +5%): 7 events — Pre-10D Mean: **+2.1899%** (**85.7% Win Rate**)
  - Bear (60D Return < -5%): 3 events — Pre-10D Mean: **-0.5721%** (66.7% Win Rate)
- **Empirical Findings**: Pre-Diwali drift is highest in Bull markets (+2.69%) and most consistent in Sideways markets (85.7% Win Rate), but breaks down in Bear markets (-0.57%).
- **Limitations**: Bear market subset is small (3 events); exploratory interpretation required.
- **Hashes**: `EXEC: 8dced61e79...` | `RESULT: e31eebe02e...`

---

## Governance Summary Table

| Exec ID | Study ID | Suite | Methodology | Dataset | Execution Hash | Result Hash | Status |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | `MOMENTUM-2026-001` | Momentum | v1.5.0 | v2.0.0 | `aef0fcffecff...` | `2ea7b5ea8a0e...` | Canonical ✅ |
| 2 | `MOMENTUM-2026-002` | Momentum | v1.5.0 | v2.0.0 | `e1ddcff71dbd...` | `a4d33ebc83eb...` | Canonical ✅ |
| 3 | `MOMENTUM-2026-002A` | Momentum | v1.5.0 | v2.0.0 | `959faedcaebd...` | `6da9aebc198f...` | Canonical ✅ |
| 4 | `MOMENTUM-2026-003` | Momentum | v1.5.0 | v2.0.0 | `b00ebcd194e1...` | `de5c5f49d37a...` | Canonical ✅ |
| 5 | `MOMENTUM-2026-004` | Momentum | v1.5.0 | v2.0.0 | `8eb51d6bc107...` | `eda1f28b491a...` | Canonical ✅ |
| 6 | `FESTIVAL-2026-F001` | Festival | v1.0.0 | v2.0.0 | `8ab6f89bc341...` | `347eb1ed3210...` | Canonical ✅ |
| 7 | `FESTIVAL-2026-F002` | Festival | v1.0.0 | v2.0.0 | `b15154e13e40...` | `76cfb4358e12...` | Canonical ✅ |
| 8 | `FESTIVAL-2026-F003` | Festival | v1.0.0 | v2.0.0 | `6fc8e5154320...` | `a7c071d3c789...` | Canonical ✅ |
| 9 | `FESTIVAL-2026-F004` | Festival | v1.0.0 | v2.0.0 | `8dced61e7910...` | `e31eebe02e45...` | Canonical ✅ |

---
*HMIE Research Compendium v1.0 Published & Locked.*
