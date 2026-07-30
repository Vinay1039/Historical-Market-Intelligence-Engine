from pydantic import BaseModel
from typing import List, Optional

class RawOHLCVRecord(BaseModel):
    symbol: str
    datetime: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None

class HistoryResponse(BaseModel):
    symbol: str
    count: int
    data: List[RawOHLCVRecord]
    disclaimer: str = "Original unadjusted historical market data from STAGING.RAW_STOCK_HISTORY."
