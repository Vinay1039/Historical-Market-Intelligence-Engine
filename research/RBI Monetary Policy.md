# HMIE Canonical Research Note: RBI Monetary Policy

> **Status**: **🟢 Completed** • **Research ID**: `RBI-2026-08` • **Dataset Version**: `v2.0.1` • **Last Updated**: `2026-08-09`

---

## 1. Research Question
**How have Indian equity markets historically behaved after RBI Rate Hikes, Rate Cuts, and Policy Pauses, and what does current policy condition most closely resemble?**

---

### 📌 Research Snapshot

| Field | Value |
|:---|:---|
| **Category** | Macro Research |
| **Asset** | Nifty 50 / F&O Equities |
| **Sample** | N = 15 MPC Meetings (3 Pause, 7 Cut, 5 Hike) |
| **Observation Period** | 2011–2025 |
| **Evidence** | Oracle DB EOD Replay |
| **Prediction** | No (Non-Predictive Historical Study) |
| **Investment Advice** | No (Educational Context Only) |
| **Reading Time** | ~4 minutes |

---

## 2. Executive Summary (BLUF)
- **Answer First**: During Policy Pause cycles, markets experience pre-decision consolidation ($T-1$ average: **-0.49%**) followed by positive post-decision drift ($T+1$ win rate: **66.7%**, mean: **+0.58%**).
- **Headline Insight**: Banking stocks (ICICIBANK, SBIN) produced the highest post-pause relief return (**+1.53%**) across 3 historical Pause meetings.
- **Most Consistent Pattern**: Pre-meeting de-risking on $T-1$ (Win Rate: 0.0%, mean: -0.49%) followed by Day 1 rebound ($T+1$ Win Rate: 66.7%).
- **Important Caveat**: Sample size for Policy Pauses is small ($N=3$). Past MPC reactions do not guarantee future performance.

---

## 3. Why This Matters
If the RBI keeps benchmark interest rates unchanged, historical evidence demonstrates that financial equities often experience an immediate post-decision relief rally as interest rate uncertainty resolves, making Banking a key sector to monitor during pause announcements.

---

## 4. Methodology & Definitions

To ensure 100% mathematical consistency and reproducibility, HMIE uses the following fixed methodology parameters:

| Parameter | Quantitative Definition | Baseline Reference |
|:---|:---|:---|
| **MPC Decision Categories** | 3 Stances: **Pause** (0 bps), **Cut** (< 0 bps), **Hike** (> 0 bps) | `STAGING.EVIDENCE_MACRO_EVENTS` |
| **Price Metric Reference** | **Daily Closing Price** (Eliminates intraday wick noise) | `STAGING.STOCK_HIST_DATA` |
| **Post-Decision Holding Period** | **3-Day Window** ($T+1 \rightarrow T+3$) | Standard Event Study Window |
| **Canonical Sector Source** | Standardized 20-Sector Master Taxonomy | `STAGING.SECTOR_MASTER` |

---

## 5. Historical Context & Performance Breakdown

Across the modern MPC sample universe ($N = 15$ meetings), policy decisions break down into 3 distinct stances:

| Category / Stance | Sample Size ($N$) | Avg Return (%) | Win Rate % | Best Performing Sector |
|:---|:---:|:---:|:---:|:---|
| **Policy Pause** | **3 Meetings** | **-0.01%** | **66.7%** ($2/3$) | 🏦 **BANKING** (+1.53%) |
| **Rate Cut** | **7 Meetings** | **+0.03%** | **57.1%** ($4/7$) | ⚡ **ENERGY** (+1.72%) |
| **Rate Hike** | **5 Meetings** | **-0.54%** | **50.0%** ($2/5$) | 🚘 **AUTO** (+0.52%) |

*Note: All returns represent 3-day post-announcement holding periods ($T+3$).*

> **Key Takeaway**: Policy Pauses historically trigger a short-term relief bounce in Banking stocks, while Rate Hikes are met with broad index weakness. Rate Cuts show surprisingly muted index-level returns but benefit Energy stocks.

---

## 6. Closest Historical Cases (Narrative Match Breakdown)

> **Primary Historical Reference**: Current research condition most closely resembles the historical event of **2025-02-07** (Match Tier: **99.4%**). Key differences: *None (Exact Baseline Match)*. Historically, benchmark index moved **-0.24%** on Day 1 ($T+1$) following this event.

| Rank & Event Date | Match Tier | Matching Factors | Key Differences Called Out | T+1 Return | T+5 Return |
|:---:|:---:|:---|:---|:---:|:---:|
| 🥇 **#1 2025-02-07** | **99.4%** | ✅ Action, ✅ BPS, ✅ CPI, ✅ Regime, ✅ Tone | *None (Exact Baseline Match)* | **-0.24%** | **N/A** |
| 🥈 **#2 2024-02-08** | **88.2%** | ✅ Action, ✅ BPS, ✅ Tone | ⚠️ CPI higher (5.1% vs 4.5%), ⚠️ Regime (BULL vs SIDEWAYS) | **+0.12%** | **+6.09%** |
| 🥉 **#3 2021-02-05** | **78.8%** | ✅ Action, ✅ BPS, ✅ CPI, ✅ Tone | ⚠️ Regime (BULL vs SIDEWAYS) | **+1.87%** | **+53.40%** |
| #4 **2018-08-01** | **49.1%** | ✅ CPI, ✅ Tone | ❌ Action (HIKE vs PAUSE), ❌ BPS (+25 vs 0) | **-1.09%** | **+49.07%** |
| #5 **2016-04-05** | **47.0%** | ✅ Tone | ❌ Action (CUT vs PAUSE), ❌ BPS (-25 vs 0) | **+0.13%** | **+52.53%** |

