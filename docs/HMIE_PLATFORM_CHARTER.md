# HMIE Platform Charter & Institutional Terminal Governance (LOCKED v6.1) 🏛️

## 0. Mission & Vision Statement
The Historical Market Intelligence Engine (HMIE) is an **evidence-first historical market research platform** that transforms historical data into standardized, reusable **Canonical Research Notes**, with web dashboards serving as interactive views of those research findings.

HMIE is a personal decision-support system for historical context designed for long-term use (5–10 years) with zero unnecessary complexity.

---

## 1. Explicit Non-Goals
HMIE is strictly a historical market intelligence and research platform. It is **NOT** intended to become:
- A broker or trade execution platform
- A real-time trading terminal or day-trading tool
- A portfolio management system (PMS)
- A prediction engine or machine learning forecasting platform
- An autonomous trading agent
- A real-time market data vendor or low-latency price feed

---

## 2. Core Operational Philosophy: Team Roles
To ensure clear architectural boundaries:
- **ChatGPT**: Product Strategy, UX, Information Architecture, Scope Control
- **Claude**: Engineering Rigor, Data Correctness, Replay Verification, Maintainability
- **Grok**: Pragmatism, KISS Principle, Grounded Logic
- **Antigravity**: Execution Partner — Rapid Iteration, Clean Code, Single-Ownership Architecture

---

## 3. The 14 Permanent Engineering & Design Principles (LOCKED)

1. **Every Feature Must Reduce Cognitive Load**: Before adding anything, ask: *Does this make the user think less?* If not, do not build it.
2. **Every Dashboard Must Answer One Research Question**:
   - 🏠 **Home Dashboard**: *What research should I do today?*
   - 🏛️ **RBI Dashboard**: *How did markets react to similar RBI decisions?*
   - 📅 **Festival Dashboard**: *How have festivals historically affected markets?*
   - 🔍 **Analog Matcher**: *Which historical meetings most resemble today's conditions?*
   - 🩺 **Health Dashboard**: *Can I trust today's research?*
3. **Every Screen Must Teach**: A user should leave every page understanding one new market or research concept.
4. **Use Correct Financial Terminology, Always Explained in Plain English**: Maintain standard financial terms (`Standard Deviation (σ)`, `Sharpe Ratio`, `Drawdown`, `Gap Up Open`) to preserve institutional credibility. Never rename or approximate terms. Instead, teach the exact concept directly alongside the metric in plain English.
5. **Transparency Over Intelligence**: Never present calculations as black boxes. Show factor-by-factor match badges (`✅ Same Action`, `✅ Similar Inflation`, `⚠️ Higher Volatility`) instead of arbitrary similarity percentages.
6. **Design for Two Audiences**:
   - *Future You (6 months from now)*: Code explains itself with shallow hierarchies, descriptive names, and inline formula explanations.
   - *Beginner Investor*: Understands every table because numbers are accompanied by clear, visible 1-line stories.
7. **Answer First (BLUF)**: Every page and major section begins with a short plain-English summary sentence before any data grids or tables appear.
8. **Consistency Before Creativity**: Maintain 100% uniform design language across all pages. Never redesign a component "because it looks cooler."
9. **UI Inspiration Standards**: Aim for the **information density of Bloomberg**, the **research workflow usability of Koyfin**, the **interaction quality of TradingView**, and the **visual simplicity of Stripe**.
10. **Information Before Decoration**: Interface elements exist strictly to communicate research. Spacing, typography, and contrast drive aesthetics.
11. **Code Readability is a Feature**: Optimize code for human understanding. Prefer clear Python/JS functions and readable SQL over clever abstractions.
12. **Simplicity is a Design Constraint**: Avoid both over-engineering (no unearned bloat) and over-simplification (preserve full quantitative capability).
13. **Earned Complexity**: Before introducing any new component, justify it: *Does this improve research? Does it solve a real problem? Is there a simpler implementation?* If not, simplify.
14. **Four Quality Gates**: Before any task is complete, it must pass Data Review, Research Review, UX Review, and Visual Review.

