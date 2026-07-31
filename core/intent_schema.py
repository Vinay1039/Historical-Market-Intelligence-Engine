"""
===============================================================================
 HMIE v3.1 — Intent Schema & Pydantic Contracts
 core/intent_schema.py

 Defines strict, type-safe data structures for user intent classification,
 parameter extraction, and engine routing.
===============================================================================
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TargetClass(str, Enum):
    CLASS_A_RESEARCH = "CLASS_A_RESEARCH"
    CLASS_B_ANALYTICS = "CLASS_B_ANALYTICS"


class IntentCategory(str, Enum):
    COMPARE = "COMPARE"
    RANK = "RANK"
    EXPLORE_EVENTS = "EXPLORE_EVENTS"
    STATISTICS = "STATISTICS"
    TIME_SERIES = "TIME_SERIES"
    FILTERS = "FILTERS"
    PRESENTATION = "PRESENTATION"
    RESEARCH = "RESEARCH"


class AnalyticsOperation(str, Enum):
    RANK_STOCKS = "RANK_STOCKS"
    COMPARE_SECTORS = "COMPARE_SECTORS"
    CALCULATE_STATISTICS = "CALCULATE_STATISTICS"
    TIME_SERIES_BREAKDOWN = "TIME_SERIES_BREAKDOWN"
    MULTI_MARKET_CAP_BREAKDOWN = "MULTI_MARKET_CAP_BREAKDOWN"
    RESEARCH_LOOKUP = "RESEARCH_LOOKUP"


class EventWindow(BaseModel):
    pre_days: int = Field(default=3, description="Trading days before event")
    post_days: int = Field(default=3, description="Trading days after event")


class StructuredIntentObject(BaseModel):
    query: str
    target_class: TargetClass
    intent_category: IntentCategory
    operation: AnalyticsOperation
    parameters: Dict[str, Any] = Field(default_factory=dict)
    has_canonical_study: bool = Field(default=False)
