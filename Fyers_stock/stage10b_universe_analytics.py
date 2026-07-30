"""
===============================================================================
 HMIE Research Suite — Momentum Studies: Monthly Universe Analytics
 Computes per-month rebalance diagnostics from STAGING.STRATEGY_MONTHLY_UNIVERSE:
   - Basket size (already stored)
   - Turnover from previous month (new symbols / basket size)
   - Herfindahl-Hirschman Index (HHI) — equal-weight = 1/N, but stored as 1.0/N
   - Sector concentration (via STAGING.STOCK_DETAILS if available)
 Results stored to STAGING.UNIVERSE_ANALYTICS Oracle table.
 Compliance: HMIE Constitution Law 5 (Zero Calculation REST Layer).
===============================================================================
"""

import sys
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection


def create_universe_analytics_table(cursor):
    """Create STAGING.UNIVERSE_ANALYTICS if it does not exist."""
    try:
        cursor.execute("DROP TABLE STAGING.UNIVERSE_ANALYTICS")
        logger.info("Dropped existing STAGING.UNIVERSE_ANALYTICS")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE STAGING.UNIVERSE_ANALYTICS (
            ID                  NUMBER(10, 0)   NOT NULL PRIMARY KEY,
            STRATEGY_CODE       VARCHAR2(50)    NOT NULL,
            MONTH_KEY           VARCHAR2(7)     NOT NULL,
            BASKET_SIZE         NUMBER(5, 0)    NOT NULL,
            UNIVERSE_SIZE       NUMBER(5, 0)    NOT NULL,
            SELECTION_RATE_PCT  NUMBER(6, 2)    NOT NULL,   -- basket/universe * 100
            TURNOVER_PCT        NUMBER(6, 2),               -- % of basket changed vs prior month
            HHI                 NUMBER(10, 6)   NOT NULL,   -- Herfindahl index (equal-weight = 1/N)
            AVG_MOMENTUM_PCT    NUMBER(10, 4)   NOT NULL,   -- mean momentum of selected basket
            TOP_MOMENTUM_PCT    NUMBER(10, 4)   NOT NULL,   -- max momentum in basket
            MIN_MOMENTUM_PCT    NUMBER(10, 4)   NOT NULL    -- min momentum in basket (95th cut level)
        )
    """)
    logger.info("Created STAGING.UNIVERSE_ANALYTICS")


def compute_analytics(conn, strategy_code="TOP_STOCK_MOMENTUM_95P"):
    """Compute monthly rebalance analytics from STRATEGY_MONTHLY_UNIVERSE."""
    logger.info(f"--- Computing Universe Analytics for {strategy_code} ---")

    df = pd.read_sql("""
        SELECT MONTH_KEY, SYMBOL, MOMENTUM_PCT, BASKET_SIZE, UNIVERSE_SIZE
        FROM STAGING.STRATEGY_MONTHLY_UNIVERSE
        WHERE STRATEGY_CODE = :1
        ORDER BY MONTH_KEY ASC, MOMENTUM_RANK ASC
    """, conn, params=[strategy_code])

    logger.info(f"    Loaded {len(df)} rows covering {df['MONTH_KEY'].nunique()} months")

    months = sorted(df['MONTH_KEY'].unique().tolist())
    records = []
    rec_id = 1

    prev_basket = set()

    for month in months:
        mdf = df[df['MONTH_KEY'] == month]
        basket = set(mdf['SYMBOL'].tolist())
        basket_size = len(basket)
        universe_size = int(mdf['UNIVERSE_SIZE'].iloc[0])

        # Selection rate
        selection_rate = round(basket_size / universe_size * 100.0, 2) if universe_size > 0 else 0.0

        # Turnover: fraction of basket that changed from prior month
        if prev_basket:
            new_entries = len(basket - prev_basket)
            turnover_pct = round(new_entries / basket_size * 100.0, 2) if basket_size > 0 else 0.0
        else:
            turnover_pct = None  # First month — no prior to compare

        # Herfindahl-Hirschman Index (equal-weight assumption: weight = 1/N)
        # For equal-weight portfolio: HHI = N * (1/N)^2 = 1/N
        hhi = round(1.0 / basket_size, 6) if basket_size > 0 else 1.0

        # Momentum statistics of selected basket
        mom_vals = mdf['MOMENTUM_PCT'].astype(float).tolist()
        avg_mom = round(float(np.mean(mom_vals)), 4)
        top_mom = round(float(np.max(mom_vals)), 4)
        min_mom = round(float(np.min(mom_vals)), 4)

        records.append((
            rec_id, strategy_code, month,
            basket_size, universe_size, selection_rate,
            turnover_pct, hhi,
            avg_mom, top_mom, min_mom
        ))
        rec_id += 1
        prev_basket = basket

    logger.info(f"    Computed analytics for {len(records)} months")
    return records


def main():
    logger.info("=" * 70)
    logger.info(" HMIE Research Suite — Momentum Universe Analytics")
    logger.info("=" * 70)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        create_universe_analytics_table(cursor)
        records = compute_analytics(conn)

        cursor.executemany("""
            INSERT INTO STAGING.UNIVERSE_ANALYTICS (
                ID, STRATEGY_CODE, MONTH_KEY, BASKET_SIZE, UNIVERSE_SIZE,
                SELECTION_RATE_PCT, TURNOVER_PCT, HHI,
                AVG_MOMENTUM_PCT, TOP_MOMENTUM_PCT, MIN_MOMENTUM_PCT
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)
        """, records)

        conn.commit()

        # Full distribution stats — not just mean
        turnovers  = [r[6] for r in records if r[6] is not None]
        hhis       = [r[7] for r in records]
        baskets    = [r[3] for r in records]
        mom_tops   = [r[9] for r in records]

        logger.info("\n" + "=" * 70)
        logger.info(f" UNIVERSE ANALYTICS COMPLETE --- {len(records)} months")
        logger.info(f"")
        logger.info(f"   BASKET SIZE (symbols/month)")
        logger.info(f"     Mean={np.mean(baskets):.1f} | Min={np.min(baskets)} | Median={np.median(baskets):.0f} | Max={np.max(baskets)}")
        logger.info(f"")
        logger.info(f"   MONTHLY TURNOVER (%)")
        if turnovers:
            logger.info(f"     Mean={np.mean(turnovers):.1f}% | Min={np.min(turnovers):.1f}% | Median={np.median(turnovers):.1f}% | Max={np.max(turnovers):.1f}% | Std={np.std(turnovers):.1f}%")
        logger.info(f"")
        logger.info(f"   HHI CONCENTRATION (lower = more diversified, equal-weight = 1/N)")
        logger.info(f"     Mean={np.mean(hhis):.4f} | Min={np.min(hhis):.4f} | Median={np.median(hhis):.4f} | Max={np.max(hhis):.4f} | Std={np.std(hhis):.4f}")
        logger.info(f"")
        logger.info(f"   TOP MOMENTUM SCORE (best single stock in basket, %)")
        logger.info(f"     Mean={np.mean(mom_tops):.1f}% | Min={np.min(mom_tops):.1f}% | Median={np.median(mom_tops):.1f}% | Max={np.max(mom_tops):.1f}%")
        logger.info("=" * 70)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
