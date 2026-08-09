import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Define base path (Fyers directory)
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Force-load credentials from fyers.env in the current directory
ENV_PATH = BASE_DIR / "fyers.env"
if ENV_PATH.exists():
    print(f"Loading env from {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Now import the downloader components
# Add project root and base directory at index 0 of sys.path to avoid name collision with standard/global config directories
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BASE_DIR))
print("Current sys.path:", sys.path)

from download.downloader import DownloadPipeline
from config import OUTPUT_FOLDER

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

def main():
    # 1. Read symbols from Fyers_Indices.csv
    csv_path = BASE_DIR / "Fyers_Indices.csv"
    if not csv_path.exists():
        print(f"Error: {csv_path} does not exist.")
        return
        
    try:
        df_symbols = pd.read_csv(csv_path)
        if 'SYMBOL' not in df_symbols.columns:
            # Fallback for encoding/format
            df_symbols = pd.read_csv(csv_path, encoding='mac_roman')
        symbols = df_symbols['SYMBOL'].dropna().unique().tolist()
        print(f"Loaded {len(symbols)} symbols to fetch.")
    except Exception as e:
        print(f"Failed to read symbols: {e}")
        return

    # 2. Run the Download Pipeline for 15 years
    print("Initializing DownloadPipeline for 15 years...")
    pipeline = DownloadPipeline(years=15)
    
    def display_progress(current: int, total: int, symbol: str, stage: str):
        print(f"[{current}/{total}] Fetching {symbol} via {stage}...", flush=True)

    summary = pipeline.run(symbols, progress_callback=display_progress)
    print("\nDownload Phase Complete.")
    print(f"Success: {len(summary['success'])}")
    print(f"Recovered: {len(summary['recovered'])}")
    print(f"Failed: {len(summary['failed'])}")

    # 3. Combine individual files into HIST_DATA.csv
    print("\nCombining individual CSVs into HIST_DATA.csv...")
    combined_dfs = []
    
    for symbol in symbols:
        clean_filename = symbol.replace("NSE:", "").replace("BSE:", "").replace("-INDEX", "")
        file_path = OUTPUT_FOLDER / f"{clean_filename}.csv"
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                # Ensure Symbol column is present
                df.insert(0, 'Symbol', symbol)
                combined_dfs.append(df)
                print(f"Combined data for {symbol} ({len(df)} rows)")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"Warning: No data file found for {symbol} at {file_path}")

    if combined_dfs:
        final_df = pd.concat(combined_dfs, ignore_index=True)
            
        # Convert columns to uppercase for calculations to match user's logic
        final_df.columns = final_df.columns.str.upper()
        
        # Rename DATE column to DATETIME as requested
        if 'DATE' in final_df.columns:
            final_df = final_df.rename(columns={'DATE': 'DATETIME'})

        # Create temporary date column for chronological sorting during indicator calculation
        final_df['_SORT_DATE'] = pd.to_datetime(final_df['DATETIME'])
        final_df = final_df.sort_values(by=['SYMBOL', '_SORT_DATE'], ascending=[True, True]).reset_index(drop=True)
        
        print("\nCalculating technical indicators and wicks...")
        
        # 1. Day changes
        final_df['PREVIOUS_CLOSE'] = final_df.groupby('SYMBOL')['CLOSE'].shift(1)
        final_df['CHANGE'] = final_df['CLOSE'] - final_df['PREVIOUS_CLOSE']
        final_df['CHANGE_PERCENT'] = (final_df['CHANGE'] * 100 / final_df['PREVIOUS_CLOSE']).round(2)
        
        # 2. Daily limits
        final_df['LOW_CLOSE'] = final_df['CLOSE'] - final_df['LOW']
        final_df['HIGH_CLOSE'] = final_df['CLOSE'] - final_df['HIGH']
        final_df['TOTAL_LOW_HIGH'] = final_df['HIGH'] - final_df['LOW']
        
        # 3. Gap logic
        final_df['GAP'] = np.where(
            final_df['OPEN'] > final_df['PREVIOUS_CLOSE'], 'gap up',
            np.where(
                final_df['OPEN'] < final_df['PREVIOUS_CLOSE'], 'gap down',
                'no gap'
            )
        )
        final_df['GAP_PERCENT'] = ((final_df['OPEN'] - final_df['PREVIOUS_CLOSE']) * 100 / final_df['PREVIOUS_CLOSE']).round(2)

        # 4. Directional 2-Day Span calculations (Prev High/Low to Current Low/High)
        final_df['PREV_HIGH'] = final_df.groupby('SYMBOL')['HIGH'].shift(1)
        final_df['PREV_LOW'] = final_df.groupby('SYMBOL')['LOW'].shift(1)

        # If market fell today (CLOSE < PREVIOUS_CLOSE): Prev High -> Current Low
        # If market went up today (CLOSE >= PREVIOUS_CLOSE): Prev Low -> Current High
        final_df['TOTAL_PREV_LOW_HIGH'] = np.where(
            final_df['CLOSE'] >= final_df['PREVIOUS_CLOSE'],
            final_df['HIGH'] - final_df['PREV_LOW'],
            final_df['PREV_HIGH'] - final_df['LOW']
        ).round(2)

        final_df['TOTAL_PREV_LOW_HIGH_PERCENT'] = ((final_df['TOTAL_PREV_LOW_HIGH'] * 100.0) / final_df['PREVIOUS_CLOSE']).round(2)
        final_df.drop(columns=['PREV_HIGH', 'PREV_LOW'], inplace=True)        
        
        # 5. Wicks
        final_df['UPPER_WICK'] = (final_df['HIGH'] - final_df[['OPEN','CLOSE']].max(axis=1)).round(2)
        final_df['LOWER_WICK'] = (final_df[['OPEN','CLOSE']].min(axis=1) - final_df['LOW']).round(2)
        
        # 6. 52-week High/Low
        final_df['HIGH_52W'] = final_df.groupby('SYMBOL')['HIGH'].transform(lambda x: x.rolling(252).max())
        final_df['LOW_52W'] = final_df.groupby('SYMBOL')['LOW'].transform(lambda x: x.rolling(252).min())
        
        # 7. Distances to 52-week high/low
        final_df['DIST_HIGH52'] = ((final_df['CLOSE'] - final_df['HIGH_52W']) * 100 / final_df['HIGH_52W']).round(2)
        final_df['DIST_LOW52'] = ((final_df['CLOSE'] - final_df['LOW_52W']) * 100 / final_df['LOW_52W']).round(2)
        
        # 8. Date analytics (Mapping DATETIME to DAY_NAME, MONTH, QUARTER, WEEK)
        final_df['DAY_NAME'] = final_df['_SORT_DATE'].dt.day_name()
        final_df['MONTH'] = final_df['_SORT_DATE'].dt.month
        final_df['QUARTER'] = final_df['_SORT_DATE'].dt.quarter
        final_df['WEEK'] = final_df['_SORT_DATE'].dt.isocalendar().week
        final_df['DATETIME'] = final_df['_SORT_DATE'].dt.strftime('%d-%b-%Y')
        
        # 9. Technical Indicators
        print("Calculating technical indicators (RSI, VWAP, EMA 20/50/100/200/400/500, MACD)...")
        final_df['RSI_14'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: pandas_rsi(x, 14)).round(2)
        final_df['VWAP'] = ((final_df['HIGH'] + final_df['LOW'] + final_df['CLOSE']) / 3).round(2)
        final_df['EMA_20'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=20, adjust=False).mean()).round(2)
        final_df['EMA_50'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=50, adjust=False).mean()).round(2)
        final_df['EMA_100'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=100, adjust=False).mean()).round(2)
        final_df['EMA_200'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=200, adjust=False).mean()).round(2)
        final_df['EMA_400'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=400, adjust=False).mean()).round(2)
        final_df['EMA_500'] = final_df.groupby('SYMBOL')['CLOSE'].transform(lambda x: x.ewm(span=500, adjust=False).mean()).round(2)
        
        # MACD calculations
        macd_df = final_df.groupby('SYMBOL', group_keys=False)['CLOSE'].apply(pandas_macd)
        final_df['MACD'] = macd_df['MACD'].round(2)
        final_df['MACD_SIGNAL'] = macd_df['MACD_SIGNAL'].round(2)
        final_df['MACD_HIST'] = macd_df['MACD_HIST'].round(2)
        
        # MACD Cross signals
        prev_macd = final_df.groupby('SYMBOL')['MACD'].shift(1)
        prev_signal = final_df.groupby('SYMBOL')['MACD_SIGNAL'].shift(1)
        final_df['MACD_CROSS'] = np.where(
            (final_df['MACD'] > final_df['MACD_SIGNAL']) & (prev_macd <= prev_signal),
            'BULLISH',
            np.where(
                (final_df['MACD'] < final_df['MACD_SIGNAL']) & (prev_macd >= prev_signal),
                'BEARISH',
                'NO SIGNAL'
            )
        )
        final_df['MACD_TREND'] = np.where(
            final_df['MACD_HIST'] > 0, 'POSITIVE MOMENTUM', 'NEGATIVE MOMENTUM'
        )

        # Ensure VOLUME column exists
        if 'VOLUME' not in final_df.columns:
            final_df['VOLUME'] = 0
        
        # Sort by DATETIME descending per symbol
        final_df = final_df.sort_values(by=['SYMBOL', '_SORT_DATE'], ascending=[True, False]).reset_index(drop=True)
        final_df.drop(columns=['_SORT_DATE'], inplace=True)
        
        # Round numeric float columns to 2 decimal places to eliminate floating point imprecision (e.g., 111.64999999999782 -> 111.65)
        num_cols = [
            'OPEN','HIGH','LOW','CLOSE','CHANGE','CHANGE_PERCENT',
            'TOTAL_LOW_HIGH','GAP_PERCENT','TOTAL_PREV_LOW_HIGH',
            'TOTAL_PREV_LOW_HIGH_PERCENT','UPPER_WICK','LOWER_WICK',
            'LOW_CLOSE','HIGH_CLOSE','PREVIOUS_CLOSE','HIGH_52W','LOW_52W',
            'DIST_HIGH52','DIST_LOW52','RSI_14','VWAP','EMA_20','EMA_50',
            'EMA_100','EMA_200','EMA_400','EMA_500','MACD','MACD_SIGNAL','MACD_HIST'
        ]
        for c in num_cols:
            if c in final_df.columns:
                final_df[c] = final_df[c].astype(float).round(2)

        # Convert integer columns
        int_cols = ['VOLUME', 'MONTH', 'QUARTER', 'WEEK']
        for c in int_cols:
            if c in final_df.columns:
                final_df[c] = final_df[c].fillna(0).astype(int)

        # Reorder columns to exact user-requested order
        columns_order = [
            'SYMBOL','DATETIME','OPEN','HIGH','LOW','CLOSE','CHANGE','CHANGE_PERCENT',
            'TOTAL_LOW_HIGH','GAP','GAP_PERCENT','TOTAL_PREV_LOW_HIGH',
            'TOTAL_PREV_LOW_HIGH_PERCENT','UPPER_WICK','LOWER_WICK','VOLUME',
            'LOW_CLOSE','HIGH_CLOSE','PREVIOUS_CLOSE','HIGH_52W','LOW_52W',
            'DIST_HIGH52','DIST_LOW52','DAY_NAME','MONTH','QUARTER','WEEK',
            'RSI_14','VWAP','EMA_20','EMA_50','EMA_100','EMA_200','EMA_400','EMA_500',
            'MACD','MACD_SIGNAL','MACD_HIST','MACD_CROSS','MACD_TREND'
        ]
        final_df = final_df[columns_order]
        
        output_file = BASE_DIR / "HIST_DATA.csv"
        final_df.to_csv(output_file, index=False, float_format='%.2f')
        print(f"\nSUCCESS: Compiled data saved to {output_file} ({len(final_df)} total rows)")
    else:
        print("\nERROR: No symbol data could be compiled.")

if __name__ == "__main__":
    main()
