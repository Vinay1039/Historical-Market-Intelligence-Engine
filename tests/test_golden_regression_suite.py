"""
===============================================================================
 LEVEL 8 & 9: GOLDEN REGRESSION & USER ACCEPTANCE SUITE
 tests/test_golden_regression_suite.py
===============================================================================
"""

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_evidence_engine import HMIEResearchEngine


class TestGoldenRegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_golden_acceptance_queries(self):
        golden_queries = [
            ("Compare Auto vs Bank on Diwali", "GOVERNED_RESEARCH"),
            ("Top 5 NIFTY50 stocks on August 15", "DATA_EXPLORER"),
            ("What is the total average return of sectors from year 2015 to 2025 on Jan 26", "DATA_EXPLORER"),
            ("Which NIFTY50 stock gave more return in every Holi from year 2020 to 2025", "DATA_EXPLORER"),
            ("Which event produced the strongest rally: Elections, RBI policy, or Budget?", "GOVERNED_RESEARCH"),
            ("Is Momentum robust during Bear market regimes?", "GOVERNED_RESEARCH")
        ]

        for q, expected_mode in golden_queries:
            res = self.engine.query_evidence(q)
            self.assertEqual(res['mode'], expected_mode, f"Failed regression for query: {q}")
            print(f"[PASS Level 8 & 9 Acceptance] '{q[:35]}...' -> {expected_mode}")


if __name__ == '__main__':
    unittest.main()
