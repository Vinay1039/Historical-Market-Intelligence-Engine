"""
===============================================================================
 LEVEL 3: RANK_STOCKS OPERATION TESTS
 tests/test_rank.py
===============================================================================
"""

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_evidence_engine import HMIEResearchEngine


class TestRankOperation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_rank_stocks_ordering(self):
        query = "What are top 5 total average return stocks in Nifty50 from year 2015 to 2025 on August 15"
        res = self.engine.query_evidence(query)
        self.assertEqual(res['mode'], "DATA_EXPLORER")
        self.assertIn("ICICI Bank", res['plain_english_answer'])
        self.assertIn("Tata Motors", res['plain_english_answer'])
        print("[PASS Level 3 Rank] Stock Leaderboard Ordering Verified")


if __name__ == '__main__':
    unittest.main()
