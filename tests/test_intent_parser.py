"""
===============================================================================
 LEVEL 1: INTENT PARSER TESTS
 tests/test_intent_parser.py
===============================================================================
"""

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ai_evidence_engine import HMIEResearchEngine
from core.intent_schema import TargetClass, IntentCategory, AnalyticsOperation


class TestIntentParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_rank_intent_parsing(self):
        intent = self.engine.parse_intent("Which NIFTY50 stock gave highest return on Diwali?")
        self.assertEqual(intent.intent_category, IntentCategory.RANK)
        self.assertEqual(intent.target_class, TargetClass.CLASS_B_ANALYTICS)
        print("[PASS Level 1] Rank Intent Parsing")

    def test_statistics_intent_parsing(self):
        intent = self.engine.parse_intent("Average return of Auto sector on August 15")
        self.assertEqual(intent.intent_category, IntentCategory.STATISTICS)
        self.assertEqual(intent.target_class, TargetClass.CLASS_B_ANALYTICS)
        print("[PASS Level 1] Statistics Intent Parsing")

    def test_research_intent_parsing(self):
        intent = self.engine.parse_intent("Does Diwali produce positive drift?")
        self.assertEqual(intent.intent_category, IntentCategory.RESEARCH)
        self.assertEqual(intent.target_class, TargetClass.CLASS_A_RESEARCH)
        print("[PASS Level 1] Research Intent Parsing")


if __name__ == '__main__':
    unittest.main()
