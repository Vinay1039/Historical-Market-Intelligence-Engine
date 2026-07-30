import os
import sys
import argparse
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import oracledb

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize Oracle Thick Client
try:
    oracledb.init_oracle_client(lib_dir=r"C:\instantclient_23_0")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
FYERS_HIST_DIR = BASE_DIR.parent
FYERS_DIR = FYERS_HIST_DIR / "Fyers"

# Setup Logging & Error persistence
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "stage3_execution.log"

logger = logging.getLogger("Stage3ETL")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Oracle DB connection params
DB_USER = os.getenv("ORACLE_DB_USER", "analysis")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD", "hr")
DB_HOST = os.getenv("ORACLE_DB_HOST", "localhost")
DB_PORT = os.getenv("ORACLE_DB_PORT", "1521")
DB_SERVICE_NAME = os.getenv("ORACLE_DB_SERVICE_NAME", "XE")

def get_db_connection():
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}"
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)

def run_phase_1_masters(conn):
    """Phase 1: Seed STAGING.SECTOR_MASTER and STAGING.INDUSTRY_MASTER from HR.STOCKS."""
    logger.info("\n--- Phase 1: Seeding SECTOR_MASTER and INDUSTRY_MASTER ---")
    cursor = conn.cursor()
    
    # 1. Clear existing masters cleanly
    cursor.execute("DELETE FROM STAGING.INDUSTRY_MASTER")
    cursor.execute("DELETE FROM STAGING.SECTOR_MASTER")
    conn.commit()

    # 2. Seed SECTOR_MASTER
    sql_sectors = """
    INSERT INTO STAGING.SECTOR_MASTER (SECTOR_CODE, SECTOR_NAME, STOCK_COUNT, TOTAL_MARKET_CAP)
    SELECT 
        REGEXP_REPLACE(UPPER(TRIM(SECTOR)), '[^A-Z0-9_]', '_') AS SECTOR_CODE,
        TRIM(SECTOR) AS SECTOR_NAME,
        COUNT(*) AS STOCK_COUNT,
        SUM(MARKET_CAP) AS TOTAL_MARKET_CAP
    FROM HR.STOCKS
    WHERE EXCHANGE = 'NSE' AND MARKET_CAP IS NOT NULL AND SECTOR IS NOT NULL
    GROUP BY TRIM(SECTOR)
    """
    cursor.execute(sql_sectors)
    sector_count = cursor.rowcount
    logger.info(f"✓ Inserted {sector_count} sectors into STAGING.SECTOR_MASTER")

    # 3. Seed INDUSTRY_MASTER
    sql_industries = """
    INSERT INTO STAGING.INDUSTRY_MASTER (INDUSTRY_CODE, INDUSTRY_NAME, SECTOR_CODE, STOCK_COUNT, TOTAL_MARKET_CAP)
    SELECT 
        REGEXP_REPLACE(UPPER(TRIM(INDUSTRY)), '[^A-Z0-9_]', '_') AS INDUSTRY_CODE,
        TRIM(INDUSTRY) AS INDUSTRY_NAME,
        REGEXP_REPLACE(UPPER(TRIM(SECTOR)), '[^A-Z0-9_]', '_') AS SECTOR_CODE,
        COUNT(*) AS STOCK_COUNT,
        SUM(MARKET_CAP) AS TOTAL_MARKET_CAP
    FROM HR.STOCKS
    WHERE EXCHANGE = 'NSE' AND MARKET_CAP IS NOT NULL AND SECTOR IS NOT NULL AND INDUSTRY IS NOT NULL
    GROUP BY TRIM(INDUSTRY), TRIM(SECTOR)
    """
    cursor.execute(sql_industries)
    ind_count = cursor.rowcount
    logger.info(f"✓ Inserted {ind_count} industries into STAGING.INDUSTRY_MASTER")

    conn.commit()
    cursor.close()

