from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class SectorItem(BaseModel):
    sector_code: str
    sector_name: str
    stock_count: int
    total_market_cap: Optional[float] = None

class SectorListResponse(BaseModel):
    count: int
    sectors: List[SectorItem]

class IndustryItem(BaseModel):
    industry_code: str
    industry_name: str
    sector_code: str
    stock_count: int
    total_market_cap: Optional[float] = None

class IndustryListResponse(BaseModel):
    count: int
    industries: List[IndustryItem]

class DailyAggregationRecord(BaseModel):
    code: str
    datetime: str
    avg_change_pct: Optional[float] = None
    median_change_pct: Optional[float] = None
    total_volume: Optional[int] = None
    avg_rsi_14: Optional[float] = None
    active_stocks: Optional[int] = None
    advancing_stocks: Optional[int] = None
    declining_stocks: Optional[int] = None
    unchanged_stocks: Optional[int] = None
    breadth_ratio: Optional[float] = None
    net_advances: Optional[int] = None
    pct_above_ema20: Optional[float] = None
    pct_above_ema50: Optional[float] = None
    pct_above_ema200: Optional[float] = None

class DailyAggregationResponse(BaseModel):
    code: str
    count: int
    data: List[DailyAggregationRecord]

class MarketBreadthRecord(BaseModel):
    datetime: str
    total_stocks: int
    advancing_stocks: int
    declining_stocks: int
    unchanged_stocks: int
    breadth_ratio: Optional[float] = None
    net_advances: int
    pct_above_ema20: Optional[float] = None
    pct_above_ema50: Optional[float] = None
    pct_above_ema200: Optional[float] = None

class MarketBreadthResponse(BaseModel):
    count: int
    data: List[MarketBreadthRecord]

class PerformanceRecord(BaseModel):
    code: str
    period_type: str
    period_label: str
    avg_return_pct: Optional[float] = None
    win_rate_pct: Optional[float] = None
    volatility_pct: Optional[float] = None
    sample_count: int

class PerformanceResponse(BaseModel):
    count: int
    data: List[PerformanceRecord]

class RotationRecord(BaseModel):
    code: str
    datetime: str
    return_1m: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_12m: Optional[float] = None
    relative_strength_1m: Optional[float] = None
    relative_strength_3m: Optional[float] = None
    relative_strength_6m: Optional[float] = None
    relative_strength_12m: Optional[float] = None
    rank_1m: Optional[int] = None
    rank_3m: Optional[int] = None
    rank_12m: Optional[int] = None
    rank_delta_3m: Optional[int] = None
    rotation_status: str

class RotationResponse(BaseModel):
    count: int
    data: List[RotationRecord]

class StockRankingRecord(BaseModel):
    symbol: str
    datetime: str
    sector_code: Optional[str] = None
    industry_code: Optional[str] = None
    return_3m: Optional[float] = None
    sector_rank: Optional[int] = None
    industry_rank: Optional[int] = None
    market_rank: Optional[int] = None
    sector_percentile: Optional[float] = None
    industry_percentile: Optional[float] = None
    market_percentile: Optional[float] = None
    rsi_rank_industry: Optional[int] = None

class StockRankingResponse(BaseModel):
    count: int
    data: List[StockRankingRecord]

class ThemeItem(BaseModel):
    theme_code: str
    theme_name: str
    description: Optional[str] = None
    stock_count: int

class ThemeListResponse(BaseModel):
    count: int
    themes: List[ThemeItem]

class ThemeRotationRecord(BaseModel):
    theme_code: str
    datetime: str
    return_1m: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_12m: Optional[float] = None
    relative_strength_1m: Optional[float] = None
    relative_strength_3m: Optional[float] = None
    relative_strength_6m: Optional[float] = None
    relative_strength_12m: Optional[float] = None
    theme_rank_3m: Optional[int] = None
    rank_delta_3m: Optional[int] = None
    rotation_status: str

class ThemeRotationResponse(BaseModel):
    count: int
    data: List[ThemeRotationRecord]

class RegimeRecord(BaseModel):
    datetime: str
    regime_name: str
    pct_above_ema20: Optional[float] = None
    pct_above_ema50: Optional[float] = None
    pct_above_ema200: Optional[float] = None
    breadth_ratio: Optional[float] = None
    net_advances: Optional[int] = None
    avg_market_return_pct: Optional[float] = None
    regime_duration_days: int

class RegimeResponse(BaseModel):
    count: int
    data: List[RegimeRecord]

class RegimeSummaryItem(BaseModel):
    regime_name: str
    total_days: int
    avg_daily_return_pct: Optional[float] = None
    pct_of_time: Optional[float] = None

class RegimeSummaryResponse(BaseModel):
    count: int
    regimes: List[RegimeSummaryItem]

class AINarrativeRequest(BaseModel):
    prompt: str
    target_date: Optional[str] = None

class AINarrativeResponse(BaseModel):
    prompt: str
    target_date: str
    regime: str
    regime_duration_days: int
    leading_sectors: List[Dict[str, Any]]
    top_themes: List[Dict[str, Any]]
    top_stocks: List[Dict[str, Any]]
    markdown_narrative: str
