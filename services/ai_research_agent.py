"""
HMIE Stage 3.7 — AI Research Evidence Narrator Service
Adheres strictly to HMIE Constitution Law #8: "AI Never Calculates".
Fetches precomputed analytical data from Oracle/FastAPI endpoints and formats explainable markdown research briefings.
"""

from typing import Dict, Any, Optional
from core.database import get_db_connection

def generate_market_narrative(prompt: str, target_date: Optional[str] = None) -> Dict[str, Any]:
    """Generates an evidence-backed market research narrative from precomputed data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Fetch Latest Date if not provided
        if not target_date:
            cursor.execute("SELECT TO_CHAR(MAX(DATETIME), 'YYYY-MM-DD') FROM STAGING.MARKET_REGIMES")
            target_date = cursor.fetchone()[0]

        # 2. Fetch Current Macro Market Regime
        cursor.execute("""
            SELECT REGIME_NAME, REGIME_DURATION_DAYS, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200, BREADTH_RATIO, NET_ADVANCES, AVG_MARKET_RETURN_PCT
            FROM STAGING.MARKET_REGIMES
            WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        """, [target_date])
        reg_row = cursor.fetchone()
        regime_info = {
            "date": target_date,
            "regime": reg_row[0] if reg_row else "UNKNOWN",
            "duration_days": int(reg_row[1]) if reg_row else 0,
            "pct_above_ema20": float(reg_row[2]) if reg_row and reg_row[2] is not None else 0.0,
            "pct_above_ema50": float(reg_row[3]) if reg_row and reg_row[3] is not None else 0.0,
            "pct_above_ema200": float(reg_row[4]) if reg_row and reg_row[4] is not None else 0.0,
            "breadth_ratio": float(reg_row[5]) if reg_row and reg_row[5] is not None else 0.0,
            "net_advances": int(reg_row[6]) if reg_row and reg_row[6] is not None else 0,
            "avg_return_pct": float(reg_row[7]) if reg_row and reg_row[7] is not None else 0.0
        }

        # 3. Fetch Top 5 Leading Sectors
        cursor.execute("""
            SELECT * FROM (
                SELECT SECTOR_CODE, SECTOR_RANK_3M, RELATIVE_STRENGTH_3M, RANK_DELTA_3M, ROTATION_STATUS
                FROM STAGING.SECTOR_ROTATION
                WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
                ORDER BY SECTOR_RANK_3M ASC
            ) WHERE ROWNUM <= 5
        """, [target_date])
        leading_sectors = [
            {
                "sector_code": r[0],
                "rank_3m": int(r[1]),
                "relative_strength_3m": float(r[2]) if r[2] is not None else 0.0,
                "rank_delta_3m": int(r[3]) if r[3] is not None else 0,
                "status": r[4]
            }
            for r in cursor.fetchall()
        ]

        # 4. Fetch Top 3 Custom Themes
        cursor.execute("""
            SELECT * FROM (
                SELECT THEME_CODE, THEME_RANK_3M, RELATIVE_STRENGTH_3M, RANK_DELTA_3M, ROTATION_STATUS
                FROM STAGING.THEME_ROTATION
                WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
                ORDER BY THEME_RANK_3M ASC
            ) WHERE ROWNUM <= 3
        """, [target_date])
        top_themes = [
            {
                "theme_code": r[0],
                "rank_3m": int(r[1]),
                "relative_strength_3m": float(r[2]) if r[2] is not None else 0.0,
                "rank_delta_3m": int(r[3]) if r[3] is not None else 0,
                "status": r[4]
            }
            for r in cursor.fetchall()
        ]

        # 5. Fetch Top 5 Ranked Stocks Market-Wide
        cursor.execute("""
            SELECT * FROM (
                SELECT r.SYMBOL, s.COMPANY, r.SECTOR_CODE, r.INDUSTRY_CODE, r.RETURN_3M, r.MARKET_RANK, r.MARKET_PERCENTILE
                FROM STAGING.STOCK_RANKINGS r
                JOIN HR.STOCKS s ON r.SYMBOL = s.SYMBOL
                WHERE r.DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
                ORDER BY r.MARKET_RANK ASC
            ) WHERE ROWNUM <= 5
        """, [target_date])
        top_stocks = [
            {
                "symbol": r[0],
                "company": r[1],
                "sector_code": r[2],
                "industry_code": r[3],
                "return_3m": float(r[4]) if r[4] is not None else 0.0,
                "market_rank": int(r[5]),
                "market_percentile": float(r[6]) if r[6] is not None else 0.0
            }
            for r in cursor.fetchall()
        ]

        # 6. Format Markdown Narrative Report
        sec_table_rows = "\n".join([
            f"| Rank {s['rank_3m']} | `{s['sector_code']}` | **{s['relative_strength_3m']:+.2f}%** | {s['rank_delta_3m']:+d} | `{s['status']}` |"
            for s in leading_sectors
        ])

        thm_table_rows = "\n".join([
            f"| Rank {t['rank_3m']} | `{t['theme_code']}` | **{t['relative_strength_3m']:+.2f}%** | {t['rank_delta_3m']:+d} | `{t['status']}` |"
            for t in top_themes
        ])

        stk_table_rows = "\n".join([
            f"| #{k['market_rank']} | **{k['symbol']}** ({k['company']}) | `{k['sector_code']}` | **{k['return_3m']:+.2f}%** | Top {k['market_percentile']:.1f}% |"
            for k in top_stocks
        ])

        markdown_narrative = f"""# 📊 HMIE Historical Market Intelligence Briefing
**Target Date**: {target_date} | **Source**: Oracle `STAGING` Precomputed Data | **Compliance**: Constitution Law #8 (Zero Calculation)

---

## 🏛️ 1. Macro Market Regime Context
- **Current Regime**: `{regime_info['regime']}` (Active Duration: **{regime_info['duration_days']} consecutive trading days**)
- **Breadth Participation**: **{regime_info['pct_above_ema200']:.2f}%** of stocks above EMA200 | **{regime_info['pct_above_ema50']:.2f}%** above EMA50
- **Advance/Decline Ratio**: **{regime_info['breadth_ratio']:.2f}** (Net Advances: **{regime_info['net_advances']:+d}**)
- **Average Market Return**: **{regime_info['avg_return_pct']:+.2f}%**

---

## 🚀 2. Sector Leadership & Rotation (3-Month Relative Strength)
| Sector Rank | Sector Code | 3M Relative Strength | 3M Rank Delta | Rotation Status |
| :--- | :--- | :--- | :--- | :--- |
{sec_table_rows}

---

## 🎯 3. Custom Macro Theme Rotation
| Theme Rank | Theme Code | 3M Relative Strength | 3M Rank Delta | Rotation Status |
| :--- | :--- | :--- | :--- | :--- |
{thm_table_rows}

---

## 🏆 4. Top Ranked Stocks Market-Wide
| Market Rank | Stock Ticker | Sector | 3M Return | Market Percentile |
| :--- | :--- | :--- | :--- | :--- |
{stk_table_rows}

---

> [!NOTE]
> **Evidence Verification Statement**: All indicators, relative strength scores, rank deltas, and regime classifications presented above were extracted directly from precomputed Oracle analytical vectors without real-time computation or model hallucination.
"""

        return {
            "prompt": prompt,
            "target_date": target_date,
            "regime": regime_info['regime'],
            "regime_duration_days": regime_info['duration_days'],
            "leading_sectors": leading_sectors,
            "top_themes": top_themes,
            "top_stocks": top_stocks,
            "markdown_narrative": markdown_narrative
        }
    finally:
        cursor.close()
        conn.close()
