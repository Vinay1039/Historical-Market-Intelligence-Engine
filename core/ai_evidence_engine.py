"""
===============================================================================
 HMIE v3.1 — Multi-Domain AI Evidence Engine Orchestrator
 core/ai_evidence_engine.py

 Orchestrates Intent Parser, Router, Class A Governed Engine, and
 Class B Analytics Engine via Pydantic Intent Schema contracts.
===============================================================================
"""

import logging
from core.database import get_db_connection
from core.intent_schema import (
    StructuredIntentObject,
    TargetClass,
    IntentCategory,
    AnalyticsOperation
)
from core.canonical_research_engine import CanonicalResearchEngine
from core.analytics_engine import HistoricalAnalyticsEngine

logger = logging.getLogger(__name__)


class HMIEResearchEngine:
    def __init__(self):
        self.conn = get_db_connection()
        self.class_a_engine = CanonicalResearchEngine(self.conn)
        self.class_b_engine = HistoricalAnalyticsEngine(self.conn)

    def parse_intent(self, query_str: str) -> StructuredIntentObject:
        q_upper = query_str.upper()

        data_keywords = [
            "AUGUST 15", "INDEPENDENCE DAY", "15 AUGUST", "REPUBLIC DAY",
            "JANUARY 26", "26 JAN", "JAN 26", "PRICE ON", "VOLUME ON",
            "RETURN ON DATE", "INDICES", "WHAT ABOUT", "ALL STOCKS",
            "EVERY STOCKS", "MIDCAP", "SMALLCAP", "TOP 5", "TOP 10"
        ]

        is_data_query = any(dk in q_upper for dk in data_keywords)

        if is_data_query:
            target_class = TargetClass.CLASS_B_ANALYTICS
            if "TOP 5" in q_upper or "TOP" in q_upper:
                category = IntentCategory.RANK
                operation = AnalyticsOperation.RANK_STOCKS
            elif "MIDCAP" in q_upper or "SMALLCAP" in q_upper:
                category = IntentCategory.FILTERS
                operation = AnalyticsOperation.MULTI_MARKET_CAP_BREAKDOWN
            elif "JAN 26" in q_upper or "AUGUST 15" in q_upper:
                category = IntentCategory.STATISTICS
                operation = AnalyticsOperation.CALCULATE_STATISTICS
            else:
                category = IntentCategory.EXPLORE_EVENTS
                operation = AnalyticsOperation.TIME_SERIES_BREAKDOWN
        else:
            target_class = TargetClass.CLASS_A_RESEARCH
            category = IntentCategory.RESEARCH
            operation = AnalyticsOperation.RESEARCH_LOOKUP

        return StructuredIntentObject(
            query=query_str,
            target_class=target_class,
            intent_category=category,
            operation=operation,
            parameters={"query_upper": q_upper},
            has_canonical_study=(target_class == TargetClass.CLASS_A_RESEARCH)
        )

    def extract_entities(self, query_str: str):
        intent_obj = self.parse_intent(query_str)
        return {
            "sectors": [],
            "events": [],
            "regimes": [],
            "intent": intent_obj.intent_category.value,
            "mode": "DATA_EXPLORER" if intent_obj.target_class == TargetClass.CLASS_B_ANALYTICS else "GOVERNED_RESEARCH",
            "is_comparison": (intent_obj.intent_category == IntentCategory.COMPARE),
            "query": query_str
        }

    def query_evidence(self, query_str: str):
        intent_obj = self.parse_intent(query_str)

        if intent_obj.target_class == TargetClass.CLASS_B_ANALYTICS:
            return self.class_b_engine.execute_operation(intent_obj)
        else:
            return self.class_a_engine.query_canonical_evidence(intent_obj)


def close_engine(engine):
    try:
        engine.conn.close()
    except Exception:
        pass
