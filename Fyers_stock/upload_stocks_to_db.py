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

# Paths
BASE_DIR = Path(__file__).resolve().parent
FYERS_HIST_DIR = BASE_DIR.parent
FYERS_DIR = FYERS_HIST_DIR / "Fyers"

# Setup Logging & Error persistence
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "pipeline_errors.log"
FAILED_CSV = BASE_DIR / "failed_symbols.csv"

# Configure logging to console AND log file
logger = logging.getLogger("StockETL")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Load environment credentials
ENV_PATH = FYERS_DIR / "fyers.env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

sys.path.insert(0, str(FYERS_HIST_DIR))
sys.path.insert(0, str(FYERS_DIR))

from download.downloader import DownloadPipeline
import download.downloader as downloader_mod
import download.csv_writer as csv_writer_mod

OUTPUT_FOLDER = BASE_DIR / "Historical_Data"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
downloader_mod.OUTPUT_FOLDER = OUTPUT_FOLDER
csv_writer_mod.OUTPUT_FOLDER = OUTPUT_FOLDER

# Oracle DB connection params
DB_USER = os.getenv("ORACLE_DB_USER", "analysis")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD", "hr")
DB_HOST = os.getenv("ORACLE_DB_HOST", "localhost")
DB_PORT = os.getenv("ORACLE_DB_PORT", "1521")
DB_SERVICE_NAME = os.getenv("ORACLE_DB_SERVICE_NAME", "XE")

def record_failed_symbol(symbol: str, stage: str, error_msg: str):
    """Records failed symbol details into failed_symbols.csv for tracking & retry."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_err = pd.DataFrame([{
        'TIMESTAMP': timestamp,
        'SYMBOL': symbol,
        'STAGE': stage,
        'ERROR': str(error_msg)
    }])
    header = not FAILED_CSV.exists()
    df_err.to_csv(FAILED_CSV, mode='a', index=False, header=header)

def get_db_connection():
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}"
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)

def ensure_tables_exist(conn):
    """Ensures STAGING.RAW_STOCK_HISTORY table exists in Oracle."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM STAGING.RAW_STOCK_HISTORY WHERE ROWNUM = 1")
    except Exception:
        logger.info("Creating table STAGING.RAW_STOCK_HISTORY...")
        ddl = """
        CREATE TABLE STAGING.RAW_STOCK_HISTORY (
            SYMBOL     VARCHAR2(50) NOT NULL, 
            DATETIME   DATE NOT NULL, 
            OPEN       NUMBER(12,4), 
            HIGH       NUMBER(12,4), 
            LOW        NUMBER(12,4), 
            CLOSE      NUMBER(12,4), 
            VOLUME     NUMBER(15,0),
            CREATED_AT DATE DEFAULT SYSDATE,
            CONSTRAINT PK_RAW_STOCK_HISTORY PRIMARY KEY (SYMBOL, DATETIME)
        )
        """
        try:
            cursor.execute(ddl)
            conn.commit()
            logger.info("✓ Table STAGING.RAW_STOCK_HISTORY created successfully.")
        except Exception as e:
            logger.warning(f"Notice regarding STAGING.RAW_STOCK_HISTORY creation: {e}")
    finally:
        cursor.close()