def run_phase_2_daily_aggregations(conn):
    """Phase 2: Aggregate daily price/indicator data into MARKET_BREADTH_DAILY, SECTOR_DAILY, and INDUSTRY_DAILY."""
    logger.info("\n--- Phase 2: Computing Daily Aggregations & Breadth Engine (MARKET, SECTOR, INDUSTRY) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.MARKET_BREADTH_DAILY")
    cursor.execute("TRUNCATE TABLE STAGING.SECTOR_DAILY")
    cursor.execute("TRUNCATE TABLE STAGING.INDUSTRY_DAILY")

    # 1. Aggregate MARKET_BREADTH_DAILY
    sql_market_breadth = """
    INSERT INTO STAGING.MARKET_BREADTH_DAILY (
        DATETIME, TOTAL_STOCKS, ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS,
        BREADTH_RATIO, NET_ADVANCES, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
    )
    SELECT 
        h.DATETIME,
        COUNT(*) AS TOTAL_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) AS ADVANCING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS DECLINING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT = 0 THEN 1 ELSE 0 END) AS UNCHANGED_STOCKS,
        ROUND(SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS BREADTH_RATIO,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) - SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS NET_ADVANCES,
        ROUND(SUM(CASE WHEN h.EMA_20 IS NOT NULL AND h.CLOSE > h.EMA_20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA20,
        ROUND(SUM(CASE WHEN h.EMA_50 IS NOT NULL AND h.CLOSE > h.EMA_50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA50,
        ROUND(SUM(CASE WHEN h.EMA_200 IS NOT NULL AND h.CLOSE > h.EMA_200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA200
    FROM STAGING.STOCK_HIST_DATA h
    GROUP BY h.DATETIME
    """
    cursor.execute(sql_market_breadth)
    mkt_cnt = cursor.rowcount
    logger.info(f"✓ Computed {mkt_cnt:,} daily market-wide breadth records")

    # 2. Aggregate SECTOR_DAILY
    sql_sector_daily = """
    INSERT INTO STAGING.SECTOR_DAILY (
        SECTOR_CODE, DATETIME, AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
        ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
        PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
    )
    SELECT 
        REGEXP_REPLACE(UPPER(TRIM(s.SECTOR)), '[^A-Z0-9_]', '_') AS SECTOR_CODE,
        h.DATETIME,
        ROUND(AVG(h.CHANGE_PERCENT), 4) AS AVG_CHANGE_PCT,
        ROUND(MEDIAN(h.CHANGE_PERCENT), 4) AS MEDIAN_CHANGE_PCT,
        SUM(h.VOLUME) AS TOTAL_VOLUME,
        ROUND(AVG(h.RSI_14), 4) AS AVG_RSI_14,
        COUNT(*) AS ACTIVE_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) AS ADVANCING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS DECLINING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT = 0 THEN 1 ELSE 0 END) AS UNCHANGED_STOCKS,
        ROUND(SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS BREADTH_RATIO,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) - SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS NET_ADVANCES,
        ROUND(SUM(CASE WHEN h.EMA_20 IS NOT NULL AND h.CLOSE > h.EMA_20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA20,
        ROUND(SUM(CASE WHEN h.EMA_50 IS NOT NULL AND h.CLOSE > h.EMA_50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA50,
        ROUND(SUM(CASE WHEN h.EMA_200 IS NOT NULL AND h.CLOSE > h.EMA_200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA200
    FROM STAGING.STOCK_HIST_DATA h
    JOIN HR.STOCKS s ON h.SYMBOL = s.SYMBOL
    WHERE s.EXCHANGE = 'NSE' AND s.SECTOR IS NOT NULL
    GROUP BY REGEXP_REPLACE(UPPER(TRIM(s.SECTOR)), '[^A-Z0-9_]', '_'), h.DATETIME
    """
    cursor.execute(sql_sector_daily)
    sec_daily_cnt = cursor.rowcount
    logger.info(f"✓ Computed {sec_daily_cnt:,} daily sector aggregate & breadth records")

    # 3. Aggregate INDUSTRY_DAILY
    sql_ind_daily = """
    INSERT INTO STAGING.INDUSTRY_DAILY (
        INDUSTRY_CODE, DATETIME, AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
        ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
        PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
    )
    SELECT 
        REGEXP_REPLACE(UPPER(TRIM(s.INDUSTRY)), '[^A-Z0-9_]', '_') AS INDUSTRY_CODE,
        h.DATETIME,
        ROUND(AVG(h.CHANGE_PERCENT), 4) AS AVG_CHANGE_PCT,
        ROUND(MEDIAN(h.CHANGE_PERCENT), 4) AS MEDIAN_CHANGE_PCT,
        SUM(h.VOLUME) AS TOTAL_VOLUME,
        ROUND(AVG(h.RSI_14), 4) AS AVG_RSI_14,
        COUNT(*) AS ACTIVE_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) AS ADVANCING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS DECLINING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT = 0 THEN 1 ELSE 0 END) AS UNCHANGED_STOCKS,
        ROUND(SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS BREADTH_RATIO,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) - SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS NET_ADVANCES,
        ROUND(SUM(CASE WHEN h.EMA_20 IS NOT NULL AND h.CLOSE > h.EMA_20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA20,
        ROUND(SUM(CASE WHEN h.EMA_50 IS NOT NULL AND h.CLOSE > h.EMA_50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA50,
        ROUND(SUM(CASE WHEN h.EMA_200 IS NOT NULL AND h.CLOSE > h.EMA_200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS PCT_ABOVE_EMA200
    FROM STAGING.STOCK_HIST_DATA h
    JOIN HR.STOCKS s ON h.SYMBOL = s.SYMBOL
    WHERE s.EXCHANGE = 'NSE' AND s.INDUSTRY IS NOT NULL
    GROUP BY REGEXP_REPLACE(UPPER(TRIM(s.INDUSTRY)), '[^A-Z0-9_]', '_'), h.DATETIME
    """
    cursor.execute(sql_ind_daily)
    ind_daily_cnt = cursor.rowcount
    logger.info(f"✓ Computed {ind_daily_cnt:,} daily industry aggregate & breadth records")

    conn.commit()
    cursor.close()

