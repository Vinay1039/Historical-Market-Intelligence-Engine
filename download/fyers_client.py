import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from config import FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN, RETRY_COUNT, RETRY_DELAY
from download.retry import retry_with_backoff

logger = logging.getLogger("downloader")

class FyersDownloader:
    """Client for downloading historical OHLCV data from the Fyers API v3."""
    
    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()
        self.base_url = "https://api-t1.fyers.in/data/history"
        
        # Verify credentials
        if not FYERS_CLIENT_ID or not FYERS_ACCESS_TOKEN:
            logger.warning(
                "Fyers credentials (FYERS_CLIENT_ID or FYERS_ACCESS_TOKEN) are missing. "
                "Ensure fyers.env contains valid credentials."
            )
            
    def _fetch_chunk(self, symbol: str, start_date: datetime, end_date: datetime) -> List[List[Any]]:
        """Fetches a single chunk (max 366 days) of historical daily data."""
        if not FYERS_CLIENT_ID or not FYERS_ACCESS_TOKEN:
            raise ValueError("Fyers authentication details are missing. Set FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN.")
            

        headers = {
            "Authorization": f"{FYERS_CLIENT_ID}:{FYERS_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }


        # Auto-format symbol name to match FYERS index requirements (e.g. NSE:NIFTY50-INDEX)
        fyers_symbol = symbol
        if not fyers_symbol.startswith("NSE:") and not fyers_symbol.startswith("BSE:"):
            fyers_symbol = f"NSE:{fyers_symbol}"
        if not fyers_symbol.endswith("-INDEX") and not fyers_symbol.endswith("-EQ"):
            fyers_symbol = f"{fyers_symbol}-INDEX"

        params = {
            "symbol": fyers_symbol,
            "resolution": "1D",
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
        
        def make_request():
            response = self.session.get(self.base_url, headers=headers, params=params, timeout=15)
            # Catch 422 errors which represent requesting periods before the index was created
            if response.status_code == 422:
                logger.warning(f"Received 422 Unprocessable Entity for {symbol} on range {params['range_from']} to {params['range_to']}. Index may not have existed yet.")
                return []
            response.raise_for_status()
            res_json = response.json()
            
            # Check for API-specific error messages
            status = res_json.get("s")
            if status == "error":
                message = res_json.get("message", "Unknown Fyers API error")
                raise ValueError(f"Fyers API Error: {message}")
            elif status == "no_data":
                return []
                
            return res_json.get("candles", [])
            
        # Execute request using retry logic
        return retry_with_backoff(
            make_request,
            retries=RETRY_COUNT,
            base_delay=RETRY_DELAY,
            exceptions=(requests.RequestException, ValueError)
        )

    def download(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Downloads Daily historical data for the given symbol and date range.
        Handles date range chunking automatically.
        """
        logger.info(f"Fyers API: Starting download for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        all_candles = []
        current_start = start_date
        
        while current_start < end_date:
            # Chunk limit for 1D resolution is 366 days
            current_end = min(current_start + timedelta(days=365), end_date)
            
            logger.debug(f"Fetching chunk {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')} for {symbol}")
            candles = self._fetch_chunk(symbol, current_start, current_end)
            if candles:
                all_candles.extend(candles)
                
            current_start = current_end + timedelta(days=1)
            
        if not all_candles:
            raise ValueError("No data returned from Fyers API for the specified range.")
            
        # Convert to DataFrame
        # Fyers candle structure: [timestamp, open, high, low, close, volume]
        df = pd.DataFrame(all_candles, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Fyers timestamp can be either seconds or milliseconds epoch
        # Let's handle both dynamically
        first_ts = df['Date'].iloc[0]
        if first_ts > 1e11:  # Milliseconds
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        else:  # Seconds
            df['Date'] = pd.to_datetime(df['Date'], unit='s')
            
        # Localize/convert to IST or keep as date
        df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.date
        
        return df
