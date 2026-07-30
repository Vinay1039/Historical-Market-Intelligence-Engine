import pandas as pd
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from config import OUTPUT_FOLDER, FORCE_DOWNLOAD, FAILED_SYMBOLS_CSV
from download.fyers_client import FyersDownloader
from download.yahoo_client import YahooDownloader
from download.csv_writer import validate_and_save_data

logger = logging.getLogger("downloader")

class BaseDownloader(ABC):
    """Abstract Base Class for all data providers."""
    
    @abstractmethod
    def download(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Downloads daily historical data for the symbol within the range."""
        pass

class DownloadPipeline:
    """Orchestrates the download process across multiple stages and providers."""
    
    def __init__(self, years: int = 15):
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=years * 365)
        
        self.fyers_client = FyersDownloader()
        self.yahoo_client = YahooDownloader()
        
    def check_exists(self, symbol: str) -> bool:
        """Checks if historical data CSV already exists for the symbol."""
        clean_filename = symbol.replace("NSE:", "").replace("BSE:", "").replace("-INDEX", "")
        file_path = OUTPUT_FOLDER / f"{clean_filename}.csv"
        return file_path.exists()
        
    def run(self, symbols: List[str], progress_callback=None) -> Dict[str, Any]:
        """
        Runs the full download pipeline.
        """
        success_list = []
        recovered_list = []
        failed_list = []  # List of dicts with failure metadata
        
        # Stage 1: Primary Source (Fyers API)
        stage_1_failed: List[Tuple[str, str]] = []  # List of (symbol, reason)
        
        logger.info(f"Pipeline started for {len(symbols)} symbols. Target: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        for idx, symbol in enumerate(symbols):
            if progress_callback:
                progress_callback(idx + 1, len(symbols), symbol, "Fyers API")
                
            logger.info(f"Processing symbol [{idx + 1}/{len(symbols)}]: {symbol}")
            
            # Check for resume
            if self.check_exists(symbol) and not FORCE_DOWNLOAD:
                logger.info(f"CSV already exists for {symbol}. Skipping download.")
                success_list.append(symbol)
                continue
                
            # Run Stage 1 (Fyers API)
            try:
                df = self.fyers_client.download(symbol, self.start_date, self.end_date)
                validate_and_save_data(df, symbol)
                success_list.append(symbol)
                logger.info(f"Stage 1 Success: {symbol} downloaded via Fyers API.")
            except Exception as e:
                err_msg = str(e)
                logger.error(f"Stage 1 Failure: {symbol} failed via Fyers API. Error: {err_msg}")
                stage_1_failed.append((symbol, err_msg))
                
        # Stage 2: Fallback Source (Yahoo Finance)
        if stage_1_failed:
            logger.info(f"Stage 1 complete. Starting Stage 2 fallback for {len(stage_1_failed)} failed symbols.")
            
            for idx, (symbol, primary_reason) in enumerate(stage_1_failed):
                if progress_callback:
                    progress_callback(idx + 1, len(stage_1_failed), symbol, "Yahoo Finance Fallback")
                    
                logger.info(f"Processing fallback [{idx + 1}/{len(stage_1_failed)}]: {symbol}")
                
                try:
                    df = self.yahoo_client.download(symbol, self.start_date, self.end_date)
                    validate_and_save_data(df, symbol)
                    recovered_list.append(symbol)
                    logger.info(f"Stage 2 Success: {symbol} recovered via Yahoo Finance.")
                except Exception as e:
                    fallback_err = str(e)
                    logger.critical(f"Stage 2 Failure: {symbol} failed Yahoo Finance fallback. Error: {fallback_err}")
                    failed_list.append({
                        "Symbol": symbol,
                        "Reason": f"Fyers error: {primary_reason}; Yahoo error: {fallback_err}",
                        "Source": "Fyers -> Yahoo Finance",
                        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
        # Log and save failed symbols report
        if failed_list:
            failed_df = pd.DataFrame(failed_list)
            # Append if file exists, else create new
            if FAILED_SYMBOLS_CSV.exists():
                try:
                    existing_failed = pd.read_csv(FAILED_SYMBOLS_CSV)
                    failed_df = pd.concat([existing_failed, failed_df]).drop_duplicates(subset=['Symbol'], keep='last')
                except Exception:
                    pass
            failed_df.to_csv(FAILED_SYMBOLS_CSV, index=False)
            logger.warning(f"Saved {len(failed_list)} failed symbols to {FAILED_SYMBOLS_CSV}")
            
        summary = {
            "success": success_list,
            "recovered": recovered_list,
            "failed": [item["Symbol"] for item in failed_list]
        }
        
        logger.info(
            f"Pipeline Complete. Summary: "
            f"Success: {len(success_list)}, "
            f"Recovered: {len(recovered_list)}, "
            f"Failed: {len(failed_list)}"
        )
        return summary
