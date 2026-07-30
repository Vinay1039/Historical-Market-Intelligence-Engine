# HMIE Master Research Questions (v1.0.0 - v1.5.0)

This document establishes the foundational research questions driving all analytical engines, evidence tables, and UI visualizers in HMIE.

---

## 🎯 Domain 1: Market Regimes & Breadth Structure

- **Q1.1**: *What percentage of equities trading above key EMAs (EMA20, EMA50, EMA200) signals a sustainable market regime transition vs a false breakout?*
  - **Engine**: Stage 3.2 Market Breadth & Stage 3.6 Regime Engine (`STAGING.MARKET_BREADTH_DAILY`, `STAGING.MARKET_REGIMES`).
  - **Evidence**: $N=3,714$ trading days classified into `BULL_EXPANSION`, `BEAR_MARKET`, `BEAR_REBOUND`, `CONSOLIDATION`.

- **Q1.2**: *What is the average duration (in trading days) of bull expansion vs bear market regimes in Indian finance over 15+ years?*
  - **Engine**: Stage 3.6 Historical Regime Engine (`STAGING.MARKET_REGIMES`).

---

## 🎯 Domain 2: Sector & Theme Rotation Momentum

- **Q2.1**: *Do sectors in top 3-month relative strength ranks maintain leadership over 63-day holding periods?*
  - **Engine**: Stage 3.3 Sector & Industry Rotation Engine (`STAGING.SECTOR_ROTATION`, `STAGING.INDUSTRY_ROTATION`).

- **Q2.2**: *Can custom cross-industry macro baskets (e.g. Defence & Aerospace, Railway Capex) outperform broad sector indices during infrastructure capital expansion cycles?*
  - **Engine**: Stage 3.5 Custom Theme Engine (`STAGING.THEME_ROTATION`).

---

## 🎯 Domain 3: Historical Evidence & Scenario Parallels

- **Q3.1**: *What is the empirical distribution of market drawdown depth ($\ge 8\%$) and recovery duration (in calendar days) following major market shocks in India?*
  - **Engine**: Stage 4 Historical Evidence Engine (`STAGING.EVIDENCE_CORRECTIONS`).
  - **Evidence**: $N=9$ drawdowns (COVID crash 2020, Taper Tantrum 2013, Demonetization 2016, NBFC crisis 2018).

- **Q3.2**: *How do key equity sectors perform in the pre-30D and post-30D windows surrounding macro events (Union Budgets, General Elections)?*
  - **Engine**: Stage 4 Macro Event Evidence (`STAGING.EVIDENCE_MACRO_EVENTS`).
  - **Evidence**: $N=12$ macro event windows.

---

## 🎯 Domain 4: Quantitative Strategy Backtesting

- **Q4.1**: *What are the historical 15-year CAGR, Max Drawdown, Sharpe Ratio, and Win Rate of monthly sector rotation and top momentum stock strategies?*
  - **Engine**: Stage 6 Quantitative Strategy Lab (`STAGING.STRATEGY_PERFORMANCE`, `STAGING.STRATEGY_TRADES`).
