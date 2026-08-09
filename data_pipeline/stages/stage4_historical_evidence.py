"""
===============================================================================
 HMIE Stage 4: Historical Evidence Engine Pipeline (stage4_historical_evidence.py)
 Precomputes 15-Year Market Corrections, Recoveries & Macro Event Evidence in Oracle.
 Compliance: HMIE Constitution Laws 1-10 (Zero Calculation REST Layer).
===============================================================================
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add workspace to path
sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection

def run_phase_1_corrections_evidence(conn):
    """Phase 1: Precomputes market drawdowns, recovery durations & top recovering sectors."""
    logger.info("--- Phase 1: Computing Historical Corrections & Recovery Evidence ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.EVIDENCE_CORRECTIONS")

    # Load daily market index time series (average price index over 15+ years)
    sql_mkt = """
    SELECT DATETIME, ROUND(AVG(CLOSE), 4) AS MKT_INDEX
    FROM STAGING.STOCK_HIST_DATA
    GROUP BY DATETIME
    ORDER BY DATETIME ASC
    """
    df = pd.read_sql(sql_mkt, conn)
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])

    # Vectorized peak detection
    df['PEAK'] = df['MKT_INDEX'].cummax()
    df['DRAWDOWN_PCT'] = (df['MKT_INDEX'] - df['PEAK']) / df['PEAK'] * 100.0

    corrections = []
    in_correction = False
    peak_date = None
    peak_val = 0
    trough_date = None
    trough_val = 0
    trough_dd = 0

    for row in df.itertuples():
        dt = row.DATETIME
        idx_val = row.MKT_INDEX
        dd = row.DRAWDOWN_PCT

        if not in_correction:
            if dd <= -8.0:  # Threshold: Drawdown >= 8%
                in_correction = True
                # Find peak before this drawdown
                prev_peak_row = df[(df['DATETIME'] <= dt) & (df['MKT_INDEX'] == row.PEAK)].iloc[-1]
                peak_date = prev_peak_row.DATETIME
                peak_val = prev_peak_row.MKT_INDEX
                trough_date = dt
                trough_val = idx_val
                trough_dd = dd
        else:
            if dd < trough_dd:
                trough_date = dt
                trough_val = idx_val
                trough_dd = dd

            if idx_val >= peak_val:  # Full Recovery achieved
                recovery_date = dt
                corr_days = (trough_date - peak_date).days
                rec_days = (recovery_date - trough_date).days

                # Recovery classification
                if rec_days <= max(1, corr_days * 1.5):
                    rec_type = 'V_SHAPED'
                elif rec_days <= 365:
                    rec_type = 'U_SHAPED'
                else:
                    rec_type = 'L_SHAPED_CONSOLIDATION'

                corrections.append({
                    "name": f"Correction ({peak_date.strftime('%b %Y')} - {trough_dd:.1f}%)",
                    "peak_date": peak_date.strftime('%Y-%m-%d'),
                    "trough_date": trough_date.strftime('%Y-%m-%d'),
                    "recovery_date": recovery_date.strftime('%Y-%m-%d'),
                    "max_dd_pct": round(trough_dd, 2),
                    "corr_days": corr_days,
                    "rec_days": rec_days,
                    "rec_type": rec_type
                })
                in_correction = False
                trough_dd = 0

    # If still in correction at current date
    if in_correction:
        last_dt = df.iloc[-1].DATETIME
        corr_days = (trough_date - peak_date).days
        corrections.append({
            "name": f"Ongoing Correction ({peak_date.strftime('%b %Y')} - {trough_dd:.1f}%)",
            "peak_date": peak_date.strftime('%Y-%m-%d'),
            "trough_date": trough_date.strftime('%Y-%m-%d'),
            "recovery_date": None,
            "max_dd_pct": round(trough_dd, 2),
            "corr_days": corr_days,
            "rec_days": None,
            "rec_type": 'ONGOING'
        })

    # For each correction, query precomputed top recovering sector & theme
    records = []
    for idx, c in enumerate(corrections, 1):
        tr_dt = c['trough_date']

        # Top sector 30D post trough
        cursor.execute("""
            SELECT * FROM (
                SELECT SECTOR_CODE FROM STAGING.SECTOR_ROTATION
                WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD') + 25 AND DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') + 35
                ORDER BY SECTOR_RANK_3M ASC
            ) WHERE ROWNUM = 1
        """, [tr_dt])
        r_sec30 = cursor.fetchone()
        top_sec30 = r_sec30[0] if r_sec30 else "ELECTRONIC_TECHNOLOGY"

        # Top sector 60D post trough
        cursor.execute("""
            SELECT * FROM (
                SELECT SECTOR_CODE FROM STAGING.SECTOR_ROTATION
                WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD') + 55 AND DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') + 65
                ORDER BY SECTOR_RANK_3M ASC
            ) WHERE ROWNUM = 1
        """, [tr_dt])
        r_sec60 = cursor.fetchone()
        top_sec60 = r_sec60[0] if r_sec60 else top_sec30

        # Top theme 60D post trough
        cursor.execute("""
            SELECT * FROM (
                SELECT THEME_CODE FROM STAGING.THEME_ROTATION
                WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD') + 55 AND DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') + 65
                ORDER BY THEME_RANK_3M ASC
            ) WHERE ROWNUM = 1
        """, [tr_dt])
        r_thm60 = cursor.fetchone()
        top_thm60 = r_thm60[0] if r_thm60 else "EV_MOBILITY"

        records.append((
            idx, c['name'], c['peak_date'], c['trough_date'], c['recovery_date'],
            c['max_dd_pct'], c['corr_days'], c['rec_days'], c['rec_type'],
            top_sec30, top_sec60, top_thm60
        ))

    sql_insert = """
    INSERT INTO STAGING.EVIDENCE_CORRECTIONS (
        EVENT_ID, EVENT_NAME, PEAK_DATE, TROUGH_DATE, RECOVERY_DATE,
        MAX_DRAWDOWN_PCT, CORRECTION_DAYS, RECOVERY_DAYS, RECOVERY_TYPE,
        TOP_SECTOR_30D, TOP_SECTOR_60D, TOP_THEME_60D
    ) VALUES (
        :1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'),
        TO_DATE(:5, 'YYYY-MM-DD'),
        :6, :7, :8, :9, :10, :11, :12
    )
    """
    cursor.executemany(sql_insert, records)
    logger.info(f"✓ Inserted {len(records)} historical correction & recovery evidence events into STAGING.EVIDENCE_CORRECTIONS")
    conn.commit()
    cursor.close()

def run_phase_2_macro_events_evidence(conn):
    """Phase 2: Precomputes macro event responses (Union Budgets, Elections, Crises)."""
    logger.info("\n--- Phase 2: Computing Macro Event Evidence (STAGING.EVIDENCE_MACRO_EVENTS) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.EVIDENCE_MACRO_EVENTS")

    macro_events = [
        # Union Budgets
        {"name": "Union Budget 2014", "cat": "BUDGET", "date": "2014-07-10"},
        {"name": "Union Budget 2017", "cat": "BUDGET", "date": "2017-02-01"},
        {"name": "Union Budget 2019", "cat": "BUDGET", "date": "2019-07-05"},
        {"name": "Union Budget 2021", "cat": "BUDGET", "date": "2021-02-01"},
        {"name": "Union Budget 2024", "cat": "BUDGET", "date": "2024-02-01"},
        # Elections
        {"name": "General Election 2014", "cat": "ELECTION", "date": "2014-05-16"},
        {"name": "General Election 2019", "cat": "ELECTION", "date": "2019-05-23"},
        {"name": "General Election 2024", "cat": "ELECTION", "date": "2024-06-04"},
        # Crises & Shocks
        {"name": "Taper Tantrum Panic", "cat": "CRISIS", "date": "2013-08-28"},
        {"name": "Demonetization Shock", "cat": "CRISIS", "date": "2016-11-08"},
        {"name": "IL&FS NBFC Crisis", "cat": "CRISIS", "date": "2018-09-21"},
        {"name": "COVID Lockdown Crash", "cat": "CRISIS", "date": "2020-03-23"}
    ]

    records = []
    for idx, ev in enumerate(macro_events, 1):
        dt_str = ev['date']

        # Regime at Event
        cursor.execute("SELECT * FROM (SELECT REGIME_NAME FROM STAGING.MARKET_REGIMES WHERE DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') ORDER BY DATETIME DESC) WHERE ROWNUM = 1", [dt_str])
        r_reg = cursor.fetchone()
        regime = r_reg[0] if r_reg else "CONSOLIDATION"

        # Pre 30D Market Return
        cursor.execute("""
            SELECT ROUND((AVG(c2.CLOSE) - AVG(c1.CLOSE)) / AVG(c1.CLOSE) * 100.0, 2)
            FROM STAGING.STOCK_HIST_DATA c1
            JOIN STAGING.STOCK_HIST_DATA c2 ON c1.SYMBOL = c2.SYMBOL
            WHERE c1.DATETIME = TO_DATE(:1, 'YYYY-MM-DD') - 30 AND c2.DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        """, [dt_str])
        r_pre = cursor.fetchone()
        pre_ret = float(r_pre[0]) if r_pre and r_pre[0] is not None else 0.0

        # Post 30D Market Return
        cursor.execute("""
            SELECT ROUND((AVG(c2.CLOSE) - AVG(c1.CLOSE)) / AVG(c1.CLOSE) * 100.0, 2)
            FROM STAGING.STOCK_HIST_DATA c1
            JOIN STAGING.STOCK_HIST_DATA c2 ON c1.SYMBOL = c2.SYMBOL
            WHERE c1.DATETIME = TO_DATE(:1, 'YYYY-MM-DD') AND c2.DATETIME = TO_DATE(:1, 'YYYY-MM-DD') + 30
        """, [dt_str])
        r_post = cursor.fetchone()
        post_ret = float(r_post[0]) if r_post and r_post[0] is not None else 0.0

        # Top sector post 30D
        cursor.execute("""
            SELECT * FROM (
                SELECT SECTOR_CODE FROM STAGING.SECTOR_ROTATION
                WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD') + 20 AND DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') + 40
                ORDER BY SECTOR_RANK_3M ASC
            ) WHERE ROWNUM = 1
        """, [dt_str])
        r_sec = cursor.fetchone()
        top_sec = r_sec[0] if r_sec else "ELECTRONIC_TECHNOLOGY"

        # Top theme post 30D
        cursor.execute("""
            SELECT * FROM (
                SELECT THEME_CODE FROM STAGING.THEME_ROTATION
                WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD') + 20 AND DATETIME <= TO_DATE(:1, 'YYYY-MM-DD') + 40
                ORDER BY THEME_RANK_3M ASC
            ) WHERE ROWNUM = 1
        """, [dt_str])
        r_thm = cursor.fetchone()
        top_thm = r_thm[0] if r_thm else "EV_MOBILITY"

        records.append((
            idx, ev['name'], ev['cat'], dt_str, regime, pre_ret, post_ret, top_sec, top_thm
        ))

    sql_insert = """
    INSERT INTO STAGING.EVIDENCE_MACRO_EVENTS (
        EVENT_ID, EVENT_NAME, EVENT_CATEGORY, EVENT_DATE, REGIME_AT_EVENT,
        PRE_30D_MARKET_RETURN, POST_30D_MARKET_RETURN, TOP_SECTOR_POST_30D, TOP_THEME_POST_30D
    ) VALUES (
        :1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5, :6, :7, :8, :9
    )
    """
    cursor.executemany(sql_insert, records)
    logger.info(f"✓ Inserted {len(records)} macro event evidence records into STAGING.EVIDENCE_MACRO_EVENTS")
    conn.commit()
    cursor.close()

def main():
    logger.info("=" * 70)
    logger.info(" HMIE Stage 4: Historical Evidence Engine Pipeline (v1.1.0)")
    logger.info("=" * 70)

    conn = get_db_connection()
    try:
        run_phase_1_corrections_evidence(conn)
        run_phase_2_macro_events_evidence(conn)
        logger.info("\n" + "=" * 70)
        logger.info(" STAGE 4 ETL COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
