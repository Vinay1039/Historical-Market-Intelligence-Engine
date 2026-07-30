# HMIE Master Research Compendium (2011–2026)

**Platform**: Historical Market Intelligence Engine (HMIE v2.0.0)  
**Oracle Database**: Oracle 23c XE thick client (`SNAPSHOT-2026-07-29-2.4M`)  
**Observation Window**: 15 Years (January 2011 – July 2026, $N=3,714$ trading days, $N=2.42\text{M}$ stock price bars)  
**Governance**: HMIE Constitutional Laws 1–11  
**Validation Status**: Quality Gate 1 PASS (28/28) | Quality Gate 2 PASS (25/25, Dual-Pipeline 0.00% Exact Match)  

---

## 📚 Executive Summary of Published Research Studies

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   HMIE RESEARCH REGISTRY (Oracle)                                 │
├───────────────┬────────────────────────────────────────────────────────┬─────────────┬────────────┤
│ Study ID      │ Title                                                  │ Version     │ Status     │
├───────────────┼────────────────────────────────────────────────────────┼─────────────┼────────────┤
│ STD-2026-001  │ Recovery Characteristics After Major Indian Shocks      │ v1.2.0      │ PUBLISHED  │
│ STD-2026-002  │ Custom Theme & Sector Leadership During Recoveries     │ v1.0.0      │ PUBLISHED  │
│ STD-2026-003  │ 15-Year Quantitative Strategy Lab & Benchmarks         │ v2.0.0      │ PUBLISHED  │
│ STD-2026-004  │ Implementation Fee Drag & Sustainable Cost Thresholds   │ v1.0.0      │ PUBLISHED  │
└───────────────┴────────────────────────────────────────────────────────┴─────────────┴────────────┤
```

---

## 🔬 Study 1: Recovery Characteristics After Major Indian Market Corrections (STD-2026-001)

### Research Question
*What is the empirical distribution of market drawdown depth ($\ge 8\%$) and recovery duration (in calendar days) following major market shocks in Indian equities over 2011–2026?*

### Empirical Distribution ($N=8$ Completed Recovery Windows)

| Metric | Recovery Duration (Days) | Max Drawdown Depth (%) |
| :--- | :---: | :---: |
| **Mean ($\bar{X}$)** | **137.1 days** | **-19.97%** |
| **Median** | **112.0 days** | **-20.21%** |
| **Standard Deviation ($s$)** | **116.4 days** | **7.84%** |
| **Minimum / Maximum** | **[4, 358] days** | **[-38.44%, -8.41%]** |
| **95% Confidence Interval ($\text{CI}_{95\%}$)** | **[42.2, 232.0] days** | **[-26.52%, -13.42%]** |

### Historical Shocks Evidence Table (`STAGING.EVIDENCE_CORRECTIONS`)

| Event Name | Peak Date | Trough Date | Recovery Date | Max DD % | Recovery Days | Recovery Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **COVID-19 Global Shock** | 2020-01-20 | 2020-03-23 | 2020-11-10 | **-38.44%** | **295 days** | V-Shaped Recovery |
| **2015 China Devaluation** | 2015-03-03 | 2016-02-29 | 2017-03-16 | **-23.21%** | **358 days** | U-Shaped Recovery |
| **2018 NBFC Liquidity Crisis** | 2018-08-28 | 2018-10-26 | 2019-06-03 | **-14.85%** | **219 days** | V-Shaped Recovery |
| **2016 Demonetization Shock** | 2016-09-08 | 2016-12-26 | 2017-03-14 | **-11.72%** | **78 days** | V-Shaped Recovery |
| **2022 Russia-Ukraine Shock** | 2021-10-18 | 2022-03-08 | 2022-11-24 | **-15.12%** | **261 days** | U-Shaped Recovery |

---

## 📈 Study 2: Custom Theme & Sector Leadership (STD-2026-002)

### Research Question
*Which market sectors and custom themes lead the market exit out of major market crash troughs?*

### Key Discoveries
1. **2020 COVID Recovery Leadership**: `TECHNOLOGY_SERVICES` (IT) and `PHARMA` reached Rank 1 LEADING status within **45 days** of the March 23, 2020 trough, generating $+42.8\%$ 90-day post-trough return.
2. **2024 Capex Rally Leadership**: `RAILWAY_CAPEX` and `DEFENSE_OFFENCE` custom themes maintained Rank 1 LEADING status continuously during Q1 2024 with $+68.4\%$ 90-day return.

---

## 📊 Study 3: 15-Year Quantitative Strategy Lab & Benchmarks (STD-2026-003)

### Research Question
*What are the 15-year risk-adjusted returns (CAGR, MaxDD, Sharpe, Alpha, Beta) of systematic rotation strategies vs standard benchmarks (`NIFTY50`, `NIFTY500`, `NIFTY_EQUAL`, `NIFTY_MOMENTUM_30`)?*

### Precomputed Performance Summary (2011–2026)

| Strategy Code | Strategy Name | 15-Yr CAGR | Max Drawdown | Sharpe Ratio | Win Rate | Trade Count |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `SECTOR_ROTATION_TOP3` | Sector Rotation Top 3 | **16.15%** | **-36.14%** | **0.55** | **68.2%** | 179 trades |
| `THEME_MOMENTUM_TOP1` | Custom Theme Leadership | **20.74%** | **-46.04%** | **0.57** | **71.5%** | 179 trades |
| `TOP_STOCK_MOMENTUM_95P` | Top Stock Momentum | **11.28%** | **-26.02%** | **0.41** | **61.4%** | 179 trades |

### Benchmark Relative Risk Metrics vs `NIFTY50` ($11.28\%$ CAGR, $16.82\%$ Volatility)

| Strategy Code | Benchmark Index | Strategy CAGR | Alpha ($\alpha$) | Beta ($\beta$) | Volatility ($\sigma_s$) | Info Ratio ($IR$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `SECTOR_ROTATION_TOP3` | `NIFTY50` | **16.15%** | **+7.64%** | **0.56** | **23.51%** | **0.07** |
| `SECTOR_ROTATION_TOP3` | `NIFTY500` | **16.15%** | **+4.56%** | **0.71** | **23.51%** | **0.04** |
| `THEME_MOMENTUM_TOP1` | `NIFTY50` | **20.74%** | **+9.35%** | **1.02** | **31.39%** | **0.12** |
| `THEME_MOMENTUM_TOP1` | `NIFTY500` | **20.74%** | **+3.39%** | **1.34** | **31.39%** | **0.11** |
| `THEME_MOMENTUM_TOP1` | `NIFTY_MOMENTUM_30`| **20.74%** | **+0.00%** | **1.00** | **31.39%** | **0.05** |
| `TOP_STOCK_MOMENTUM_95P` | `NIFTY50` | **11.28%** | **-0.00%** | **1.00** | **23.01%** | **-0.00** |

---

## 💸 Study 4: Implementation Fee Drag & Sustainable Cost Thresholds (STD-2026-004)

### Research Question
*How sensitive is each quantitative strategy to implementation cost drag, what is the break-even fee vs `NIFTY50`, and what is the Maximum Sustainable Cost Threshold?*

### Transaction Fee Stress Matrix & Data-Driven Classifications

| Strategy Code | Fee Drag ($f$) | Net Total Return | Net 15-Yr CAGR | Net Max Drawdown | Break-Even Fee vs NIFTY50 | Max Sustainable Cost Threshold | Robustness Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `SECTOR_ROTATION_TOP3` | **0.00%** | **+832.70%** | **+16.15%** | **-36.14%** | **0.180%** | **0.627%** | 🟩 `ROBUST` |
| `SECTOR_ROTATION_TOP3` | **0.10%** | **+578.14%** | **+13.42%** | **-38.46%** | **0.180%** | **0.627%** | 🟩 `ROBUST` |
| `SECTOR_ROTATION_TOP3` | **0.25%** | **+311.66%** | **+9.43%** | **-41.80%** | **0.180%** | **0.627%** | 🟩 `ROBUST` |
| `SECTOR_ROTATION_TOP3` | **0.50%** | **+58.37%** | **+3.08%** | **-55.48%** | **0.180%** | **0.627%** | 🟩 `ROBUST` |
| `THEME_MOMENTUM_TOP1` | **0.00%** | **+1,563.68%** | **+20.74%** | **-46.04%** | **0.343%** | **0.788%** | 🟩 `ROBUST` |
| `THEME_MOMENTUM_TOP1` | **0.10%** | **+1,114.78%** | **+17.91%** | **-48.69%** | **0.343%** | **0.788%** | 🟩 `ROBUST` |
| `THEME_MOMENTUM_TOP1` | **0.25%** | **+614.93%** | **+13.77%** | **-53.08%** | **0.343%** | **0.788%** | 🟩 `ROBUST` |
| `THEME_MOMENTUM_TOP1` | **0.50%** | **+181.76%** | **+7.16%** | **-60.17%** | **0.343%** | **0.788%** | 🟩 `ROBUST` |
| `TOP_STOCK_MOMENTUM_95P` | **0.00%** | **+392.76%** | **+11.28%** | **-26.02%** | **0.001%** | **0.447%** | 🟨 `MODERATE` |
| `TOP_STOCK_MOMENTUM_95P` | **0.10%** | **+253.94%** | **+8.66%** | **-27.29%** | **0.001%** | **0.447%** | 🟨 `MODERATE` |
| `TOP_STOCK_MOMENTUM_95P` | **0.25%** | **+104.79%** | **+4.84%** | **-30.15%** | **0.001%** | **0.447%** | 🟨 `MODERATE` |
| `TOP_STOCK_MOMENTUM_95P` | **0.50%** | **-17.51%** | **-1.27%** | **-36.13%** | **0.001%** | **0.447%** | 🟨 `MODERATE` |

---

## 🏛️ Macro Event Evidence Table (`STAGING.EVIDENCE_MACRO_EVENTS`)

| Macro Event Name | Event Date | Category | Pre 30D Return | Post 30D Return | Top Performing Sector (Post 30D) |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Union Budget 2021** | 2021-02-01 | `BUDGET` | -2.15% | **+11.45%** | `BANKS_FINANCE` |
| **General Election 2024** | 2024-06-04 | `ELECTION` | +1.85% | **+6.20%** | `RAILWAY_CAPEX` |
| **Demonetization 2016** | 2016-11-08 | `MACRO_SHOCK` | -1.10% | **-4.85%** | `PHARMA` |
| **COVID Emergency Lockdown** | 2020-03-24 | `PANDEMIC` | -28.40% | **+18.90%** | `TECHNOLOGY_SERVICES` |

---

## 🛡️ Reproducibility & Governance Architecture

All published research adheres strictly to:
1. **Constitutional Law 1 ("Historical First")**: 100% real historical data; zero forward-looking bias.
2. **Constitutional Law 8 ("AI Never Calculates")**: REST API serves precomputed Oracle tables.
3. **Constitutional Law 9 ("Verify Before You Trust")**: Quality Gate 1 (28 checks) and Gate 2 (25 checks).
4. **Constitutional Law 10 ("Reproducibility Over Convenience")**: 0.00% exact match across dual independent pipelines.
5. **Constitutional Law 11 ("Law of Reproducible Research")**: SHA256 SQL Hashing + Oracle Research Registry.
