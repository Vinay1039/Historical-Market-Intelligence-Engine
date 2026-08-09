# HMIE Canonical Research Note: Union Budget Seasonality

> **Status**: **🟢 Completed** • **Research ID**: `BUDGET-2027-02` • **Dataset Version**: `v2.0.1` • **Last Updated**: `2026-08-09`

---

## 1. Research Question
**How have Indian equity markets historically behaved during pre-budget consolidation windows ($T-10 \rightarrow T-1$), Budget Day sessions, and post-budget policy drift windows ($T+1 \rightarrow T+10$) across 14 annual Union Budgets ($2011–2025$), and which fiscal-sensitive sectors (PSU Banks, Energy, Infra) lead post-budget rallies?**

---

### 📌 Research Snapshot

| Field | Value |
|:---|:---|
| **Category** | Macro Research |
| **Asset** | Nifty 50 / F&O Equities |
| **Sample** | N = 14 Union Budget Announcements |
| **Observation Period** | 2011–2025 |
| **Evidence** | Oracle DB EOD Replay |
| **Prediction** | No (Non-Predictive Historical Study) |
| **Investment Advice** | No (Educational Context Only) |
| **Reading Time** | ~5 minutes |

---

## 2. Executive Summary (BLUF)
- **Answer First**: Union Budgets exhibit a distinct pre-budget de-risking window ($T-10 \rightarrow T-1$), with Nifty 50 declining an average of **-0.85%** (Win Rate: **42.9%**, $6/14$ years positive).
- **Headline Insight**: Post-budget sessions ($T+1 \rightarrow T+10$) deliver positive relief rallies in **64.3% of years** (mean return: **+1.62%**), with PSU Banking (SBIN **+2.19%**) and Energy (RELIANCE **+1.62%**) leading.
- **Most Consistent Pattern**: Pre-budget anxiety creates short-term price dips which are frequently followed by post-budget relief as fiscal clarity emerges.
- **Important Caveat**: Past budget reactions do not guarantee future performance.

---

## 3. Why This Matters
Ahead of February Union Budgets, investors often face heightened volatility and rumors regarding tax or capital gains changes. Quantitative historical evidence reveals that pre-budget anxiety creates short-term price dips ($T-10 \rightarrow T-1$), which are frequently followed by post-budget relief rallies ($T+1 \rightarrow T+10$) as fiscal clarity emerges.

---

## 4. Methodology & Definitions

To ensure 100% mathematical consistency and reproducibility, HMIE uses the following fixed methodology parameters:

| Parameter | Quantitative Definition | Baseline Reference |
|:---|:---|:---|
| **Budget Announcement Event** | Official Union Budget Presentation Day (February 1 Baseline) | `STAGING.EVIDENCE_MACRO_EVENTS` |
| **Observation Windows** | **3 Phases**: Pre ($T-10..T-1$), Day 0, Post ($T+1..T+10$) | Multi-day Fiscal Policy Study |
| **Price Metric Reference** | **Daily Closing Price** (Eliminates intraday wick noise) | `STAGING.STOCK_HIST_DATA` |
| **Canonical Sector Source** | Standardized 20-Sector Master Taxonomy | `STAGING.SECTOR_MASTER` |

---

## 5. Historical Context & Performance Breakdown

Across the 14-year sample universe ($N = 14$ Union Budgets), market performance follows a clear 3-phase fiscal cycle:

| Category / Window | Sample Size ($N$) | Avg Return (%) | Win Rate % | Best Performing Sector |
|:---|:---:|:---:|:---:|:---|
| **Phase 1: Pre-Budget De-risking** | **14 Budgets** | **-0.85%** | **42.9%** ($6/14$) | 💻 **NIFTY IT** (-0.08%) |
| **Phase 2: Budget Day Session** | **14 Budgets** | **+0.15%** | **50.0%** ($7/14$) | 🏦 **BANK NIFTY** (+0.45%) |
| **Phase 3: Post-Budget Relief Rally** | **14 Budgets** | **+1.62%** | **64.3%** ($9/14$) | 🏦 **PSU BANKING** (+2.19%) |

> **Key Takeaway**: Pre-budget windows ($T-10 \rightarrow T-1$) experience de-risking in over 57% of years, whereas post-budget windows ($T+1 \rightarrow T+10$) deliver positive relief rallies in 64.3% of years.

---

## 6. Representative Historical Cases

> **Primary Historical Reference**: Current macro fiscal conditions most closely resemble **Union Budget 2021** (Match Tier: **94.0%**). The 2021 budget triggered a massive post-event relief rally of **+9.01%** in Nifty 50 over 30 days as high capital expenditure commitments removed growth uncertainty.

### Selected Union Budget Episodes in Oracle Database

| Rank & Event Name | Presentation Date | Macro Regime at Event | Pre-30D Return | Post-30D Return | 30-Day Post-Budget Sector Leader |
|:---:|:---:|:---:|:---:|:---:|:---|
| 🥇 **#1 Union Budget 2021** | 2021-02-01 | CONSOLIDATION | 0.00% | **+9.01%** | 🚚 DISTRIBUTION_SERVICES |
| 🥈 **#2 Union Budget 2017** | 2017-02-01 | CONSOLIDATION | +6.00% | **+0.57%** | 📡 COMMUNICATIONS |
| 🥉 **#3 Union Budget 2024** | 2024-02-01 | CONSOLIDATION | +3.20% | **+1.71%** | ⚡ ENERGY_MINERALS |
| #4 **Union Budget 2014** | 2014-07-10 | CONSOLIDATION | +2.54% | **+0.00%** | 💼 COMMERCIAL_SERVICES |
| #5 **Union Budget 2019** | 2019-07-05 | CONSOLIDATION | 0.00% | **-2.45%** | 🛍️ CONSUMER_NON_DURABLES |

