from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StrategySummaryRecord(BaseModel):
    strategy_id: int
    strategy_code: str
    strategy_name: str
    benchmark: str
    start_date: str
    end_date: str
    total_return_pct: float
    cagr_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    sharpe_ratio: float
    profit_factor: float
    total_trades: int

class StrategySummaryResponse(BaseModel):
    count: int
    data: List[StrategySummaryRecord]

class TradeRecord(BaseModel):
    trade_id: int
    strategy_code: str
    symbol_or_code: str
    entry_date: str
    exit_date: str
    holding_days: int
    entry_price: float
    exit_price: float
    return_pct: float
    win_flag: int

class TradeResponse(BaseModel):
    count: int
    data: List[TradeRecord]

class BenchmarkPerformanceRecord(BaseModel):
    strategy_code: str
    benchmark_code: str
    benchmark_name: str
    strategy_cagr_pct: float
    benchmark_cagr_pct: float
    strategy_volatility_pct: float
    benchmark_volatility_pct: float
    alpha_pct: float
    beta: float
    information_ratio: float
    tracking_error_pct: float

class BenchmarkPerformanceResponse(BaseModel):
    count: int
    data: List[BenchmarkPerformanceRecord]

class FeeSensitivityRecord(BaseModel):
    strategy_code: str
    fee_level_pct: float
    net_total_return_pct: float
    net_cagr_pct: float
    net_max_drawdown_pct: float
    net_sharpe_ratio: float
    net_profit_factor: float
    cagr_drag_pct: float
    break_even_fee_pct: Optional[float] = None
    max_sustainable_cost_pct: Optional[float] = None
    robustness_classification: Optional[str] = None

class FeeSensitivityResponse(BaseModel):
    count: int
    data: List[FeeSensitivityRecord]

class PlausibilityAuditRecord(BaseModel):
    audit_id: int
    run_date: Optional[str] = None
    strategy_code: str
    benchmark_code: Optional[str] = None
    rule_code: str
    rule_description: str
    observed_value: str
    threshold_value: str
    severity: str           # 'PASS', 'WARNING', 'FAIL'
    recommendation: str

class PlausibilityAuditResponse(BaseModel):
    total_rules_evaluated: int
    pass_count: int
    warning_count: int
    fail_count: int
    gate_passed: bool       # True only if fail_count == 0
    data: List[PlausibilityAuditRecord]

class CanonicalResearchRecord(BaseModel):
    execution_id: int
    study_id: str
    study_name: str
    methodology_version: str
    dataset_version: str
    git_commit: str
    execution_timestamp: str
    canonical_flag: int
    execution_hash: str
    result_hash: str
    summary_metrics_json: str
    limitations_json: Optional[str] = None
    supersedes_exec_id: Optional[int] = None

class CanonicalResearchResponse(BaseModel):
    count: int
    data: List[CanonicalResearchRecord]
