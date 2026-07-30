from pydantic import BaseModel
from typing import List, Optional

class TechnicalRecord(BaseModel):
    symbol: str
    datetime: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    total_low_high: Optional[float] = None
    gap: Optional[str] = None
    gap_percent: Optional[float] = None
    total_prev_low_high: Optional[float] = None
    total_prev_low_high_percent: Optional[float] = None
    upper_wick: Optional[float] = None
    lower_wick: Optional[float] = None
    volume: Optional[int] = None
    low_close: Optional[float] = None
    high_close: Optional[float] = None
    previous_close: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    dist_high52: Optional[float] = None
    dist_low52: Optional[float] = None
    day_name: Optional[str] = None
    month: Optional[int] = None
    quarter: Optional[int] = None
    week: Optional[int] = None
    rsi_14: Optional[float] = None
    vwap: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_100: Optional[float] = None
    ema_200: Optional[float] = None
    ema_400: Optional[float] = None
    ema_500: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    macd_cross: Optional[str] = None
    macd_trend: Optional[str] = None

class TechnicalResponse(BaseModel):
    symbol: str
    count: int
    data: List[TechnicalRecord]

class DashboardSummary(BaseModel):
    symbol: str
    latest_date: str
    close_price: float
    change_percent: float
    rsi_14: Optional[float] = None
    macd_signal: Optional[str] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None

class DashboardResponse(BaseModel):
    summary: DashboardSummary
    recent_history: List[TechnicalRecord]
