from pydantic import BaseModel
from typing import List, Optional

class StockSymbolItem(BaseModel):
    symbol: str
    company: Optional[str] = None
    market_cap: Optional[float] = None

class SymbolListResponse(BaseModel):
    count: int
    symbols: List[StockSymbolItem]
