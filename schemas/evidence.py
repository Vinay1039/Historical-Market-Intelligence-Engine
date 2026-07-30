from pydantic import BaseModel
from typing import List, Optional

class CorrectionRecord(BaseModel):
    event_id: int
    event_name: str
    peak_date: str
    trough_date: str
    recovery_date: Optional[str] = None
    max_drawdown_pct: float
    correction_days: int
    recovery_days: Optional[int] = None
    recovery_type: str
    top_sector_30d: str
    top_sector_60d: str
    top_theme_60d: str

class CorrectionResponse(BaseModel):
    count: int
    data: List[CorrectionRecord]

class MacroEventRecord(BaseModel):
    event_id: int
    event_name: str
    event_category: str
    event_date: str
    regime_at_event: str
    pre_30d_market_return: float
    post_30d_market_return: float
    top_sector_post_30d: str
    top_theme_post_30d: str

class MacroEventResponse(BaseModel):
    count: int
    data: List[MacroEventRecord]

class RecoveryStatsResponse(BaseModel):
    total_corrections: int
    avg_drawdown_pct: float
    avg_correction_days: float
    avg_recovery_days: float
    v_shaped_count: int
    u_shaped_count: int
    most_frequent_recovering_sector_60d: str