def pandas_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def pandas_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return pd.DataFrame({
        'MACD': macd_line,
        'MACD_SIGNAL': signal_line,
        'MACD_HIST': macd_hist
    }, index=series.index)

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates all 40 quantitative technical indicator columns for stock DataFrame using vectorized operations."""
    if df.empty:
        return df

    df_calc = df.copy()
    df_calc.columns = df_calc.columns.str.upper()

    if 'DATE' in df_calc.columns and 'DATETIME' not in df_calc.columns:
        df_calc = df_calc.rename(columns={'DATE': 'DATETIME'})

    df_calc['_SORT_DATE'] = pd.to_datetime(df_calc['DATETIME'])
    df_calc = df_calc.sort_values(by=['SYMBOL', '_SORT_DATE'], ascending=[True, True]).reset_index(drop=True)

    # 1. Day changes 
    df_calc['PREVIOUS_CLOSE'] = df_calc.groupby('SYMBOL')['CLOSE'].shift(1)
    df_calc['CHANGE'] = df_calc['CLOSE'] - df_calc['PREVIOUS_CLOSE']
    df_calc['CHANGE_PERCENT'] = (df_calc['CHANGE'] * 100 / df_calc['PREVIOUS_CLOSE']).round(2)

    # 2. Daily limits
    df_calc['LOW_CLOSE'] = df_calc['CLOSE'] - df_calc['LOW']
    df_calc['HIGH_CLOSE'] = df_calc['CLOSE'] - df_calc['HIGH']
    df_calc['TOTAL_LOW_HIGH'] = df_calc['HIGH'] - df_calc['LOW']

    # 3. Gap logic
    df_calc['GAP'] = np.where(
        df_calc['OPEN'] > df_calc['PREVIOUS_CLOSE'], 'gap up',
        np.where(
            df_calc['OPEN'] < df_calc['PREVIOUS_CLOSE'], 'gap down',
            'no gap'
        )
    )
    df_calc['GAP_PERCENT'] = ((df_calc['OPEN'] - df_calc['PREVIOUS_CLOSE']) * 100 / df_calc['PREVIOUS_CLOSE']).round(2)

    # 4. Directional 2-Day Span calculations
    df_calc['PREV_HIGH'] = df_calc.groupby('SYMBOL')['HIGH'].shift(1)
    df_calc['PREV_LOW'] = df_calc.groupby('SYMBOL')['LOW'].shift(1)

    df_calc['TOTAL_PREV_LOW_HIGH'] = np.where(
        df_calc['CLOSE'] >= df_calc['PREVIOUS_CLOSE'],
        df_calc['HIGH'] - df_calc['PREV_LOW'],
        df_calc['PREV_HIGH'] - df_calc['LOW']
    ).round(2)

    df_calc['TOTAL_PREV_LOW_HIGH_PERCENT'] = ((df_calc['TOTAL_PREV_LOW_HIGH'] * 100.0) / df_calc['PREVIOUS_CLOSE']).round(2)
    df_calc.drop(columns=['PREV_HIGH', 'PREV_LOW'], inplace=True)

    # 5. Wicks
    df_calc['UPPER_WICK'] = (df_calc['HIGH'] - df_calc[['OPEN','CLOSE']].max(axis=1)).round(2)
    df_calc['LOWER_WICK'] = (df_calc[['OPEN','CLOSE']].min(axis=1) - df_calc['LOW']).round(2)

    # 6. 52-week High/Low
    df_calc['HIGH_52W'] = df_calc.groupby('SYMBOL')['HIGH'].transform(lambda x: x.rolling(252).max())
    df_calc['LOW_52W'] = df_calc.groupby('SYMBOL')['LOW'].transform(lambda x: x.rolling(252).min())

    # 7. Distances to 52-week high/low
    df_calc['DIST_HIGH52'] = ((df_calc['CLOSE'] - df_calc['HIGH_52W']) * 100 / df_calc['HIGH_52W']).round(2)
    df_calc['DIST_LOW52'] = ((df_calc['CLOSE'] - df_calc['LOW_52W']) * 100 / df_calc['LOW_52W']).round(2)

    # 8. Date analytics
    df_calc['DAY_NAME'] = df_calc['_SORT_DATE'].dt.day_name()
    df_calc['MONTH'] = df_calc['_SORT_DATE'].dt.month
    df_calc['QUARTER'] = df_calc['_SORT_DATE'].dt.quarter
    df_calc['WEEK'] = df_calc['_SORT_DATE'].dt.isocalendar().week.astype(int)
    df_calc['DATETIME_STR'] = df_calc['_SORT_DATE'].dt.strftime('%Y-%m-%d')

    # 9. Technical Indicators
    df_calc['RSI_14'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: pandas_rsi(x, 14)).round(2)
    df_calc['VWAP'] = ((df_calc['HIGH'] + df_calc['LOW'] + df_calc['CLOSE']) / 3).round(2)
    df_calc['EMA_20'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=20, adjust=False).mean()).round(2)
    df_calc['EMA_50'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=50, adjust=False).mean()).round(2)
    df_calc['EMA_100'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=100, adjust=False).mean()).round(2)
    df_calc['EMA_200'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=200, adjust=False).mean()).round(2)
    df_calc['EMA_400'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=400, adjust=False).mean()).round(2)
    df_calc['EMA_500'] = df_calc.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=500, adjust=False).mean()).round(2)

    # MACD
    macd_df = df_calc.groupby('SYMBOL', group_keys=False)['CLOSE'].apply(pandas_macd)
    df_calc['MACD'] = macd_df['MACD'].round(2)
    df_calc['MACD_SIGNAL'] = macd_df['MACD_SIGNAL'].round(2)
    df_calc['MACD_HIST'] = macd_df['MACD_HIST'].round(2)

    prev_macd = df_calc.groupby('SYMBOL')['MACD'].shift(1)
    prev_signal = df_calc.groupby('SYMBOL')['MACD_SIGNAL'].shift(1)
    df_calc['MACD_CROSS'] = np.where(
        (df_calc['MACD'] > df_calc['MACD_SIGNAL']) & (prev_macd <= prev_signal),
        'BULLISH',
        np.where(
            (df_calc['MACD'] < df_calc['MACD_SIGNAL']) & (prev_macd >= prev_signal),
            'BEARISH',
            'NO SIGNAL'
        )
    )
    df_calc['MACD_TREND'] = np.where(
        df_calc['MACD_HIST'] > 0, 'POSITIVE MOMENTUM', 'NEGATIVE MOMENTUM'
    )

    if 'VOLUME' not in df_calc.columns:
        df_calc['VOLUME'] = 0

    df_calc = df_calc.sort_values(by=['SYMBOL', '_SORT_DATE'], ascending=[True, False]).reset_index(drop=True)
    df_calc.drop(columns=['_SORT_DATE'], inplace=True)
    return df_calc

def upload_raw_dataframe_to_oracle(conn, df: pd.DataFrame, batch_size: int = 10000) -> int:
    """Stage 1: Blazing fast vector insertion of raw OHLCV data into STAGING.RAW_STOCK_HISTORY."""
    if df.empty:
        return 0

    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.upper()

    if 'DATE' in df_clean.columns and 'DATETIME' not in df_clean.columns:
        df_clean = df_clean.rename(columns={'DATE': 'DATETIME'})

    if 'DATETIME_STR' not in df_clean.columns:
        df_clean['DATETIME_STR'] = pd.to_datetime(df_clean['DATETIME']).dt.strftime('%Y-%m-%d')

    if 'VOLUME' not in df_clean.columns:
        df_clean['VOLUME'] = 0

    cols = ['SYMBOL', 'DATETIME_STR', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
    for col in cols:
        if col not in df_clean.columns:
            raise KeyError(f"Missing required raw column: {col}")

    df_subset = df_clean[cols]
    raw_tuples = df_subset.itertuples(index=False, name=None)
    records = [
        tuple(
            None if (x is None or pd.isna(x)) else
            int(x) if isinstance(x, (np.integer, np.uint32)) else
            float(x) if isinstance(x, (np.floating, np.float64)) else
            x
            for x in row
        )
        for row in raw_tuples
    ]

    insert_sql = """
    INSERT INTO STAGING.RAW_STOCK_HISTORY (
        SYMBOL, DATETIME, OPEN, HIGH, LOW, CLOSE, VOLUME
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7
    )
    """

    cursor = conn.cursor()
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        chunk = records[i:i + batch_size]
        cursor.executemany(insert_sql, chunk)
        total_inserted += len(chunk)

    cursor.close()
    return total_inserted

def upload_indicators_dataframe_to_oracle(conn, df: pd.DataFrame, batch_size: int = 10000) -> int:
    """Stage 2: Vector insertion of calculated indicators into STAGING.STOCK_HIST_DATA."""
    if df.empty:
        return 0

    df_clean = df.copy()
    if 'DATETIME_STR' not in df_clean.columns:
        df_clean['DATETIME_STR'] = pd.to_datetime(df_clean['DATETIME']).dt.strftime('%Y-%m-%d')

    cols_order = [
        'SYMBOL', 'DATETIME_STR', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'CHANGE', 'CHANGE_PERCENT',
        'TOTAL_LOW_HIGH', 'GAP', 'GAP_PERCENT', 'TOTAL_PREV_LOW_HIGH',
        'TOTAL_PREV_LOW_HIGH_PERCENT', 'UPPER_WICK', 'LOWER_WICK', 'VOLUME',
        'LOW_CLOSE', 'HIGH_CLOSE', 'PREVIOUS_CLOSE', 'HIGH_52W', 'LOW_52W',
        'DIST_HIGH52', 'DIST_LOW52', 'DAY_NAME', 'MONTH', 'QUARTER', 'WEEK',
        'RSI_14', 'VWAP', 'EMA_20', 'EMA_50', 'EMA_100', 'EMA_200', 'EMA_400', 'EMA_500',
        'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'MACD_CROSS', 'MACD_TREND'
    ]

    df_subset = df_clean[cols_order]
    raw_tuples = df_subset.itertuples(index=False, name=None)
    records = [
        tuple(
            None if (x is None or pd.isna(x)) else
            int(x) if isinstance(x, (np.integer, np.uint32)) else
            float(x) if isinstance(x, (np.floating, np.float64)) else
            x
            for x in row
        )
        for row in raw_tuples
    ]

    insert_sql = """
    INSERT INTO STAGING.STOCK_HIST_DATA (
        SYMBOL, DATETIME, OPEN, HIGH, LOW, CLOSE, CHANGE, CHANGE_PERCENT,
        TOTAL_LOW_HIGH, GAP, GAP_PERCENT, TOTAL_PREV_LOW_HIGH,
        TOTAL_PREV_LOW_HIGH_PERCENT, UPPER_WICK, LOWER_WICK, VOLUME,
        LOW_CLOSE, HIGH_CLOSE, PREVIOUS_CLOSE, HIGH_52W, LOW_52W,
        DIST_HIGH52, DIST_LOW52, DAY_NAME, MONTH, QUARTER, WEEK,
        RSI_14, VWAP, EMA_20, EMA_50, EMA_100, EMA_200, EMA_400, EMA_500,
        MACD, MACD_SIGNAL, MACD_HIST, MACD_CROSS, MACD_TREND
    ) VALUES (
        :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8,
        :9, :10, :11, :12,
        :13, :14, :15, :16,
        :17, :18, :19, :20, :21,
        :22, :23, :24, :25, :26, :27,
        :28, :29, :30, :31, :32, :33, :34, :35,
        :36, :37, :38, :39, :40
    )
    """

    cursor = conn.cursor()
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        chunk = records[i:i + batch_size]
        cursor.executemany(insert_sql, chunk)
        total_inserted += len(chunk)

    cursor.close()
    return total_inserted

def get_symbols_from_oracle(limit: int = 900):
    """Fetches top N stock symbols by MARKET_CAP from HR.STOCKS table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"""
    SELECT * FROM (
        SELECT SYMBOL, COMPANY, MARKET_CAP
        FROM HR.STOCKS
        WHERE EXCHANGE = 'NSE'
          AND MARKET_CAP IS NOT NULL
          AND SYMBOL NOT LIKE '%.%'
        ORDER BY MARKET_CAP DESC
    ) WHERE ROWNUM <= {limit}
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows]

def run_stage_1(symbols: list, conn) -> int:
    """Stage 1: Download OHLCV stock data and bulk insert into STAGING.RAW_STOCK_HISTORY."""
    logger.info("\n" + "=" * 65)
    logger.info(" STAGE 1: Download -> Oracle STAGING.RAW_STOCK_HISTORY (Raw OHLCV)")
    logger.info("=" * 65)

    ensure_tables_exist(conn)

    cursor = conn.cursor()
    logger.info("Truncating table STAGING.RAW_STOCK_HISTORY before ingestion...")
    cursor.execute("TRUNCATE TABLE STAGING.RAW_STOCK_HISTORY")
    cursor.close()
    logger.info("✓ Table STAGING.RAW_STOCK_HISTORY truncated successfully.\n")

    pipeline = DownloadPipeline(years=15)
    total_raw_rows = 0
    failed_count = 0

    for idx, sym in enumerate(symbols, 1):
        fyers_sym = f"NSE:{sym}-EQ"
        logger.info(f"[{idx}/{len(symbols)}] Stage 1 Raw Ingestion for {sym}...")

        clean_filename = sym.replace("NSE:", "").replace("BSE:", "").replace("-EQ", "")
        csv_file = OUTPUT_FOLDER / f"{clean_filename}.csv"

        df_raw = None
        if csv_file.exists():
            df_raw = pd.read_csv(csv_file)
            if 'Symbol' not in df_raw.columns:
                df_raw.insert(0, 'Symbol', sym)
        else:
            try:
                pipeline.run([fyers_sym])
            except Exception as e:
                err_msg = f"API download failed: {e}"
                logger.warning(f"  ⚠️ {sym}: {err_msg}")
                record_failed_symbol(sym, "Stage 1 API Download", err_msg)
            
            if csv_file.exists():
                df_raw = pd.read_csv(csv_file)
                if 'Symbol' not in df_raw.columns:
                    df_raw.insert(0, 'Symbol', sym)

        if df_raw is not None and not df_raw.empty:
            try:
                inserted = upload_raw_dataframe_to_oracle(conn, df_raw, batch_size=10000)
                total_raw_rows += inserted
                logger.info(f"  ✓ {sym}: Ingested {inserted:,} raw rows")
            except Exception as e:
                err_msg = f"Oracle Raw Upload failed: {e}"
                logger.error(f"  ❌ {sym}: {err_msg}")
                record_failed_symbol(sym, "Stage 1 Oracle Ingestion", err_msg)
                failed_count += 1
        else:
            err_msg = "No raw data retrieved or file empty"
            logger.warning(f"  ❌ {sym}: {err_msg}")
            record_failed_symbol(sym, "Stage 1 Raw Data Missing", err_msg)
            failed_count += 1

    # Single commit at the end of Stage 1
    conn.commit()
    logger.info(f"\n✓ Stage 1 Complete: Total {total_raw_rows:,} raw rows committed to STAGING.RAW_STOCK_HISTORY. (Failed: {failed_count})")
    return total_raw_rows

def run_stage_2(symbols: list, conn) -> int:
    """Stage 2: Read raw data (from DB or CSV), compute indicators, bulk insert into STAGING.STOCK_HIST_DATA."""
    logger.info("\n" + "=" * 65)
    logger.info(" STAGE 2: STAGING.RAW_STOCK_HISTORY -> Feature Engineering -> STAGING.STOCK_HIST_DATA")
    logger.info("=" * 65)

    cursor = conn.cursor()
    logger.info("Truncating table STAGING.STOCK_HIST_DATA before indicator upload...")
    cursor.execute("TRUNCATE TABLE STAGING.STOCK_HIST_DATA")
    cursor.close()
    logger.info("✓ Table STAGING.STOCK_HIST_DATA truncated successfully.\n")

    total_indicator_rows = 0
    failed_count = 0

    for idx, sym in enumerate(symbols, 1):
        logger.info(f"[{idx}/{len(symbols)}] Stage 2 Processing {sym}...")

        clean_filename = sym.replace("NSE:", "").replace("BSE:", "").replace("-EQ", "")
        csv_file = OUTPUT_FOLDER / f"{clean_filename}.csv"

        df_raw = None
        if csv_file.exists():
            df_raw = pd.read_csv(csv_file)
            if 'Symbol' not in df_raw.columns:
                df_raw.insert(0, 'Symbol', sym)
        else:
            try:
                query = f"SELECT SYMBOL, DATETIME, OPEN, HIGH, LOW, CLOSE, VOLUME FROM STAGING.RAW_STOCK_HISTORY WHERE SYMBOL = '{sym}' ORDER BY DATETIME ASC"
                df_raw = pd.read_sql(query, conn)
            except Exception as e:
                logger.error(f"  ❌ {sym}: Failed to query Oracle RAW table: {e}")

        if df_raw is not None and not df_raw.empty:
            try:
                df_calc = calculate_technical_indicators(df_raw)
                inserted = upload_indicators_dataframe_to_oracle(conn, df_calc, batch_size=10000)
                total_indicator_rows += inserted
                logger.info(f"  ✓ {sym}: Calculated indicators & inserted {inserted:,} rows")
            except Exception as e:
                err_msg = f"Feature calculation/upload error: {e}"
                logger.error(f"  ❌ {sym}: {err_msg}")
                record_failed_symbol(sym, "Stage 2 Indicator Processing", err_msg)
                failed_count += 1
        else:
            err_msg = "No raw data found for indicator calculation"
            logger.warning(f"  ❌ {sym}: {err_msg}")
            record_failed_symbol(sym, "Stage 2 Raw Missing", err_msg)
            failed_count += 1

    # Single commit at the end of Stage 2
    conn.commit()
    logger.info(f"\n✓ Stage 2 Complete: Total {total_indicator_rows:,} indicator rows committed to STAGING.STOCK_HIST_DATA. (Failed: {failed_count})")
    return total_indicator_rows

def main():
    parser = argparse.ArgumentParser(description="2-Stage Optimized Stock ETL Pipeline")
    parser.add_argument("--limit", type=int, default=900, help="Number of stocks to process (default: 900)")
    parser.add_argument("--stage", type=str, choices=["1", "2", "all"], default="all", help="Stage to run: 1 (Raw Ingestion), 2 (Feature Engineering), all (Both)")
    args = parser.parse_args()

    logger.info("=" * 65)
    logger.info(" High-Performance Decoupled Stock ETL Pipeline")
    logger.info("=" * 65)
    logger.info(f"Logs persisted to: {LOG_FILE}")
    logger.info(f"Failed symbols tracked in: {FAILED_CSV}")

    symbols = get_symbols_from_oracle(limit=args.limit)
    logger.info(f"\nTarget Stock Symbols ({len(symbols)}): {symbols[:10]}... (Total {len(symbols)} stocks)")

    conn = get_db_connection()

    try:
        if args.stage in ["1", "all"]:
            run_stage_1(symbols, conn)

        if args.stage in ["2", "all"]:
            run_stage_2(symbols, conn)

    finally:
        conn.close()

    logger.info("\n" + "=" * 65)
    logger.info(" ETL PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 65)

if __name__ == "__main__":
    main()