def run_phase_3_performance(conn):
    """Phase 3: Compute monthly, quarterly, annual, and CAGR stats for SECTOR_PERFORMANCE and INDUSTRY_PERFORMANCE."""
    logger.info("\n--- Phase 3: Computing Performance Stats (SECTOR_PERFORMANCE & INDUSTRY_PERFORMANCE) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.SECTOR_PERFORMANCE")
    cursor.execute("TRUNCATE TABLE STAGING.INDUSTRY_PERFORMANCE")

    # 1. Monthly & Quarterly performance per Sector
    sql_sector_performance = """
    INSERT INTO STAGING.SECTOR_PERFORMANCE (SECTOR_CODE, PERIOD_TYPE, PERIOD_LABEL, AVG_RETURN_PCT, WIN_RATE_PCT, VOLATILITY_PCT, SAMPLE_COUNT)
    SELECT 
        SECTOR_CODE,
        'MONTHLY' AS PERIOD_TYPE,
        TO_CHAR(DATETIME, 'Mon') AS PERIOD_LABEL,
        ROUND(AVG(AVG_CHANGE_PCT), 4) AS AVG_RETURN_PCT,
        ROUND(SUM(CASE WHEN AVG_CHANGE_PCT > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS WIN_RATE_PCT,
        ROUND(STDDEV(AVG_CHANGE_PCT), 4) AS VOLATILITY_PCT,
        COUNT(*) AS SAMPLE_COUNT
    FROM STAGING.SECTOR_DAILY
    GROUP BY SECTOR_CODE, TO_CHAR(DATETIME, 'Mon')
    """
    cursor.execute(sql_sector_performance)
    sec_perf_cnt = cursor.rowcount
    logger.info(f"✓ Inserted {sec_perf_cnt:,} monthly performance records into STAGING.SECTOR_PERFORMANCE")

    # 2. Monthly & Quarterly performance per Industry
    sql_ind_performance = """
    INSERT INTO STAGING.INDUSTRY_PERFORMANCE (INDUSTRY_CODE, PERIOD_TYPE, PERIOD_LABEL, AVG_RETURN_PCT, WIN_RATE_PCT, VOLATILITY_PCT, SAMPLE_COUNT)
    SELECT 
        INDUSTRY_CODE,
        'MONTHLY' AS PERIOD_TYPE,
        TO_CHAR(DATETIME, 'Mon') AS PERIOD_LABEL,
        ROUND(AVG(AVG_CHANGE_PCT), 4) AS AVG_RETURN_PCT,
        ROUND(SUM(CASE WHEN AVG_CHANGE_PCT > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS WIN_RATE_PCT,
        ROUND(STDDEV(AVG_CHANGE_PCT), 4) AS VOLATILITY_PCT,
        COUNT(*) AS SAMPLE_COUNT
    FROM STAGING.INDUSTRY_DAILY
    GROUP BY INDUSTRY_CODE, TO_CHAR(DATETIME, 'Mon')
    """
    cursor.execute(sql_ind_performance)
    ind_perf_cnt = cursor.rowcount
    logger.info(f"✓ Inserted {ind_perf_cnt:,} monthly performance records into STAGING.INDUSTRY_PERFORMANCE")

    conn.commit()
    cursor.close()