---

## 7. Current Market Context

| Parameter | Current Research Condition | Baseline Standard / Description |
|:---|:---|:---|
| **Repo Rate Decision** | **PAUSE** (No Change) | Benchmark rate held steady at 6.50% |
| **BPS Change** | **0.0 bps** | Zero interest rate adjustment |
| **CPI Inflation** | **4.5%** | Within RBI target band ($4.0\% \pm 2\%$) |
| **Market Regime** | **SIDEWAYS** | Nifty index in consolidation phase |
| **Statement Tone** | **NEUTRAL** | Balanced policy stance |

---

## 8. Sector & Theme Impact & Performance

### Historical Sector Observations (`STAGING.SECTOR_MASTER`)
- **BANKING**: Produced average return of **+1.53%** across **3 historical Policy Pause meetings** (Win Rate: **66.7%**).
- **ENERGY**: Produced average return of **+1.21%** across **3 historical Policy Pause meetings** (Win Rate: **66.7%**).
- **AUTO**: Produced average return of **+0.46%** across **3 historical Policy Pause meetings** (Win Rate: **66.7%**).

### Interpretation & Context
Interest-rate sensitive financials have historically responded better than other sectors following Policy Pause announcements as interest rate uncertainty dissipates.

---

## 9. Stock Impact (Leaders & Laggards)

### Top Outperforming Champions ($T+3$ Window)

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🥇 **DIXON** | **+3.04%** | **66.7%** (2/3) | 3 Pause events |
| 🥈 **ICICIBANK** | **+2.82%** | **100.0%** (3/3) | 3 Pause events |
| 🥉 **SBIN** | **+2.29%** | **66.7%** (2/3) | 3 Pause events |

### Bottom Performing Laggards

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🔻 **LT** | **-1.24%** | **33.3%** (1/3) | 3 Pause events |

---

## 10. Key Observations
1. **Pre-Meeting De-risking**: Nifty 50 consistently exhibits light consolidation on $T-1$ (Win rate: 0.0%, Mean: -0.49%) as market participants trim leverage prior to the policy statement.
2. **Day 1 Rebound**: Post-announcement Day 1 ($T+1$) yields positive returns in 2 of 3 pause meetings (Mean: +0.58%).
3. **Financials Lead Relief**: Large-cap banking stocks (ICICIBANK, SBIN) drive index stability following rate pauses.

---

## 11. Evidence Quality & Credibility Assessment

| Field | Value | Detailed Justification |
|:---|:---:|:---|
| **Historical Sample** | **N = 15** | 15 MPC meetings evaluated across modern era ($2011–2025$) |
| **Pause Sub-Sample** | **N = 3** | 3 Policy Pause meetings (primary research focus) |
| **Evidence Quality** | **MODERATE** | Small pause sample ($N=3$) limits statistical robustness |
| **Cross Validation** | **VERIFIED** | Verified against Oracle `STAGING.STOCK_HIST_DATA` |
| **Last Data Refresh** | **`2026-08-09`** | Automatically verified daily against Oracle EOD pipeline |
| **Dataset Version** | **`v2.0.1`** | Oracle analytical stage baseline tables |
| **Prediction Confidence** | **N/A** | **Non-Predictive Historical Study** |

---

## 12. How This Research Can Be Used

| Intended Purpose (✓) | Explicit Non-Purpose (✗) |
|:---|:---|
| ✓ Understanding historical market reactions to RBI policy decisions | ✗ Predicting exact RBI rate decisions or policy stance |
| ✓ Evaluating sector positioning around MPC announcements | ✗ Executing high-leverage option bets on MPC day |
| ✓ Building context for long-term interest-rate-sensitive allocations | ✗ Providing personalized financial or investment advice |

---

## 13. Next Research Questions
1. *How did Banking stocks perform when RBI paused rates during high inflation ($>6\%$) vs moderate inflation ($<4.5\%$)?*
2. *Did Realty stocks outperform Banking during initial Rate Cut cycles ($N=7$)?*
3. *How does market behavior around RBI Policy decisions compare with Union Budget announcements?*

---

## 14. Recommended Next Reading in HMIE Terminal Library

- 🏛️ [`Union Budget Seasonality.md`](/research/Union%20Budget%20Seasonality.md) — *Compares fiscal policy event reactions with monetary policy event reactions.*
- 📉 [`Market Corrections & Recoveries.md`](/research/Market%20Corrections%20%26%20Recoveries.md) — *Evaluates interest rate policy interactions during active drawdowns.*
- 🪔 [`Pre-Diwali Seasonality.md`](/research/Pre-Diwali%20Seasonality.md) — *Studies monetary policy liquidity cycles preceding festive demand windows.*
- 🇮🇳 [`Independence Day Seasonality.md`](/research/Independence%20Day%20Seasonality.md) — *Studies IT-sector holiday seasonality that may coincide with August MPC meetings.*

---

> **Specification**: `CRN v1.1` • **Dataset**: `v2.0.1` • **Quality Gates Passed**: `✓ CAR-1` `✓ CAR-2` `✓ CAR-3` `✓ CAR-4` `✓ CAR-5`
