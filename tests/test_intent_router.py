"""
===============================================================================
 HMIE v3.1 — Intent Router & Schema Test Harness
 tests/test_intent_router.py

 Tests Pydantic Intent Object parsing, Intent Router classification,
 and engine execution across Class A and Class B queries.
===============================================================================
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_evidence_engine import HMIEResearchEngine
from core.intent_schema import TargetClass, IntentCategory, AnalyticsOperation


class TestIntentRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_class_a_research_intent(self):
        query = "What happens to Banking stocks after RBI policy decision meetings"
        intent_obj = self.engine.parse_intent(query)
        self.assertEqual(intent_obj.target_class, TargetClass.CLASS_A_RESEARCH)
        self.assertEqual(intent_obj.intent_category, IntentCategory.RESEARCH)
        self.assertEqual(intent_obj.operation, AnalyticsOperation.RESEARCH_LOOKUP)
        print("[PASS] Class A Research Intent Classification")

    def test_class_b_rank_stocks_intent(self):
        query = "What are top 5 total average return stocks in Nifty50 from year 2015 to 2025 on August 15"
        intent_obj = self.engine.parse_intent(query)
        self.assertEqual(intent_obj.target_class, TargetClass.CLASS_B_ANALYTICS)
        self.assertEqual(intent_obj.intent_category, IntentCategory.RANK)
        self.assertEqual(intent_obj.operation, AnalyticsOperation.RANK_STOCKS)
        print("[PASS] Class B Rank Stocks Intent Classification")

    def test_class_b_jan26_statistics_intent(self):
        query = "What is the total average return of sectors from year 2015 to 2025 on Jan 26"
        intent_obj = self.engine.parse_intent(query)
        self.assertEqual(intent_obj.target_class, TargetClass.CLASS_B_ANALYTICS)
        self.assertEqual(intent_obj.intent_category, IntentCategory.STATISTICS)
        self.assertEqual(intent_obj.operation, AnalyticsOperation.CALCULATE_STATISTICS)
        print("[PASS] Class B Statistics Intent Classification")

    def test_class_b_multimarket_cap_filters_intent(self):
        query = "Which NIFTY50, MIDCAP, SMALLCAP stock gave more return in every August 15"
        intent_obj = self.engine.parse_intent(query)
        self.assertEqual(intent_obj.target_class, TargetClass.CLASS_B_ANALYTICS)
        self.assertEqual(intent_obj.intent_category, IntentCategory.FILTERS)
        self.assertEqual(intent_obj.operation, AnalyticsOperation.MULTI_MARKET_CAP_BREAKDOWN)
        print("[PASS] Class B Multi-Market Cap Intent Classification")


if __name__ == '__main__':
    unittest.main()
