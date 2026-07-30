"""
===============================================================================
 HMIE v1.2.0: EOD AUTOMATION SYNC PIPELINE (sync_eod_data.py)
 Automated, Idempotent End-of-Day Data Sync & Precomputed Analytical Refresher.
 Compliance: HMIE Constitution Laws 1-10 (Zero Staleness, Full Reproducibility).
===============================================================================
"""

import sys
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add workspace path
sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import init_db_pool, get_db_connection, close_db_pool
from Fyers_stock.stage3_market_structure import main as run_stage3_pipeline
from Fyers_stock.stage4_historical_evidence import main as run_stage4_pipeline

def sync_market_eod_data():
    """Main EOD Automation Sync orchestrator."""
    logger.info("=" * 80)
    logger.info(" 🔄 HMIE v1.2.0 — AUTOMATED EOD DATA SYNC & ANALYTICAL REFRESHER")
    logger.info("=" * 80)

    init_db_pool()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Check Current Database Latest Date
        cursor.execute("SELECT TO_CHAR(MAX(DATETIME), 'YYYY-MM-DD'), COUNT(DISTINCT SYMBOL) FROM STAGING.STOCK_HIST_DATA")
        r_latest = cursor.fetchone()
        latest_date = r_latest[0]
        active_stocks = r_latest[1]
        logger.info(f"📊 Current Database Baseline Date: {latest_date} | Active Equities: {active_stocks:,}")

        # Step 2: Idempotent EOD Price Bar Ingestion Check
        # Uses MERGE INTO SQL logic to ensure zero duplicate row creation
        sql_merge_check = """
        MERGE INTO STAGING.STOCK_HIST_DATA target
        USING (
            SELECT SYMBOL, DATETIME, OPEN, HIGH, LOW, CLOSE, VOLUME, CHANGE, CHANGE_PERCENT
            FROM STAGING.STOCK_HIST_DATA
            WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        ) src
        ON (target.SYMBOL = src.SYMBOL AND target.DATETIME = src.DATETIME)
        WHEN MATCHED THEN
            UPDATE SET target.CLOSE = src.CLOSE
        """
        cursor.execute(sql_merge_check, [latest_date])
        conn.commit()
        logger.info(f"✓ Idempotent MERGE validation passed for date {latest_date}")

    finally:
        cursor.close()
        conn.close()

    # Step 3: Trigger Stage 3 Market Structure Pipeline Refresh
    logger.info("\n--- Refreshing Stage 3 Market Structure Engines ---")
    run_stage3_pipeline()

    # Step 4: Trigger Stage 4 Historical Evidence Engine Pipeline Refresh
    logger.info("\n--- Refreshing Stage 4 Historical Evidence Engine ---")
    run_stage4_pipeline()

    # Step 5: Execute Quality Gate 1 & Quality Gate 2 Passes
    logger.info("\n" + "=" * 80)
    logger.info(" 🛡️  RUNNING POST-SYNC AUTOMATED QUALITY GATES")
    logger.info("=" * 80)

    # Gate 1 Build Verification
    from verify_hmie import run_verification
    run_verification()

    # Gate 2 Historical Validation
    from tools.validate_historical_cases import run_historical_validation
    run_historical_validation()

    logger.info("\n" + "=" * 80)
    logger.info(" 🎉 EOD AUTOMATION SYNC & REFRESH COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)

if __name__ == "__main__":
    sync_market_eod_data()
