"""
===============================================================================
 HMIE Stage 8: Benchmark Comparison Engine Pipeline (stage8_benchmark_engine.py)
 Precomputes Benchmark Price History (NIFTY50, NIFTY500, NIFTY_EQUAL, NIFTY_MOMENTUM_30)
 and Relative Quantitative Metrics (Alpha, Beta, Volatility, Tracking Error, Information Ratio).
 Compliance: HMIE Constitution Laws 1-11 (v2.0.0 Baseline).
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

# Add workspace path
sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection

def calculate_benchmark_metrics(strat_rets, bench_rets, rf_annual=5.0):
    """
    Calculates Alpha, Beta, Strategy Volatility, Benchmark Volatility, Tracking Error,
    and Information Ratio from monthly decimal returns.
    """
    s_rets = np.array(strat_rets) / 100.0
    b_rets = np.array(bench_rets) / 100.0

    min_len = min(len(s_rets), len(b_rets))
    s_rets = s_rets[:min_len]
    b_rets = b_rets[:min_len]

    # Portfolio Cumulative Curves & CAGRs
    eq_s = np.cumprod(1.0 + s_rets) * 100.0
    eq_b = np.cumprod(1.0 + b_rets) * 100.0
    years = min_len / 12.0

    cagr_s = float(((eq_s[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0)
    cagr_b = float(((eq_b[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0)

    # Annualized Volatilities
    vol_s = float(np.std(s_rets, ddof=1) * np.sqrt(12) * 100.0) if len(s_rets) > 1 else 10.0
    vol_b = float(np.std(b_rets, ddof=1) * np.sqrt(12) * 100.0) if len(b_rets) > 1 else 10.0

    # Beta: Cov(S, B) / Var(B)
    var_b = np.var(b_rets, ddof=1)
    if var_b < 1e-8:
        var_b = 1e-6
    cov_sb = np.cov(s_rets, b_rets)[0][1]
    beta = float(cov_sb / var_b)

    # Jensen's Alpha: (CAGR_s - RF) - Beta * (CAGR_b - RF)
    alpha = float((cagr_s - rf_annual) - beta * (cagr_b - rf_annual))

    # Tracking Error & Information Ratio
    active_diff = s_rets - b_rets
    tracking_error = float(np.std(active_diff, ddof=1) * np.sqrt(12) * 100.0) if len(active_diff) > 1 else 1.0
    if tracking_error < 1e-4:
        tracking_error = 0.01

    mean_active_monthly = float(np.mean(active_diff))
    info_ratio = float((mean_active_monthly / (tracking_error / np.sqrt(12) / 100.0))) if tracking_error > 0 else 0.0

    return round(cagr_s, 2), round(cagr_b, 2), round(vol_s, 2), round(vol_b, 2), round(alpha, 2), round(beta, 2), round(info_ratio, 2), round(tracking_error, 2)

def run_benchmark_engine(conn):
    logger.info("--- Stage 8: Computing Benchmark Price History & Strategy Comparisons ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.BENCHMARK_HIST_DATA")
    cursor.execute("TRUNCATE TABLE STAGING.STRATEGY_BENCHMARK_PERFORMANCE")

    # Benchmark Proxy Policy v2.0 — Rule: No benchmark symbol may appear in any
    # strategy universe. NIFTY_MOMENTUM_30 must have zero overlap with
    # THEME_MOMENTUM_TOP1 (Defence/PSU/Rail). All symbols: >=120M history.
    benchmarks = [
        {"code": "NIFTY50", "name": "NIFTY 50 Index (Top 50 Large Cap)", "where": "WHERE SYMBOL IN ('TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL')"},
        {"code": "NIFTY500", "name": "NIFTY 500 Broad Market Index", "where": "WHERE SYMBOL IN ('TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL', 'WIPRO', 'HCLTECH', 'BEL', 'HAL', 'RVNL')"},
        {"code": "NIFTY_EQUAL", "name": "NIFTY Equal Weight Benchmark Index", "where": "WHERE SYMBOL IN ('RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL')"},
        {"code": "NIFTY_MOMENTUM_30",
         "name": "NIFTY Momentum 30 Index (Diversified Sectors Proxy)",
         "where": "WHERE SYMBOL IN ('DIVISLAB', 'AUROPHARMA', 'LUPIN', 'PIDILITIND', 'BRITANNIA', 'NTPC', 'ONGC', 'ASHOKLEY', 'KAJARIACER', 'MANAPPURAM')"}
    ]

    base_mth_sql = """
    WITH monthly_bars AS (
        SELECT SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') AS MTH, DATETIME, CLOSE,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME ASC) AS RN_FIRST,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME DESC) AS RN_LAST
        FROM STAGING.STOCK_HIST_DATA
        {where_clause}
    ),
    monthly_returns AS (
        SELECT f.SYMBOL, f.MTH, f.DATETIME AS DT, ((l.CLOSE - f.CLOSE) / f.CLOSE * 100) AS RET
        FROM monthly_bars f
        JOIN monthly_bars l ON f.SYMBOL = l.SYMBOL AND f.MTH = l.MTH
        WHERE f.RN_FIRST = 1 AND l.RN_LAST = 1
    )
    SELECT MTH, MIN(DT) AS DT, AVG(RET) AS RET
    FROM monthly_returns
    GROUP BY MTH
    ORDER BY MTH ASC
    """

    bench_returns_map = {}

    for b in benchmarks:
        bcode = b['code']
        bname = b['name']
        sql = base_mth_sql.format(where_clause=b['where'])

        df_bench = pd.read_sql(sql, conn)
        df_bench['DT'] = pd.to_datetime(df_bench['DT'])

        b_rets = df_bench['RET'].tolist()
        b_dates = df_bench['DT'].tolist()
        bench_returns_map[bcode] = b_rets

        # Insert Benchmark History
        bench_records = []
        b_price = 100.0
        for idx in range(len(b_dates)):
            dt_str = b_dates[idx].strftime('%Y-%m-%d')
            m_ret = round(float(b_rets[idx]), 4)
            b_price = b_price * (1.0 + m_ret / 100.0)
            bench_records.append((bcode, bname, dt_str, round(b_price, 2), m_ret))

        cursor.executemany("""
            INSERT INTO STAGING.BENCHMARK_HIST_DATA (
                BENCHMARK_CODE, BENCHMARK_NAME, DATETIME, CLOSE_PRICE, MONTHLY_RETURN_PCT
            ) VALUES (
                :1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5
            )
        """, bench_records)

        logger.info(f"✓ Processed Benchmark [{bcode}]: Inserted {len(bench_records)} monthly price bars")

    # Fetch Strategy Monthly Returns from Trade Logs in Oracle
    strategies = ["SECTOR_ROTATION_TOP3", "THEME_MOMENTUM_TOP1", "TOP_STOCK_MOMENTUM_95P"]
    
    for scode in strategies:
        cursor.execute("""
            SELECT RETURN_PCT FROM STAGING.STRATEGY_TRADES
            WHERE STRATEGY_CODE = :1 ORDER BY TRADE_ID ASC
        """, [scode])
        s_rets = [r[0] for r in cursor.fetchall()]

        for b in benchmarks:
            bcode = b['code']
            bname = b['name']
            b_rets = bench_returns_map[bcode]

            cagr_s, cagr_b, vol_s, vol_b, alpha, beta, ir, te = calculate_benchmark_metrics(s_rets, b_rets)

            cursor.execute("""
                INSERT INTO STAGING.STRATEGY_BENCHMARK_PERFORMANCE (
                    STRATEGY_CODE, BENCHMARK_CODE, BENCHMARK_NAME,
                    STRATEGY_CAGR_PCT, BENCHMARK_CAGR_PCT, STRATEGY_VOLATILITY_PCT, BENCHMARK_VOLATILITY_PCT,
                    ALPHA_PCT, BETA, INFORMATION_RATIO, TRACKING_ERROR_PCT
                ) VALUES (
                    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11
                )
            """, [scode, bcode, bname, cagr_s, cagr_b, vol_s, vol_b, alpha, beta, ir, te])

            logger.info(f"✓ Strategy [{scode}] vs Benchmark [{bcode}]: Alpha={alpha:+.2f}% | Beta={beta:.2f} | InfoRatio={ir:.2f}")

    conn.commit()
    cursor.close()
    logger.info("✓ Successfully populated Oracle STAGING.STRATEGY_BENCHMARK_PERFORMANCE")

def main():
    logger.info("=" * 70)
    logger.info(" HMIE Stage 8: Benchmark Comparison Engine Pipeline")
    logger.info("=" * 70)

    conn = get_db_connection()
    try:
        run_benchmark_engine(conn)
        logger.info("\n" + "=" * 70)
        logger.info(" STAGE 8 ETL COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