def compute_rotation_df(df_daily: pd.DataFrame, df_market: pd.DataFrame, entity_col: str) -> pd.DataFrame:
    """Computes rolling relative strength, dense ranks, rank deltas, and rotation status."""
    df = df_daily.copy()
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])
    df = df.sort_values(by=[entity_col, 'DATETIME']).reset_index(drop=True)

    df_mkt = df_market.copy()
    df_mkt['DATETIME'] = pd.to_datetime(df_mkt['DATETIME'])
    df_mkt = df_mkt.sort_values('DATETIME').reset_index(drop=True)

    df_mkt['MKT_RET_1M'] = df_mkt['AVG_CHANGE_PCT'].rolling(21, min_periods=1).sum()
    df_mkt['MKT_RET_3M'] = df_mkt['AVG_CHANGE_PCT'].rolling(63, min_periods=1).sum()
    df_mkt['MKT_RET_6M'] = df_mkt['AVG_CHANGE_PCT'].rolling(126, min_periods=1).sum()
    df_mkt['MKT_RET_12M'] = df_mkt['AVG_CHANGE_PCT'].rolling(252, min_periods=1).sum()

    mkt_map_1m = dict(zip(df_mkt['DATETIME'], df_mkt['MKT_RET_1M']))
    mkt_map_3m = dict(zip(df_mkt['DATETIME'], df_mkt['MKT_RET_3M']))
    mkt_map_6m = dict(zip(df_mkt['DATETIME'], df_mkt['MKT_RET_6M']))
    mkt_map_12m = dict(zip(df_mkt['DATETIME'], df_mkt['MKT_RET_12M']))

    df['RETURN_1M'] = df.groupby(entity_col)['AVG_CHANGE_PCT'].transform(lambda x: x.rolling(21, min_periods=1).sum()).round(4)
    df['RETURN_3M'] = df.groupby(entity_col)['AVG_CHANGE_PCT'].transform(lambda x: x.rolling(63, min_periods=1).sum()).round(4)
    df['RETURN_6M'] = df.groupby(entity_col)['AVG_CHANGE_PCT'].transform(lambda x: x.rolling(126, min_periods=1).sum()).round(4)
    df['RETURN_12M'] = df.groupby(entity_col)['AVG_CHANGE_PCT'].transform(lambda x: x.rolling(252, min_periods=1).sum()).round(4)

    df['MKT_1M'] = df['DATETIME'].map(mkt_map_1m).fillna(0)
    df['MKT_3M'] = df['DATETIME'].map(mkt_map_3m).fillna(0)
    df['MKT_6M'] = df['DATETIME'].map(mkt_map_6m).fillna(0)
    df['MKT_12M'] = df['DATETIME'].map(mkt_map_12m).fillna(0)

    df['RELATIVE_STRENGTH_1M'] = (df['RETURN_1M'] - df['MKT_1M']).round(4)
    df['RELATIVE_STRENGTH_3M'] = (df['RETURN_3M'] - df['MKT_3M']).round(4)
    df['RELATIVE_STRENGTH_6M'] = (df['RETURN_6M'] - df['MKT_6M']).round(4)
    df['RELATIVE_STRENGTH_12M'] = (df['RETURN_12M'] - df['MKT_12M']).round(4)

    df['RANK_1M'] = df.groupby('DATETIME')['RELATIVE_STRENGTH_1M'].rank(ascending=False, method='min').fillna(0).astype(int)
    df['RANK_3M'] = df.groupby('DATETIME')['RELATIVE_STRENGTH_3M'].rank(ascending=False, method='min').fillna(0).astype(int)
    df['RANK_12M'] = df.groupby('DATETIME')['RELATIVE_STRENGTH_12M'].rank(ascending=False, method='min').fillna(0).astype(int)

    df['RANK_3M_AGO'] = df.groupby(entity_col)['RANK_3M'].shift(63)
    df['RANK_DELTA_3M'] = (df['RANK_3M_AGO'] - df['RANK_3M']).fillna(0).astype(int)

    def get_status(row):
        rank = row['RANK_3M']
        rs3 = row['RELATIVE_STRENGTH_3M']
        delta = row['RANK_DELTA_3M']
        rank_ago = row['RANK_3M_AGO']

        if rank <= 5 and rs3 > 0:
            return 'LEADING'
        elif rank <= 10 and delta >= 3:
            return 'EMERGING'
        elif not pd.isna(rank_ago) and rank_ago <= 8 and delta <= -3:
            return 'WEAKENING'
        elif rank > 15 or rs3 < -5.0:
            return 'LAGGING'
        else:
            return 'NEUTRAL'

    df['ROTATION_STATUS'] = df.apply(get_status, axis=1)
    df['DATETIME_STR'] = df['DATETIME'].dt.strftime('%Y-%m-%d')
    return df