---

## 7. Current Market Context

| Parameter | Current Research Condition | Baseline Standard / Description |
|:---|:---|:---|
| **Macro Event Category** | **Union Budget Announcement** | Annual Fiscal Policy & Tax Statement |
| **Observation Horizon** | **14-Year Sample Universe** ($2011–2025$) | Modern Fiscal Reform Era |
| **Current Market Regime** | **CONSOLIDATION / BULL** | Pre-budget positioning window |
| **Primary Beneficiary Sectors** | **PSU BANKS, ENERGY, INFRASTRUCTURE** | Direct Capex & Policy Beneficiaries |

---

## 8. Sector & Theme Impact & Performance

### Historical Sector Observations (`STAGING.SECTOR_MASTER`)
Across all 14 historical Union Budget windows ($2011–2025$):
- 🏦 **PSU BANKING / SBIN**: Produced an average post-budget return of **+2.19%** ($T+1 \rightarrow T+10$, Win Rate: **50.0%**, $N=14$).
- ⚡ **RELIANCE / ENERGY**: Produced an average post-budget return of **+1.62%** ($T+1 \rightarrow T+10$, Win Rate: **64.3%**, $N=14$).
- 🚆 **RAILWAY / CAPEX THEME**: Outperformed broad market index post-budget in **4 of the last 5 budgets** ($80.0\%$).

### Interpretation & Context
State Bank of India and Reliance Industries most frequently demonstrate post-budget relief buying as capital expenditure allocations and tax clarity emerge.

---

## 9. Stock Impact (Leaders & Laggards)

### Top Post-Budget Champions ($T+1 \rightarrow T+10$ Window)

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🥇 **SBIN** | **+2.19%** | **50.0%** (7/14) | 14 events |
| 🥈 **RELIANCE** | **+1.62%** | **64.3%** (9/14) | 14 events |
| 🥉 **INFY** | **+0.73%** | **50.0%** (7/14) | 14 events |

### Bottom Performing Laggards ($T+1 \rightarrow T+10$)

| Stock | Avg Return | Win Rate | Sample |
|:---|:---:|:---:|:---:|
| 🔻 **BEL** | **-2.18%** | **42.9%** (6/14) | 14 events |
| 🔻 **LT** | **-1.34%** | **50.0%** (7/14) | 14 events |

---

## 10. Key Observations
1. **Pre-Budget De-risking**: Markets trim exposure heading into Budget Day ($T-10 \rightarrow T-1$ mean return: -0.85%).
2. **Post-Budget Relief**: 9 out of 14 years ($64.3\%$) logged positive post-budget 10-day returns as fiscal uncertainty lifted.
3. **Energy & PSU Leadership**: SBIN and RELIANCE provide consistent post-budget relief rally performance.

---

## 11. Evidence Quality & Credibility Assessment

| Field | Value | Detailed Justification |
|:---|:---:|:---|
| **Historical Sample** | **N = 14** | 14 consecutive Union Budget announcements ($2011–2025$) |
| **Post-Budget Consistency** | **HIGH** | 64.3% win rate across post-budget 10-day windows |
| **Cross Validation** | **VERIFIED** | Verified against Oracle database macro event logs |
| **Evidence Quality** | **HIGH** | Cross-validated against Oracle `STAGING.STOCK_HIST_DATA` |
| **Last Data Refresh** | **`2026-08-09`** | Automatically verified daily against Oracle EOD pipeline |
| **Dataset Version** | **`v2.0.1`** | Oracle analytical stage baseline tables |
| **Prediction Confidence** | **N/A** | **Non-Predictive Historical Study** |

---

## 12. How This Research Can Be Used

| Intended Purpose (✓) | Explicit Non-Purpose (✗) |
|:---|:---|
| ✓ Understanding pre-budget de-risking and post-budget relief trends | ✗ Predicting exact tax changes or budget announcement details |
| ✓ Evaluating sector positioning ahead of February fiscal announcements | ✗ Executing high-leverage option bets on Budget Day |
| ✓ Informing long-term asset allocation across fiscal-sensitive sectors | ✗ Providing personalized financial or investment advice |

---

## 13. Next Research Questions
1. *Do post-budget relief rallies last longer during Union Budgets presented in election years vs non-election years?*
2. *How do pre-budget expectations in Infrastructure stocks (LT) correlate with actual capital expenditure budget allocations?*
3. *What is the combined win rate of holding a Pre-Diwali through Post-Budget seasonal basket?*

---

## 14. Recommended Next Reading in HMIE Terminal Library

- 🏛️ [`RBI Monetary Policy.md`](/research/RBI%20Monetary%20Policy.md) — *Compares fiscal policy event reactions with monetary policy event reactions.*
- 📉 [`Market Corrections & Recoveries.md`](/research/Market%20Corrections%20%26%20Recoveries.md) — *Examines fiscal policy capex announcements during ongoing market corrections.*
- 🪔 [`Pre-Diwali Seasonality.md`](/research/Pre-Diwali%20Seasonality.md) — *Studies whether holding a pre-Diwali basket through February Budget Day improves combined win rates.*
- 🇮🇳 [`Independence Day Seasonality.md`](/research/Independence%20Day%20Seasonality.md) — *Compares August holiday seasonality with fiscal year-end positioning.*

---

> **Specification**: `CRN v1.1` • **Dataset**: `v2.0.1` • **Quality Gates Passed**: `✓ CAR-1` `✓ CAR-2` `✓ CAR-3` `✓ CAR-4` `✓ CAR-5`
