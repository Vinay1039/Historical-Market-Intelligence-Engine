"""
===============================================================================
 HMIE Stage 9: Transaction Fee & Slippage Stress Test Pipeline (stage9_fee_sensitivity.py)
 Precomputes Strategy Performance Across Transaction Friction Levels (0.0%, 0.10%, 0.25%, 0.50%).
 Calculates Break-Even Fee % (vs NIFTY50), Max Sustainable Cost Threshold %, and Empirical Robustness Classifications in Oracle.
 Compliance: HMIE Constitution Laws 1-11 (v2.0.0 Baseline).
===============================================================================
"""

import sys
import os
import logging
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add workspace path
sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection

def calculate_net_metrics(gross_returns, fee_pct):
    """
    Applies round-trip friction fee_pct to monthly trade returns and computes net metrics.
    """
    if len(gross_returns) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    round_trip_cost = 2.0 * fee_pct
    net_rets = (np.array(gross_returns) - round_trip_cost) / 100.0

    eq_curve = np.cumprod(1.0 + net_rets) * 100.0
    tot_ret = float(eq_curve[-1] - 100.0)

    years = len(gross_returns) / 12.0
    cagr = float(((eq_curve[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0)

    running_max = np.maximum.accumulate(eq_curve)
    drawdowns = (eq_curve - running_max) / running_max * 100.0
    max_dd = float(np.min(drawdowns))

    wins = net_rets[net_rets > 0]
    losses = net_rets[net_rets < 0]

    sum_wins = float(np.sum(wins)) if len(wins) > 0 else 0.0001
    sum_losses = float(abs(np.sum(losses))) if len(losses) > 0 else 0.0001
    profit_factor = float(sum_wins / sum_losses)

    rf_monthly = 5.0 / 12.0 / 100.0
    excess = net_rets - rf_monthly
    mean_ex = float(np.mean(excess))
    std_mth = float(np.std(net_rets, ddof=1)) if len(net_rets) > 1 else 0.001
    if std_mth < 1e-6:
        std_mth = 0.001
    sharpe = float((mean_ex / std_mth) * np.sqrt(12))

    return round(tot_ret, 2), round(cagr, 2), round(max_dd, 2), round(sharpe, 2), round(profit_factor, 2)

def calculate_threshold_fees(gross_returns, bench_cagr=11.28):
    """
    Computes break-even fee % (vs benchmark) and max sustainable cost % (0.0% CAGR threshold).
    """
    g_rets = np.array(gross_returns) / 100.0
    years = len(g_rets) / 12.0

    # 1. Break-even fee vs benchmark
    f_be = 0.0
    for fee in np.linspace(0.0, 2.0, 2001):
        net_r = g_rets - (2.0 * fee / 100.0)
        eq = np.cumprod(1.0 + net_r) * 100.0
        cagr = ((eq[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0
        if cagr <= bench_cagr:
            f_be = fee
            break

    # 2. Max Sustainable Cost Threshold (CAGR <= 0%)
    f_max_cost = 0.0
    for fee in np.linspace(0.0, 2.0, 2001):
        net_r = g_rets - (2.0 * fee / 100.0)
        eq = np.cumprod(1.0 + net_r) * 100.0
        cagr = ((eq[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0
        if cagr <= 0.0:
            f_max_cost = fee
            break

    # Data-driven classification based on Max Sustainable Cost Threshold %
    if f_max_cost < 0.30:
        classification = "FRAGILE"
    elif 0.30 <= f_max_cost < 0.60:
        classification = "MODERATE"
    elif 0.60 <= f_max_cost < 0.90:
        classification = "ROBUST"
    else:
        classification = "EXCEPTIONAL"

    return round(float(f_be), 3), round(float(f_max_cost), 3), classification

def run_fee_sensitivity_engine(conn):
    logger.info("--- Stage 9: Computing Strategy Transaction Fee Sensitivity & Sustainable Cost Thresholds ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.STRATEGY_FEE_SENSITIVITY")

    fee_levels = [0.00, 0.10, 0.25, 0.50]
    strategies = ["SECTOR_ROTATION_TOP3", "THEME_MOMENTUM_TOP1", "TOP_STOCK_MOMENTUM_95P"]

    for scode in strategies:
        cursor.execute("""
            SELECT RETURN_PCT FROM STAGING.STRATEGY_TRADES
            WHERE STRATEGY_CODE = :1 ORDER BY TRADE_ID ASC
        """, [scode])
        g_rets = [r[0] for r in cursor.fetchall()]

        _, gross_cagr, _, _, _ = calculate_net_metrics(g_rets, 0.00)
        f_be, f_max_cost, classification = calculate_threshold_fees(g_rets, bench_cagr=11.28)

        for f in fee_levels:
            tot_ret, cagr, max_dd, sharpe, pf = calculate_net_metrics(g_rets, f)
            cagr_drag = round(gross_cagr - cagr, 2)

            cursor.execute("""
                INSERT INTO STAGING.STRATEGY_FEE_SENSITIVITY (
                    STRATEGY_CODE, FEE_LEVEL_PCT, NET_TOTAL_RETURN_PCT, NET_CAGR_PCT,
                    NET_MAX_DRAWDOWN_PCT, NET_SHARPE_RATIO, NET_PROFIT_FACTOR, CAGR_DRAG_PCT,
                    BREAK_EVEN_FEE_PCT, MAX_SUSTAINABLE_COST_PCT, ROBUSTNESS_CLASSIFICATION
                ) VALUES (
                    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11
                )
            """, [scode, f, tot_ret, cagr, max_dd, sharpe, pf, cagr_drag, f_be, f_max_cost, classification])

            logger.info(f"✓ Strategy [{scode}] @ Fee {f:.2f}%: Net CAGR={cagr:+.2f}% | MaxDD={max_dd:.2f}% | BreakEven={f_be:.3f}% | MaxCost={f_max_cost:.3f}% [{classification}]")

    conn.commit()
    cursor.close()
    logger.info("✓ Successfully populated Oracle STAGING.STRATEGY_FEE_SENSITIVITY with data-driven classifications")

def main():
    logger.info("=" * 70)
    logger.info(" HMIE Stage 9: Transaction Fee & Slippage Stress Test Engine Pipeline")
    logger.info("=" * 70)

    conn = get_db_connection()
    try:
        run_fee_sensitivity_engine(conn)
        logger.info("\n" + "=" * 70)
        logger.info(" STAGE 9 ETL COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