def run_phase_4_rotation_engine(conn):
    """Phase 4: Compute rolling relative strength, ranks, rank deltas, and rotation status."""
    logger.info("\n--- Phase 4: Computing Rotation Engine (SECTOR_ROTATION & INDUSTRY_ROTATION) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.SECTOR_ROTATION")
    cursor.execute("TRUNCATE TABLE STAGING.INDUSTRY_ROTATION")

    # Load market daily
    df_market = pd.read_sql("SELECT DATETIME, AVG_CHANGE_PCT FROM (SELECT DATETIME, ROUND(AVG(CHANGE_PERCENT),4) AS AVG_CHANGE_PCT FROM STAGING.STOCK_HIST_DATA GROUP BY DATETIME) ORDER BY DATETIME ASC", conn)
    
    # 1. Sector Rotation
    df_sec_daily = pd.read_sql("SELECT SECTOR_CODE, DATETIME, AVG_CHANGE_PCT FROM STAGING.SECTOR_DAILY ORDER BY SECTOR_CODE, DATETIME ASC", conn)
    df_sec_rot = compute_rotation_df(df_sec_daily, df_market, 'SECTOR_CODE')

    def cf(val):
        return None if pd.isna(val) else float(val)

    def ci(val):
        return None if pd.isna(val) else int(val)

    sec_records = [
        (
            r.SECTOR_CODE, r.DATETIME_STR,
            cf(r.RETURN_1M), cf(r.RETURN_3M), cf(r.RETURN_6M), cf(r.RETURN_12M),
            cf(r.RELATIVE_STRENGTH_1M), cf(r.RELATIVE_STRENGTH_3M), cf(r.RELATIVE_STRENGTH_6M), cf(r.RELATIVE_STRENGTH_12M),
            ci(r.RANK_1M), ci(r.RANK_3M), ci(r.RANK_12M), ci(r.RANK_DELTA_3M), r.ROTATION_STATUS
        )
        for r in df_sec_rot.itertuples(index=False)
    ]

    sql_sec_insert = """
    INSERT INTO STAGING.SECTOR_ROTATION (
        SECTOR_CODE, DATETIME, RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
        RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
        SECTOR_RANK_1M, SECTOR_RANK_3M, SECTOR_RANK_12M, RANK_DELTA_3M, ROTATION_STATUS
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15
    )
    """
    for i in range(0, len(sec_records), 10000):
        cursor.executemany(sql_sec_insert, sec_records[i:i+10000])
    logger.info(f"✓ Inserted {len(sec_records):,} sector rotation records into STAGING.SECTOR_ROTATION")

    # 2. Industry Rotation
    df_ind_daily = pd.read_sql("SELECT INDUSTRY_CODE, DATETIME, AVG_CHANGE_PCT FROM STAGING.INDUSTRY_DAILY ORDER BY INDUSTRY_CODE, DATETIME ASC", conn)
    df_ind_rot = compute_rotation_df(df_ind_daily, df_market, 'INDUSTRY_CODE')

    ind_records = [
        (
            r.INDUSTRY_CODE, r.DATETIME_STR,
            cf(r.RETURN_1M), cf(r.RETURN_3M), cf(r.RETURN_6M), cf(r.RETURN_12M),
            cf(r.RELATIVE_STRENGTH_1M), cf(r.RELATIVE_STRENGTH_3M), cf(r.RELATIVE_STRENGTH_6M), cf(r.RELATIVE_STRENGTH_12M),
            ci(r.RANK_1M), ci(r.RANK_3M), ci(r.RANK_12M), ci(r.RANK_DELTA_3M), r.ROTATION_STATUS
        )
        for r in df_ind_rot.itertuples(index=False)
    ]

    sql_ind_insert = """
    INSERT INTO STAGING.INDUSTRY_ROTATION (
        INDUSTRY_CODE, DATETIME, RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
        RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
        INDUSTRY_RANK_1M, INDUSTRY_RANK_3M, INDUSTRY_RANK_12M, RANK_DELTA_3M, ROTATION_STATUS
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15
    )
    """
    for i in range(0, len(ind_records), 10000):
        cursor.executemany(sql_ind_insert, ind_records[i:i+10000])
    logger.info(f"✓ Inserted {len(ind_records):,} industry rotation records into STAGING.INDUSTRY_ROTATION")

    conn.commit()
    cursor.close()

def run_phase_5_stock_rankings(conn):
    """Phase 5: Compute stock ranks & percentiles within Industry, Sector, and Market."""
    logger.info("\n--- Phase 5: Computing Stock Rankings (STAGING.STOCK_RANKINGS) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.STOCK_RANKINGS")

    # Load stock prices with sector & industry metadata
    sql_load = """
    SELECT 
        h.SYMBOL,
        h.DATETIME,
        REGEXP_REPLACE(UPPER(TRIM(s.SECTOR)), '[^A-Z0-9_]', '_') AS SECTOR_CODE,
        REGEXP_REPLACE(UPPER(TRIM(s.INDUSTRY)), '[^A-Z0-9_]', '_') AS INDUSTRY_CODE,
        h.CHANGE_PERCENT,
        h.RSI_14
    FROM STAGING.STOCK_HIST_DATA h
    JOIN HR.STOCKS s ON h.SYMBOL = s.SYMBOL
    WHERE s.EXCHANGE = 'NSE' AND s.SECTOR IS NOT NULL AND s.INDUSTRY IS NOT NULL
    """
    df_stocks = pd.read_sql(sql_load, conn)
    df_stocks['DATETIME'] = pd.to_datetime(df_stocks['DATETIME'])
    df_stocks = df_stocks.sort_values(by=['SYMBOL', 'DATETIME']).reset_index(drop=True)

    # 1. Compute rolling 3M (63-day) return per stock
    df_stocks['RETURN_3M'] = df_stocks.groupby('SYMBOL')['CHANGE_PERCENT'].transform(lambda x: x.rolling(63, min_periods=1).sum()).round(4)

    # 2. Compute Market Rank & Percentile per DATETIME
    df_stocks['MARKET_RANK'] = df_stocks.groupby('DATETIME')['RETURN_3M'].rank(ascending=False, method='min').fillna(0).astype(int)
    df_stocks['MKT_COUNT'] = df_stocks.groupby('DATETIME')['SYMBOL'].transform('count')
    df_stocks['MARKET_PERCENTILE'] = ((1 - (df_stocks['MARKET_RANK'] - 1) / df_stocks['MKT_COUNT']) * 100).round(2)

    # 3. Compute Sector Rank & Percentile per DATETIME + SECTOR_CODE
    df_stocks['SECTOR_RANK'] = df_stocks.groupby(['DATETIME', 'SECTOR_CODE'])['RETURN_3M'].rank(ascending=False, method='min').fillna(0).astype(int)
    df_stocks['SEC_COUNT'] = df_stocks.groupby(['DATETIME', 'SECTOR_CODE'])['SYMBOL'].transform('count')
    df_stocks['SECTOR_PERCENTILE'] = ((1 - (df_stocks['SECTOR_RANK'] - 1) / df_stocks['SEC_COUNT']) * 100).round(2)

    # 4. Compute Industry Rank & Percentile per DATETIME + INDUSTRY_CODE
    df_stocks['INDUSTRY_RANK'] = df_stocks.groupby(['DATETIME', 'INDUSTRY_CODE'])['RETURN_3M'].rank(ascending=False, method='min').fillna(0).astype(int)
    df_stocks['IND_COUNT'] = df_stocks.groupby(['DATETIME', 'INDUSTRY_CODE'])['SYMBOL'].transform('count')
    df_stocks['INDUSTRY_PERCENTILE'] = ((1 - (df_stocks['INDUSTRY_RANK'] - 1) / df_stocks['IND_COUNT']) * 100).round(2)

    # 5. Compute RSI Industry Rank per DATETIME + INDUSTRY_CODE
    df_stocks['RSI_RANK_INDUSTRY'] = df_stocks.groupby(['DATETIME', 'INDUSTRY_CODE'])['RSI_14'].rank(ascending=False, method='min').fillna(0).astype(int)

    df_stocks['DATETIME_STR'] = df_stocks['DATETIME'].dt.strftime('%Y-%m-%d')

    def cf(val):
        return None if pd.isna(val) else float(val)

    def ci(val):
        return None if pd.isna(val) else int(val)

    records = [
        (
            r.SYMBOL, r.DATETIME_STR, r.SECTOR_CODE, r.INDUSTRY_CODE,
            cf(r.RETURN_3M), ci(r.SECTOR_RANK), ci(r.INDUSTRY_RANK), ci(r.MARKET_RANK),
            cf(r.SECTOR_PERCENTILE), cf(r.INDUSTRY_PERCENTILE), cf(r.MARKET_PERCENTILE),
            ci(r.RSI_RANK_INDUSTRY)
        )
        for r in df_stocks.itertuples(index=False)
    ]

    sql_insert = """
    INSERT INTO STAGING.STOCK_RANKINGS (
        SYMBOL, DATETIME, SECTOR_CODE, INDUSTRY_CODE, RETURN_3M,
        SECTOR_RANK, INDUSTRY_RANK, MARKET_RANK,
        SECTOR_PERCENTILE, INDUSTRY_PERCENTILE, MARKET_PERCENTILE, RSI_RANK_INDUSTRY
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12
    )
    """
    batch_size = 25000
    for i in range(0, len(records), batch_size):
        cursor.executemany(sql_insert, records[i:i+batch_size])
        logger.info(f"  Inserted {min(i+batch_size, len(records)):,}/{len(records):,} stock ranking records")

    logger.info(f"✓ Inserted total {len(records):,} stock ranking records into STAGING.STOCK_RANKINGS")
    conn.commit()
    cursor.close()

