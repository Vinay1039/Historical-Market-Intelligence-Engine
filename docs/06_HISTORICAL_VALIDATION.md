# Quality Gate 2 — Historical Validation Specification (v1.0.0)

**Tool Location**: `tools/validate_historical_cases.py`

Quality Gate 2 verifies research correctness against known historical anchor events across 15+ years of Indian market history.

---

## 🎯 Historical Golden Anchor Test Cases

| Historical Anchor Event | Target Date | Expected Classification | Verified Empirical Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| **COVID Crash Low** | 2020-03-23 | `BEAR_MARKET` (% > EMA200 < 10%) | `BEAR_MARKET` (% > EMA200 = 2.55%, Breadth = 0.0075) | 🟩 PASS |
| **COVID Recovery Phase** | 2020-06-15 | `BEAR_REBOUND` (% > EMA200 > 20%) | `BEAR_REBOUND` (% > EMA200 = 30.64%) | 🟩 PASS |
| **2021 Bull Market Peak** | 2021-10-18 | Broad Breadth (% > EMA200 > 80%) | `CONSOLIDATION` (% > EMA200 = 90.90%) | 🟩 PASS |
| **2020 Tech Sector Rally** | 2020-12-01 | `TECHNOLOGY_SERVICES` Leading | Rank 4, RS 3M = +7.44%, Status = `LEADING` | 🟩 PASS |
| **2024 Capex / Railway Rally** | 2024-02-01 | `RAILWAY_CAPEX` Theme Rank 1 | Rank 1, RS 3M = +41.60%, Status = `LEADING` | 🟩 PASS |

---

## 📊 Live Validation Status (v1.0.0)

```text
HISTORICAL VALIDATION SUMMARY: 5 Passed, 0 Failed.
Status: 🟩 ALL HISTORICAL GOLDEN ANCHOR CASES ACCURATE
```
