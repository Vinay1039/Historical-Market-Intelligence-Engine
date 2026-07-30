import pandas as pd
import logging
from pathlib import Path
from config import OUTPUT_FOLDER

logger = logging.getLogger("downloader")

def validate_and_save_data(df: pd.DataFrame, symbol: str) -> Path:
    """
    Validates the downloaded DataFrame (removes duplicates, checks dates and OHLC values,
    sorts ascending by Date, formats columns) and saves it to a CSV file.
    
    Args:
        df: The pandas DataFrame with raw data.
        symbol: The stock symbol (e.g., NIFTY50).
        
    Returns:
        The Path to the saved CSV file.
    """
    if df.empty:
        raise ValueError(f"DataFrame for symbol {symbol} is empty.")
    
    # Copy DataFrame to avoid modifying original
    df_clean = df.copy()
    
    # 1. Normalize column names to title case
    # Required output columns: Date, Open, High, Low, Close, Volume
    column_mapping = {col.lower(): col for col in df_clean.columns}
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Rename standard variants
    standard_renames = {
        'Datetime': 'Date',
        'date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    df_clean = df_clean.rename(columns=standard_renames)
    
    # Keep only the required columns
    required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df_clean.columns:
            if col == 'Volume':
                df_clean['Volume'] = 0
            else:
                raise ValueError(f"Missing required column: {col}")
                
    df_clean = df_clean[required_cols]
    
    # 2. Data Validation
    # Ensure Date exists and is not null
    df_clean = df_clean.dropna(subset=['Date'])
    
    # Convert Date to string YYYY-MM-DD
    df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.strftime('%Y-%m-%d')
    
    # Ensure OHLC values exist and are not null
    df_clean = df_clean.dropna(subset=['Open', 'High', 'Low', 'Close'])
    
    # Ensure numeric types
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Drop rows where OHLC contains NaN after numeric coercion
    df_clean = df_clean.dropna(subset=['Open', 'High', 'Low', 'Close'])

    # Filter out non-trading holiday entries (where High == Low and Volume == 0)
    df_clean = df_clean[~((df_clean['High'] == df_clean['Low']) & (df_clean['Volume'] == 0))]

    # 3. Remove duplicates by Date (keep first)
    df_clean = df_clean.drop_duplicates(subset=['Date'], keep='first')
    
    # 4. Sort ascending by Date
    df_clean = df_clean.sort_values(by='Date', ascending=True).reset_index(drop=True)
    
    if df_clean.empty:
        raise ValueError(f"DataFrame for symbol {symbol} contains no valid rows after validation.")
    
    # Save to CSV
    # Remove any exchange prefix and equity suffix from filename (e.g., NSE:RELIANCE-EQ -> RELIANCE)
    clean_filename = symbol.replace("NSE:", "").replace("BSE:", "").replace("-INDEX", "").replace("-EQ", "")

    output_file = OUTPUT_FOLDER / f"{clean_filename}.csv"
    
    df_clean.to_csv(output_file, index=False)
    logger.info(f"Successfully validated and saved {len(df_clean)} rows to {output_file.name}")
    return output_file