def run_phase_6_theme_engine(conn):
    """Phase 6: Custom Theme Engine — Seed themes, compute daily aggregates, breadth, and theme rotation."""
    logger.info("\n--- Phase 6: Computing Custom Theme Engine (THEME_MASTER, THEME_CONSTITUENTS, THEME_DAILY, THEME_ROTATION) ---")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM STAGING.THEME_CONSTITUENTS")
    cursor.execute("DELETE FROM STAGING.THEME_MASTER")
    cursor.execute("TRUNCATE TABLE STAGING.THEME_DAILY")
    cursor.execute("TRUNCATE TABLE STAGING.THEME_ROTATION")

    # 1. Seed Themes & Stock Mapping
    themes = [
        ("DEFENCE_AEROSPACE", "Defence & Aerospace", "Shipbuilders, electronics, aerospace, and defence manufacturing"),
        ("RAILWAY_CAPEX", "Railway Infrastructure", "Rail EPC, rolling stock, wagon manufacturers, and rail telecom"),
        ("EV_MOBILITY", "EV & Battery Ecosystem", "EV manufacturers, battery tech, and auto ancillaries"),
        ("PSU_BANKS", "Public Sector Banks", "Public sector commercial banks"),
        ("POWER_RENEWABLES", "Power Generation & Renewables", "Thermal, hydro, solar generation, grid transmission, and power financing")
    ]

    constituents = [
        # Defence
        ("DEFENCE_AEROSPACE", "HAL"), ("DEFENCE_AEROSPACE", "BEL"), ("DEFENCE_AEROSPACE", "MAZDOCK"), 
        ("DEFENCE_AEROSPACE", "GRSE"), ("DEFENCE_AEROSPACE", "BDL"), ("DEFENCE_AEROSPACE", "SOLARINDS"), ("DEFENCE_AEROSPACE", "DATAPATT"),
        # Railway
        ("RAILWAY_CAPEX", "RVNL"), ("RAILWAY_CAPEX", "IRFC"), ("RAILWAY_CAPEX", "IRCON"), 
        ("RAILWAY_CAPEX", "TITAGARH"), ("RAILWAY_CAPEX", "TEXRAIL"), ("RAILWAY_CAPEX", "RAILTEL"),
        # EV Mobility
        ("EV_MOBILITY", "TATAMOTORS"), ("EV_MOBILITY", "AMARAJABAT"), ("EV_MOBILITY", "EXIDEIND"), 
        ("EV_MOBILITY", "OLECTRA"), ("EV_MOBILITY", "JBMMA"),
        # PSU Banks
        ("PSU_BANKS", "SBIN"), ("PSU_BANKS", "BANKBARODA"), ("PSU_BANKS", "PNB"), 
        ("PSU_BANKS", "CANBK"), ("PSU_BANKS", "UNIONBANK"), ("PSU_BANKS", "INDIANB"),
        # Power & Renewables
        ("POWER_RENEWABLES", "NTPC"), ("POWER_RENEWABLES", "POWERGRID"), ("POWER_RENEWABLES", "TATAPOWER"), 
        ("POWER_RENEWABLES", "SUZLON"), ("POWER_RENEWABLES", "IREDA"), ("POWER_RENEWABLES", "NHPC")
    ]

    for code, name, desc in themes:
        stock_cnt = sum(1 for c in constituents if c[0] == code)
        cursor.execute("INSERT INTO STAGING.THEME_MASTER (THEME_CODE, THEME_NAME, DESCRIPTION, STOCK_COUNT) VALUES (:1, :2, :3, :4)",
                       [code, name, desc, stock_cnt])

    for code, sym in constituents:
        cursor.execute("INSERT INTO STAGING.THEME_CONSTITUENTS (THEME_CODE, SYMBOL, WEIGHT) VALUES (:1, :2, 1.0)", [code, sym])

    conn.commit()
    logger.info(f"✓ Seeded {len(themes)} custom themes and {len(constituents)} constituent mappings")

    # 2. Compute Theme Daily Aggregations & Breadth
    sql_theme_daily = """
    INSERT INTO STAGING.THEME_DAILY (
        THEME_CODE, DATETIME, AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
        ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
        PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
    )
    SELECT 
        c.THEME_CODE,
        h.DATETIME,
        ROUND(AVG(h.CHANGE_PERCENT), 4) AS AVG_CHANGE_PCT,
        ROUND(MEDIAN(h.CHANGE_PERCENT), 4) AS MEDIAN_CHANGE_PCT,
        SUM(h.VOLUME) AS TOTAL_VOLUME,
        ROUND(AVG(h.RSI_14), 4) AS AVG_RSI_14,
        COUNT(*) AS ACTIVE_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) AS ADVANCING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS DECLINING_STOCKS,
        SUM(CASE WHEN h.CHANGE_PERCENT = 0 THEN 1 ELSE 0 END) AS UNCHANGED_STOCKS,
        ROUND(
            SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) * 1.0 / 
            NULLIF(SUM(CASE WHEN h.CHANGE_PERCENT < 0 THEN 1 ELSE 0 END), 0), 4
        ) AS BREADTH_RATIO,
        SUM(CASE WHEN h.CHANGE_PERCENT > 0 THEN 1 ELSE -1 END) AS NET_ADVANCES,
        ROUND(SUM(CASE WHEN h.CLOSE > h.EMA_20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS PCT_ABOVE_EMA20,
        ROUND(SUM(CASE WHEN h.CLOSE > h.EMA_50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS PCT_ABOVE_EMA50,
        ROUND(SUM(CASE WHEN h.CLOSE > h.EMA_200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS PCT_ABOVE_EMA200
    FROM STAGING.THEME_CONSTITUENTS c
    JOIN STAGING.STOCK_HIST_DATA h ON c.SYMBOL = h.SYMBOL
    GROUP BY c.THEME_CODE, h.DATETIME
    """
    cursor.execute(sql_theme_daily)
    theme_daily_cnt = cursor.rowcount
    logger.info(f"✓ Inserted {theme_daily_cnt:,} daily theme aggregate records into STAGING.THEME_DAILY")

    # 3. Compute Theme Rotation
    df_market = pd.read_sql("SELECT DATETIME, AVG_CHANGE_PCT FROM (SELECT DATETIME, ROUND(AVG(CHANGE_PERCENT),4) AS AVG_CHANGE_PCT FROM STAGING.STOCK_HIST_DATA GROUP BY DATETIME) ORDER BY DATETIME ASC", conn)
    df_thm_daily = pd.read_sql("SELECT THEME_CODE, DATETIME, AVG_CHANGE_PCT FROM STAGING.THEME_DAILY ORDER BY THEME_CODE, DATETIME ASC", conn)
    df_thm_rot = compute_rotation_df(df_thm_daily, df_market, 'THEME_CODE')

    def cf(val):
        return None if pd.isna(val) else float(val)

    def ci(val):
        return None if pd.isna(val) else int(val)

    thm_records = [
        (
            r.THEME_CODE, r.DATETIME_STR,
            cf(r.RETURN_1M), cf(r.RETURN_3M), cf(r.RETURN_6M), cf(r.RETURN_12M),
            cf(r.RELATIVE_STRENGTH_1M), cf(r.RELATIVE_STRENGTH_3M), cf(r.RELATIVE_STRENGTH_6M), cf(r.RELATIVE_STRENGTH_12M),
            ci(r.RANK_3M), ci(r.RANK_DELTA_3M), r.ROTATION_STATUS
        )
        for r in df_thm_rot.itertuples(index=False)
    ]

    sql_thm_insert = """
    INSERT INTO STAGING.THEME_ROTATION (
        THEME_CODE, DATETIME, RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
        RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
        THEME_RANK_3M, RANK_DELTA_3M, ROTATION_STATUS
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13
    )
    """
    for i in range(0, len(thm_records), 5000):
        cursor.executemany(sql_thm_insert, thm_records[i:i+5000])
    logger.info(f"✓ Inserted {len(thm_records):,} theme rotation records into STAGING.THEME_ROTATION")

    conn.commit()
    cursor.close()

