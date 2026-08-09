# HMIE Canonical Research Note: RBI-2026-08 (v2.0)

> **Dataset Version**: `v2.0.1` • **Sample Universe**: 15 RBI Monetary Policy Meetings ($2011–2025$) • **Governance**: Single Source of Truth (`STAGING.MARKET_CALENDAR` + `STAGING.STOCK_HIST_DATA`)

---

## 1. Research Question
**How have Indian equity markets historically behaved after RBI Rate Hikes, Rate Cuts, and Policy Pauses, and what does today's policy condition most closely resemble?**

---

## 2. Executive Summary (BLUF)
Historically, markets experience pre-decision consolidation ($T-1$ average return: **-0.49%**), followed by positive post-decision drift on Day 1 ($T+1$ win rate: **66.7%**, mean: **+0.58%**) during **Policy Pause** cycles. Across 3 historical Policy Pause meetings, **Banking stocks** (led by ICICIBANK and SBIN) produced the highest post-decision relief return (**+1.53%**).

---

## 3. Current Situation & Input Parameters

| Parameter | Today's Input Condition | Baseline Standard |
|:---|:---|:---|
| **Repo Rate Decision** | **PAUSE** (No Change) | Benchmark rate held steady at 6.50% |
| **BPS Change** | **0.0 bps** | Zero interest rate adjustment |
| **CPI Inflation** | **4.5%** | Within RBI target band ($4.0\% \pm 2\%$) |
| **Market Regime** | **SIDEWAYS** | Nifty index in consolidation phase |
| **Statement Tone** | **NEUTRAL** | Balanced policy stance |

---

## 4. Historical Context & Stance Breakdown

Across the modern MPC sample universe ($N = 15$ meetings), historical performance varies by policy stance:

| Stance Category | Sample Size ($N$) | 3-Day Avg Return ($T+3$) | Win Rate % | Best Performing Sector |
|:---|:---:|:---:|:---:|:---|
| **Policy Pause** | **3 Meetings** | **-0.01%** | **66.7%** (2 of 3) | 🏦 **BANKING** (+1.53%) |
| **Rate Cut** | **7 Meetings** | **+0.03%** | **57.1%** (4 of 7) | ⚡ **ENERGY** (+1.72%) |
| **Rate Hike** | **5 Meetings** | **-0.54%** | **50.0%** (2 of 5) | 🚘 **AUTO** (+0.52%) |

*Note: All returns represent 3-day post-announcement holding periods.*

---

## 5. Closest Historical Analogs (Narrative Match Breakdown)

Today's RBI meeting most closely resembles the meeting of **07-Feb-2025** (Similarity: **99.4%**) because:
- **Repo Action & BPS**: Identical (PAUSE, 0.0 bps)
- **CPI Inflation**: Identical (4.5%)
- **Statement Tone**: Identical (NEUTRAL)
- **Market Regime**: Identical (SIDEWAYS)

### Top 5 Historical Match Breakdown:

| Rank | Historical Date | Match Tier | Matching Factors | Key Differences Called Out | Nifty T+1 | Bank Nifty T+1 |
|:---:|:---:|:---:|:---|:---|:---:|:---:|
| 🥇 **#1** | **2025-02-07** | **High (99.4%)** | ✅ Action ✅ BPS ✅ CPI ✅ Regime ✅ Tone | *None (Exact Baseline Match)* | **-0.24%** | **-0.40%** |
| 🥈 **#2** | **2024-02-08** | **High (88.2%)** | ✅ Action ✅ BPS ✅ Tone | ⚠️ CPI higher (5.1% vs 4.5%)<br>⚠️ Regime (BULL vs SIDEWAYS) | **+0.12%** | **+1.84%** |
| 🥉 **#3** | **2021-02-05** | **Moderate (78.8%)** | ✅ Action ✅ BPS ✅ CPI ✅ Tone | ⚠️ Regime (BULL vs SIDEWAYS) | **+1.87%** | **+1.57%** |
| 4 | **2018-08-01** | **Low (49.1%)** | ✅ CPI ✅ Tone | ❌ Action (HIKE vs PAUSE)<br>❌ BPS (+25 vs 0) | **-1.09%** | **-0.42%** |
| 5 | **2016-04-05** | **Low (47.0%)** | ✅ Tone | ❌ Action (CUT vs PAUSE)<br>❌ BPS (-25 vs 0)<br>❌ CPI higher (5.5% vs 4.5%) | **+0.13%** | **-0.94%** |

---

## 6. Sector Impact & Performance

### Historical Observations (Facts)
Across the 3 historical Policy Pause meetings:
- 🏦 **BANKING**: **+1.53% Avg Return** (Win Rate: **66.7%**, $N=3$)
- ⚡ **ENERGY**: **+1.21% Avg Return** (Win Rate: **66.7%**, $N=3$)
- 🚘 **AUTO**: **+0.46% Avg Return** (Win Rate: **66.7%**, $N=3$)

### Interpretation & Context
This suggests that rate-sensitive financial stocks have historically experienced post-pause relief rallies as interest rate uncertainty dissipates.

---

## 7. Stock Impact (F&O Champions & Laggards)

### Top 3 F&O Champions ($T+3$ Post-Pause Window)
1. 🥇 **DIXON**: **+3.04% Avg Return** (Win Rate: **66.7%**, $N=3$)
2. 🥈 **ICICIBANK**: **+2.82% Avg Return** (Win Rate: **100.0%** — Positive in 3 of 3 meetings)
3. 🥉 **SBIN**: **+2.29% Avg Return** (Win Rate: **66.7%**, $N=3$)

### Bottom Performing Laggard
- 🔻 **LT**: **-1.24% Avg Return** (Win Rate: **33.3%**, $N=3$)

---

## 8. Key Observations

1. **Pre-Meeting De-risking**: Nifty 50 consistently exhibits light consolidation on $T-1$ (Win rate: 0.0%, Mean: -0.49%) as market participants trim leverage prior to the policy statement.
2. **Day 1 Rebound**: Post-announcement Day 1 ($T+1$) yields positive returns in 2 of 3 pause meetings (Mean: +0.58%).
3. **Financials Lead Relief**: Large-cap banking stocks (ICICIBANK, SBIN) drive index stability following rate pauses.

---

## 9. Confidence & Sample Size Assessment

| Metric | Rating | Empirical Value / Reason |
|:---|:---:|:---|
| **Sample Size ($N$)** | **LOW-MEDIUM** | $N = 3$ Policy Pause meetings in current sample universe |
| **Consistency** | **MODERATE** | 66.7% win rate across $T+1$ and $T+3$ windows |
| **Overall Confidence** | **MODERATE** | Findings provide historical context, but small sample size requires caution |

---

## 10. Limitations & Governance Disclaimer

> ⚠️ **Historical Observation Note**: All figures in this research report are calculated directly from historical Oracle database stock prices (`STAGING.STOCK_HIST_DATA`). These metrics represent historical observations for research context only and are **NOT** forecasts or investment recommendations. Past market reactions do not guarantee future performance.

---

## 11. Suggested Follow-Up Research Questions

1. *How did Banking stocks perform when RBI paused rates during high inflation ($>6\%$) vs moderate inflation ($<4.5\%$)?*
2. *Did Realty stocks outperform Banking during initial Rate Cut cycles ($N=7$)?*
3. *How does market behavior around RBI Policy decisions compare with Union Budget announcements?*
