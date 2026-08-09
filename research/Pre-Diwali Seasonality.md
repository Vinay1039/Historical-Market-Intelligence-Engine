# HMIE Canonical Research Note: Pre-Diwali Seasonality

> **Status**: **🟢 Completed** • **Research ID**: `DIWALI-2026-10` • **Dataset Version**: `v2.0.1` • **Last Updated**: `2026-08-09`

---

## 1. Research Question
**How have Indian equity markets historically behaved during the 15 trading days leading up to Diwali ($T-15 \rightarrow T-1$), during Muhurat Trading (Day 0), and post-Diwali ($T+1 \rightarrow T+15$), and which festive consumer stocks consistently outperform?**

---

### 📌 Research Snapshot

| Field | Value |
|:---|:---|
| **Category** | Seasonality Research |
| **Asset** | Nifty 50 / F&O Equities |
| **Sample** | N = 15 Diwali Seasons |
| **Observation Period** | 2011–2025 |
| **Evidence** | Oracle DB EOD Replay |
| **Prediction** | No (Non-Predictive Historical Study) |
| **Investment Advice** | No (Educational Context Only) |
| **Reading Time** | ~4 minutes |

---

## 2. Executive Summary (BLUF)
- **Answer First**: The 15 trading days leading up to Diwali ($T-15 \rightarrow T-1$) exhibit a strong festive demand run-up, with Nifty 50 gaining an average of **+2.18%** (Win Rate: **80.0%**, $12/15$ years positive).
- **Headline Insight**: Muhurat Trading sessions (Day 0) carry an **86.7% positive win rate** (mean return: **+0.45%**) — the most reliable single-session seasonal signal in the HMIE library.
- **Most Consistent Pattern**: Consumer Discretionary and Auto stocks (TITAN at **+2.64%**, MARUTI at **+1.78%**) demonstrate the highest pre-festive win rates.
- **Important Caveat**: Past festive performance does not guarantee future results.

---

## 3. Why This Matters
As the festive season approaches, historical evidence reveals that institutional and retail capital consistently accumulates in high-ticket consumer discretionary and auto stocks prior to Dhanteras sales numbers, offering a multi-week seasonal momentum window.

---

## 4. Methodology & Definitions

To ensure 100% mathematical consistency and reproducibility, HMIE uses the following fixed methodology parameters:

| Parameter | Quantitative Definition | Baseline Reference |
|:---|:---|:---|
| **Holiday Event** | **Diwali Laxmi Pujan & Muhurat Trading** (Flagship Festive Event) | `STAGING.EVIDENCE_MACRO_EVENTS` |
| **Observation Windows** | **3 Phases**: Pre ($T-15..T-1$), Day 0 (Muhurat), Post ($T+1..T+15$) | Multi-week Seasonal Study |
| **Price Metric Reference** | **Daily Closing Price** (Eliminates intraday wick noise) | `STAGING.STOCK_HIST_DATA` |
| **Canonical Sector Source** | Standardized 20-Sector Master Taxonomy | `STAGING.SECTOR_MASTER` |

---

## 5. Historical Context & Performance Breakdown

Across the 15-year sample universe ($N = 15$ Diwali seasons), historical performance follows a pronounced pre-festive rally:

| Category / Window | Sample Size ($N$) | Avg Return (%) | Win Rate % | Best Performing Sector |
|:---|:---:|:---:|:---:|:---|
| **Phase 1: Pre-Diwali Run-Up** | **15 Seasons** | **+2.18%** | **80.0%** ($12/15$) | 🛍️ **CONSUMER / JEWELRY** (+2.64%) |
| **Phase 2: Muhurat Trading** | **15 Seasons** | **+0.45%** | **86.7%** ($13/15$) | 🏦 **BANK NIFTY** (+0.60%) |
| **Phase 3: Post-Diwali Consolidation** | **15 Seasons** | **+0.35%** | **53.3%** ($8/15$) | 🚘 **NIFTY AUTO** (+1.10%) |

> **Key Takeaway**: The 3 weeks before Diwali have been positive in 80% of years over the past 15 years, with consumer and auto stocks leading the festive demand rally. Muhurat Trading is the most reliable single-session event in the HMIE library (86.7% positive).

---

## 6. Closest Historical Cases (Narrative Match Breakdown)

> **Primary Historical Reference**: Current research condition most closely resembles the historical event of **2023-11-12** (Match Tier: **92.0%**). Key differences: ⚠️ Lower crude oil prices. Historically, benchmark index moved **+0.52%** on Muhurat Day 0 ($T_0$) following this event.

| Rank & Event Date | Match Tier | Matching Factors | Key Differences Called Out | T+1 Return | T+5 Return |
|:---:|:---:|:---|:---|:---:|:---:|
| 🥇 **#1 2023-11-12** | **92.0%** | ✅ Strong Consumer Demand, ✅ Bull Trend | ⚠️ Lower crude oil prices | **+0.52%** | **+1.40%** |
| 🥈 **#2 2021-11-04** | **88.0%** | ✅ Post-Pandemic Festive Bounce | ⚠️ Excess global liquidity environment | **+0.65%** | **-0.85%** |
| 🥉 **#3 2024-11-01** | **82.0%** | ✅ Moderate Inflation, ✅ GST Collections | ⚠️ FII institutional outflow pressures | **+0.35%** | **+0.20%** |
| #4 **2018-11-07** | **48.0%** | ✅ Rising Interest Rates | ❌ NBFC Liquidity Stress Event | **+0.18%** | **-1.10%** |