def run_phase_7_regime_engine(conn):
    """Phase 7: Historical Regime Engine — Classifies daily macro market regimes & duration."""
    logger.info("\n--- Phase 7: Computing Historical Regime Engine (STAGING.MARKET_REGIMES) ---")
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE STAGING.MARKET_REGIMES")

    # Load market breadth and average market daily return
    sql_load = """
    SELECT 
        mb.DATETIME,
        mb.PCT_ABOVE_EMA20,
        mb.PCT_ABOVE_EMA50,
        mb.PCT_ABOVE_EMA200,
        mb.BREADTH_RATIO,
        mb.NET_ADVANCES,
        mkt.AVG_MARKET_RETURN_PCT
    FROM STAGING.MARKET_BREADTH_DAILY mb
    JOIN (
        SELECT DATETIME, ROUND(AVG(CHANGE_PERCENT), 4) AS AVG_MARKET_RETURN_PCT
        FROM STAGING.STOCK_HIST_DATA
        GROUP BY DATETIME
    ) mkt ON mb.DATETIME = mkt.DATETIME
    ORDER BY mb.DATETIME ASC
    """
    df = pd.read_sql(sql_load, conn)
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])

    def get_regime(row):
        p200 = row['PCT_ABOVE_EMA200'] or 0
        p50 = row['PCT_ABOVE_EMA50'] or 0
        br = row['BREADTH_RATIO'] or 0

        if p200 >= 60.0 and p50 >= 50.0 and br >= 1.0:
            return 'BULL_EXPANSION'
        elif p200 >= 55.0 and p50 < 45.0:
            return 'BULL_CORRECTION'
        elif p200 < 40.0 and p50 < 35.0:
            return 'BEAR_MARKET'
        elif p200 < 40.0 and p50 >= 50.0:
            return 'BEAR_REBOUND'
        else:
            return 'CONSOLIDATION'

    df['REGIME_NAME'] = df.apply(get_regime, axis=1)

    # Compute consecutive regime duration
    durations = []
    current_regime = None
    curr_dur = 0
    for reg in df['REGIME_NAME']:
        if reg == current_regime:
            curr_dur += 1
        else:
            current_regime = reg
            curr_dur = 1
        durations.append(curr_dur)

    df['REGIME_DURATION_DAYS'] = durations
    df['DATETIME_STR'] = df['DATETIME'].dt.strftime('%Y-%m-%d')

    def cf(val):
        return None if pd.isna(val) else float(val)

    def ci(val):
        return None if pd.isna(val) else int(val)

    records = [
        (
            r.DATETIME_STR, r.REGIME_NAME,
            cf(r.PCT_ABOVE_EMA20), cf(r.PCT_ABOVE_EMA50), cf(r.PCT_ABOVE_EMA200),
            cf(r.BREADTH_RATIO), ci(r.NET_ADVANCES), cf(r.AVG_MARKET_RETURN_PCT), ci(r.REGIME_DURATION_DAYS)
        )
        for r in df.itertuples(index=False)
    ]

    sql_insert = """
    INSERT INTO STAGING.MARKET_REGIMES (
        DATETIME, REGIME_NAME, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200,
        BREADTH_RATIO, NET_ADVANCES, AVG_MARKET_RETURN_PCT, REGIME_DURATION_DAYS
    ) VALUES (
        TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4, :5, :6, :7, :8, :9
    )
    """
    for i in range(0, len(records), 5000):
        cursor.executemany(sql_insert, records[i:i+5000])

    logger.info(f"✓ Inserted total {len(records):,} macro market regime records into STAGING.MARKET_REGIMES")
    conn.commit()
    cursor.close()

def main():
    logger.info("=" * 65)
    logger.info(" STAGE 3.6: Market Structure, Rotation, Ranking, Theme & Regime Engine ETL")
    logger.info("=" * 65)

    conn = get_db_connection()
    try:
        run_phase_1_masters(conn)
        run_phase_2_daily_aggregations(conn)
        run_phase_3_performance(conn)
        run_phase_4_rotation_engine(conn)
        run_phase_5_stock_rankings(conn)
        run_phase_6_theme_engine(conn)
        run_phase_7_regime_engine(conn)
        logger.info("\n" + "=" * 65)
        logger.info(" STAGE 3.6 ETL COMPLETED SUCCESSFULLY")
        logger.info("=" * 65)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