---

## 4. HMIE Canonical Research Note Specification v1.1 (FROZEN)

1. **Title & Upfront Status Badge**: Displays `🟢 Completed`, `🟡 Ongoing`, `🔵 Seasonal`, or `🟣 Macro`.
2. **Shortened Research Question FIRST**: Appears before metadata so the reader understands what is being answered before viewing metadata.
3. **Single Merged 8-Field Research Snapshot Box**: Merges metadata and operational parameters into a single vertical 8-field table (Category, Asset, Sample, Observation Period, Evidence, Prediction, Investment Advice, Reading Time).
4. **Standardized 4-Bullet Executive Briefing BLUF**: Answer First, Headline Insight, Most Consistent Pattern, Important Caveat.
5. **Why This Matters & Section 4 Methodology & Definitions**: Friendly, accessible section title and mandatory quantitative definitions before analysis.
6. **Evidence BEFORE Current Context**: Section 5 Historical Context & Performance Breakdown precedes Section 7 Current Market Context.
7. **Key Takeaway Blockquotes**: Consistent `> **Key Takeaway**:` callout formatting across all tables.
8. **Visual Separation of Ongoing Cases**: Completed historical episodes are strictly separated from active ongoing observations with an explicit exclusion note (*"Not Included in Completed Recovery Statistics"*).
9. **Stock Impact Tables with Win Rates**: Leaders and laggards are rendered in structured tables with explicit Win Rate columns (`Stock | Avg Return | Win Rate | Sample`).
10. **Reduced Disclaimer Redundancy**: "Historical observations only" disclaimer is restricted to BLUF, Evidence Quality, and Usage sections to avoid visual noise.
11. **Standardized 8-Field Evidence Quality Table**: Historical Sample, Completed Cases, Active Cases, Evidence Quality, Cross Validation, Last Data Refresh, Dataset Version, Prediction Confidence.
12. **Recommended Next Reading Navigation**: Displays specific recommended next reads accompanied by explicit "Recommended because..." contextual explanations.
13. **ONE Universal Generator (`generate_research_note`)**: Operating in [`services/research_summary_service.py`](file:///C:/Users/vinay/.gemini/Fyers_Hist/services/research_summary_service.py).
14. **PERMANENT SPECIFICATION FREEZE (v1.1)**: Specification v1.1 is permanently frozen.
15. **Template Release Policy**: A CRN template version upgrade requires at least **two research notes** to demonstrate clear, tangible benefit before a template bump is approved and migrated library-wide.

---

## 5. Structured Research Library Taxonomy (LOCKED)
- 🏛️ **Macro Research**: RBI Monetary Policy, Union Budget
- 📅 **Seasonality Research**: Independence Day, Pre-Diwali, Festivals
- 📉 **Market Behaviour**: Corrections & Recoveries, Bear Markets, Bull Markets
- 📊 **Sector Research**: Banking, Auto, IT, Pharma
- 🔬 **Integrated Studies**: Cross-domain evidence synthesis (e.g. Budget during Correction)

---

## 6. Project Rules for Future Work
1. **No New Report Layouts or Dashboard Sprawl**: Every future study must use CRN v1.1. No new standalone HTML dashboards (`08_xxx.html`) should be created. The Research Library Portal (`dashboards/library.html`) serves as the primary publication entry point.
2. **Quality & Evidence Over Layout Expansion**: Future improvements must focus on data quality, chart interaction, EOD replay, terminal searchability, and visual typography rather than adding new document sections.
3. **Integrated Studies Combinatorial Guardrail**: Only create an Integrated Research Study if it answers a real, practical market research question that cannot be answered by reading the individual Canonical Research Notes separately. Avoid arbitrary combinations.
4. **HMIE v1 Feature Freeze**: Core engine architecture and governance are frozen. Future work focuses exclusively on (1) high-quality research note publishing, (2) visualization and usability refinement, and (3) EOD data pipeline integrity.