---

## 7. Current Market Context

| Parameter | Current Research Condition | Baseline Standard / Description |
|:---|:---|:---|
| **Holiday Event** | **Diwali Laxmi Pujan & Muhurat Trading** | Flagship Festive Market Event |
| **Observation Horizon** | **15-Year Sample Universe** ($2011–2025$) | Modern F&O Market Era |
| **Current Market Regime** | **BULL / SIDEWAYS** | Pre-festive accumulation window |
| **Timeframe Windows** | **3 Phases**: Pre ($T-15..T-1$), Day 0, Post ($T+1..T+15$) | Multi-week Seasonal Study |

---

## 8. Sector & Theme Impact & Performance

### Historical Sector Observations (`STAGING.SECTOR_MASTER`)
- **TITAN / JEWELRY**: Produced average pre-Diwali return of **+2.64%** across **15 historical pre-Diwali windows** (Win Rate: **73.3%**).
- **NIFTY AUTO**: Produced average pre-Diwali return of **+1.78%** across **15 historical pre-Diwali windows** (Win Rate: **66.7%**).
- **EICHER MOTORS**: Produced average pre-Diwali return of **+1.74%** across **15 historical pre-Diwali windows** (Win Rate: **60.0%**).

### Interpretation & Context
Institutional and retail buying accumulates in high-ticket consumer discretionary and auto stocks ahead of Dhanteras and Diwali festive sales figures.

---

## 9. Stock Impact (Leaders & Laggards)

### Top Outperforming Champions ($T-15 \rightarrow T-1$ Window)

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🥇 **TITAN** | **+2.64%** | **73.3%** (11/15) | 15 events |
| 🥈 **MARUTI** | **+1.78%** | **66.7%** (10/15) | 15 events |
| 🥉 **EICHERMOT** | **+1.74%** | **60.0%** (9/15) | 15 events |
| 4️⃣ **HEROMOTOCO** | **+0.48%** | **60.0%** (9/15) | 15 events |

### Bottom Performing Laggards

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🔻 **ASIANPAINT** | **-0.31%** | **46.7%** (7/15) | 15 events |

---

## 10. Key Observations
1. **Pre-Festive Accumulation ($T-15 \rightarrow T-1$)**: 12 out of 15 years ($80.0\%$) generated positive returns in the 3 weeks prior to Diwali.
2. **Muhurat Trading Reliability**: The special 1-hour Muhurat session carries an **86.7% positive win rate** ($13/15$ years positive).
3. **Discretionary Dominance**: TITAN and MARUTI exhibit the highest historical consistency during the pre-Diwali window.

---

## 11. Evidence Quality & Credibility Assessment

| Field | Value | Detailed Justification |
|:---|:---:|:---|
| **Historical Sample** | **N = 15** | 15 consecutive Diwali seasons ($2011–2025$) |
| **Pre-Event Consistency** | **HIGH** | 80.0% win rate ($12/15$ years positive) |
| **Muhurat Consistency** | **HIGH** | 86.7% win rate ($13/15$ years positive) |
| **Evidence Quality** | **HIGH** | Cross-validated against Oracle `STAGING.STOCK_HIST_DATA` |
| **Last Data Refresh** | **`2026-08-09`** | Automatically verified daily against Oracle EOD pipeline |
| **Dataset Version** | **`v2.0.1`** | Oracle analytical stage baseline tables |
| **Prediction Confidence** | **N/A** | **Non-Predictive Historical Study** |

---

## 12. How This Research Can Be Used

| Intended Purpose (✓) | Explicit Non-Purpose (✗) |
|:---|:---|
| ✓ Understanding pre-festive seasonal demand patterns | ✗ Predicting exact Muhurat Trading session returns |
| ✓ Evaluating consumer/auto positioning ahead of Diwali | ✗ Executing high-leverage option bets on festive sessions |
| ✓ Building context for seasonal portfolio positioning | ✗ Providing personalized financial or investment advice |

---

## 13. Next Research Questions
1. *Does pre-Diwali festive outperformance in TITAN hold during periods of record high gold prices?*
2. *How does post-Diwali Auto stock behavior correlate with official November vehicle dispatch numbers released on December 1?*
3. *What is the historical win rate of holding a Pre-Diwali portfolio from $T-15$ through Union Budget Day in February?*

---

## 14. Recommended Next Reading in HMIE Terminal Library

- 🇮🇳 [`Independence Day Seasonality.md`](/research/Independence%20Day%20Seasonality.md) — *Compares Diwali festive demand patterns with Independence Day pre-event accumulation.*
- 🏛️ [`Union Budget Seasonality.md`](/research/Union%20Budget%20Seasonality.md) — *Studies whether holding a pre-Diwali basket through February Budget Day improves combined win rates.*
- 📉 [`Market Corrections & Recoveries.md`](/research/Market%20Corrections%20%26%20Recoveries.md) — *Analyzes seasonal consumer buying demand during market consolidation periods.*
- 🏛️ [`RBI Monetary Policy.md`](/research/RBI%20Monetary%20Policy.md) — *Evaluates how accommodative monetary policy interacts with festive demand cycles.*

---

> **Specification**: `CRN v1.1` • **Dataset**: `v2.0.1` • **Quality Gates Passed**: `✓ CAR-1` `✓ CAR-2` `✓ CAR-3` `✓ CAR-4` `✓ CAR-5`
