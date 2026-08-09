import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows terminal to avoid cp1252 encoding errors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
FYERS_HIST_DIR = BASE_DIR.parent
FYERS_DIR = FYERS_HIST_DIR / "Fyers"

# Force-load credentials from fyers.env in Fyers directory
ENV_PATH = FYERS_DIR / "fyers.env"
if ENV_PATH.exists():
    print(f"Loading env from {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Add FYERS_HIST_DIR to sys.path to access download module
sys.path.insert(0, str(FYERS_HIST_DIR))
sys.path.insert(0, str(FYERS_DIR))

# Import oracle and downloader components
import oracledb
from download.downloader import DownloadPipeline
import download.downloader as downloader_mod
import download.csv_writer as csv_writer_mod

# Configure output folder to Fyers_stock/Historical_Data
OUTPUT_FOLDER = BASE_DIR / "Historical_Data"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
downloader_mod.OUTPUT_FOLDER = OUTPUT_FOLDER
csv_writer_mod.OUTPUT_FOLDER = OUTPUT_FOLDER

def get_top_5_symbols_from_oracle():
    """Queries Oracle DB for the top 5 NSE equity stock symbols by Market Cap."""
    try:
        oracledb.init_oracle_client(lib_dir=r"C:\instantclient_23_0")
    except Exception:
        pass

    user = os.getenv("ORACLE_DB_USER", "analysis")
    pwd = os.getenv("ORACLE_DB_PASSWORD", "hr")
    host = os.getenv("ORACLE_DB_HOST", "localhost")
    port = os.getenv("ORACLE_DB_PORT", "1521")
    service = os.getenv("ORACLE_DB_SERVICE_NAME", "XE")

    try:
        dsn = f"{host}:{port}/{service}"
        conn = oracledb.connect(user=user, password=pwd, dsn=dsn)
        cursor = conn.cursor()
        query = """
        SELECT *
        FROM (
            SELECT SYMBOL, COMPANY, MARKET_CAP
            FROM HR.STOCKS
            WHERE EXCHANGE = 'NSE'
              AND MARKET_CAP IS NOT NULL
              AND SYMBOL NOT LIKE '%.%'
            ORDER BY MARKET_CAP DESC
        )
        WHERE ROWNUM <= 5
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print("Top 5 Stock Symbols from Oracle DB:")
        raw_symbols = []
        for r in rows:
            print(f"  • {r[0]:<15} ({r[1]}) - Market Cap: {r[2]:,}")
            raw_symbols.append(r[0])
        cursor.close()
        conn.close()
        return raw_symbols
    except Exception as e:
        print(f"Oracle Connection/Query Warning: {e}")
        # Fallback top 5 market cap stocks
        print("Using standard top 5 market cap stocks fallback: RELIANCE, TCS, HDFCBANK, BHARTIARTL, ICICIBANK")
        return ["RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "ICICIBANK"]

def format_fyers_stock_symbol(sym: str) -> str:
    """Formats stock symbol into FYERS equity format: NSE:<SYMBOL>-EQ"""
    sym = sym.strip()
    if sym.startswith("NSE:") or sym.startswith("BSE:"):
        return sym
    return f"NSE:{sym}-EQ"

def main():
    print("=" * 60)
    print(" 15-Year Historical Stock Data Fetcher (FYERS API)")
    print("=" * 60)

    # 1. Fetch top 5 symbols
    raw_symbols = get_top_5_symbols_from_oracle()
    fyers_symbols = [format_fyers_stock_symbol(s) for s in raw_symbols]

    print(f"\nTarget FYERS Symbols to fetch: {fyers_symbols}\n")

    # 2. Run Download Pipeline for 15 years
    print("Initializing DownloadPipeline for 15 years...")
    pipeline = DownloadPipeline(years=15)

    def display_progress(current: int, total: int, symbol: str, stage: str):
        print(f"[{current}/{total}] Fetching {symbol} via {stage}...", flush=True)

    summary = pipeline.run(fyers_symbols, progress_callback=display_progress)

    print("\n" + "=" * 60)
    print(" Download Phase Complete")
    print("=" * 60)
    print(f"Success:   {len(summary['success'])}")
    print(f"Recovered: {len(summary['recovered'])}")
    print(f"Failed:    {len(summary['failed'])}")

    # 3. Combine CSVs into HIST_STOCK_DATA.csv
    print("\nCombining individual CSVs into HIST_STOCK_DATA.csv...")
    combined_dfs = []
    
    for symbol in fyers_symbols:
        clean_filename = symbol.replace("NSE:", "").replace("BSE:", "").replace("-EQ", "").replace("-INDEX", "")
        # Search for either CLEAN.csv or CLEAN-EQ.csv
        file_path = OUTPUT_FOLDER / f"{clean_filename}.csv"
        if not file_path.exists():
            file_path = OUTPUT_FOLDER / f"{clean_filename}-EQ.csv"
            
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                if 'Symbol' not in df.columns:
                    df.insert(0, 'Symbol', clean_filename)
                combined_dfs.append(df)
                print(f"  ✓ Added {clean_filename} ({len(df)} rows)")
            except Exception as e:
                print(f"  ✗ Error reading {file_path}: {e}")
        else:
            print(f"  ⚠ CSV not found for {symbol} at {file_path}")

    if combined_dfs:
        combined_df = pd.concat(combined_dfs, ignore_index=True)
        out_csv = BASE_DIR / "HIST_STOCK_DATA.csv"
        combined_df.to_csv(out_csv, index=False)
        print(f"\nSuccessfully generated {out_csv} with {len(combined_df)} total records across {len(combined_dfs)} stocks!")

if __name__ == "__main__":
    main()
