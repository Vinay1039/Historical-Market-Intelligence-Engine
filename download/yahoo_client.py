import yfinance as yf
import pandas as pd
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger("downloader")

# Comprehensive mapping of NSE Index symbol names to Yahoo Finance tickers.
YAHOO_TICKER_MAP: Dict[str, str] = {
    # Broad Market
    'NIFTY50':              '^NSEI',
    'NIFTYNEXT50':          '^NSMIDCP',
    'NIFTY100':             '^CNX100',
    'NIFTY200':             '^CNX200',
    'NIFTY500':             '^CRSLDX',

    # Market Cap Segmented
    'NIFTYMIDCAP50':        '^NSEMDCP50',
    'NIFTYMIDCAP100':       '^NSMIDCP',
    'NIFTYSMALLCAP100':     '^CNXSC',

    # Sectoral — Banks & Finance
    'NIFTYBANK':            '^NSEBANK',
    'NIFTYFINSERVICE':      '^CNXFIN',
    'NIFTYPSUBANK':         '^CNXPSUBANK',

    # Sectoral — Technology
    'NIFTYIT':              '^CNXIT',

    # Sectoral — Healthcare & Pharma
    'NIFTYPHARMA':          '^CNXPHARMA',

    # Sectoral — Consumer
    'NIFTYFMCG':            '^CNXFMCG',
    'NIFTYAUTO':            '^CNXAUTO',
    'NIFTYMNC':             '^CNXMNC',

    # Sectoral — Commodities & Energy
    'NIFTYMETAL':           '^CNXMETAL',
    'NIFTYENERGY':          '^CNXENERGY',

    # Sectoral — Real Estate & Infrastructure
    'NIFTYREALTY':          '^CNXREALTY',
    'NIFTYINFRA':           '^CNXINFRA',

    # Sectoral — Media
    'NIFTYMEDIA':           '^CNXMEDIA',
}

# Indices NOT available on Yahoo Finance — will be marked as permanently failed
YAHOO_UNAVAILABLE = {
    'NIFTYTOTALMKT',
    'NIFTYLARGEMIDCAP250',
    'NIFTYMIDCAP150',
    'NIFTYSMALLCAP50',
    'NIFTYSMALLCAP250',
    'NIFTYMICROCAP250',
    'NIFTYPRIVATEBANK',
    'NIFTYHEALTHCARE',
    'NIFTYCONSUMERDURABLES',
    'NIFTYOILGAS',
    'NIFTYCOMMODITIES',
    'NIFTYSERVSECTOR',
}

class YahooDownloader:
    """Fallback client for downloading historical OHLCV data from Yahoo Finance."""

    def download(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Downloads Daily historical data from Yahoo Finance for a mapped NSE symbol."""
        # Clean symbol to match mapping keys
        clean_symbol = symbol.replace("NSE:", "").replace("BSE:", "").replace("-INDEX", "").strip()

        # Check if this index is known to be unavailable on Yahoo Finance
        if clean_symbol in YAHOO_UNAVAILABLE:
            raise ValueError(
                f"'{clean_symbol}' is not available on Yahoo Finance. "
                "Please authenticate with Fyers API (set FYERS_ACCESS_TOKEN in fyers.env) "
                "and re-run to download via Fyers."
            )

        # Check if this is an NSE equity stock (ends with -EQ after stripping)
        is_equity = clean_symbol.endswith('-EQ')
        base_symbol = clean_symbol.replace('-EQ', '').replace('-INDEX', '').strip()

        # Get Yahoo ticker from map, or construct appropriately
        yahoo_ticker = YAHOO_TICKER_MAP.get(clean_symbol) or YAHOO_TICKER_MAP.get(base_symbol)
        if not yahoo_ticker:
            if is_equity:
                # NSE equity stocks on Yahoo Finance use SYMBOL.NS format
                yahoo_ticker = f"{base_symbol}.NS"
                logger.info(
                    f"Yahoo Finance: Equity stock detected. Using NSE format ticker '{yahoo_ticker}'."
                )
            else:
                # Index fallback attempt with ^ prefix
                yahoo_ticker = f"^{clean_symbol}"
                logger.warning(
                    f"Yahoo Finance: No explicit mapping for '{clean_symbol}'. "
                    f"Trying candidate ticker '{yahoo_ticker}'."
                )


        logger.info(
            f"Yahoo Finance: Downloading {yahoo_ticker} "
            f"(period=max, then filtered to "
            f"{start_date.strftime('%Y-%m-%d')} – {end_date.strftime('%Y-%m-%d')})"
        )

        try:
            ticker_obj = yf.Ticker(yahoo_ticker)

            df = ticker_obj.history(
                period='max',
                interval='1d',
                auto_adjust=False,
            )

            if df.empty:
                raise ValueError(
                    f"No data returned from Yahoo Finance for ticker '{yahoo_ticker}'."
                )

            # Reset index to expose the Date as a column
            df = df.reset_index()

            # Keep required columns only
            required = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            df = df[required]

            # Convert timezone to Asia/Kolkata (IST) before extracting date string to prevent date-shifting
            date_col = pd.to_datetime(df['Date'])
            if date_col.dt.tz is None:
                date_col = date_col.dt.tz_localize('UTC')
            df['Date'] = date_col.dt.tz_convert('Asia/Kolkata').dt.date

            # Filter to the requested date range
            df = df[
                (df['Date'] >= start_date.date()) &
                (df['Date'] <= end_date.date())
            ]

            # Remove invalid/zero rows and non-trading holiday entries (where High == Low and Volume == 0)
            df = df[(df['Open'] > 0) | (df['High'] > 0) | (df['Close'] > 0)]
            df = df[~((df['High'] == df['Low']) & (df['Volume'] == 0))]

            if df.empty:
                raise ValueError(
                    f"No valid (non-zero) data found for '{yahoo_ticker}' "
                    f"in the requested date range."
                )

            return df

        except Exception as e:
            logger.error(f"Yahoo Finance: Failed to download '{yahoo_ticker}'. Error: {e}")
            raise
