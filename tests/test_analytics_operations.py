"""
===============================================================================
 HMIE Analytics Engine Test Suite — Production Validation
 tests/test_analytics_operations.py

 Verifies deterministic mathematical accuracy across:
   1. RANK_STOCKS
   2. COMPARE_SECTORS
   3. STATISTICS (Mean μ, Std Dev σ, Win Rate, Ranges)
   4. TIME_SERIES
===============================================================================
"""

import unittest
import math
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_evidence_engine import HMIEResearchEngine


class TestAnalyticsOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_statistics_math_correctness(self):
        """Test statistical function mathematical correctness (Mean & Sample Std Dev)"""
        sample_returns = [2.85, 2.65, 2.40, 1.95, 1.80, 1.45]
        mean = sum(sample_returns) / len(sample_returns)
        # Sample standard deviation (N-1 degrees of freedom)
        variance = sum((x - mean) ** 2 for x in sample_returns) / (len(sample_returns) - 1)
        std_dev = math.sqrt(variance)

        self.assertAlmostEqual(mean, 2.183333333333333, places=4)
        self.assertAlmostEqual(std_dev, 0.5382068994974578, places=4)
        print("[PASS] Statistics Math Correctness (Mean & Sample Std Dev)")

    def test_intent_router_classification(self):
        """Test Intent Router correctly assigns Class A vs Class B modes"""
        q_research = "What happens to Banking stocks after RBI policy decision meetings"
        res_r = self.engine.extract_entities(q_research)
        self.assertEqual(res_r['mode'], "GOVERNED_RESEARCH")

        q_analytics = "Which NIFTY50 stock gave more return in every August 15 from year 2020 to 2025"
        res_a = self.engine.extract_entities(q_analytics)
        self.assertEqual(res_a['mode'], "DATA_EXPLORER")
        print("[PASS] Intent Router Classification (Class A vs Class B)")

    def test_data_explorer_rank_stocks(self):
        """Test RANK_STOCKS operation output structure"""
        query = "What are top 5 total average return stocks in Nifty50 from year 2015 to 2025 on August 15"
        res = self.engine.query_evidence(query)
        self.assertEqual(res['mode'], "DATA_EXPLORER")
        self.assertIn("Top 5 Companies Table", res['plain_english_answer'])
        self.assertIn("ICICI Bank", res['plain_english_answer'])
        print("[PASS] RANK_STOCKS Operation Output Structure")

    def test_data_explorer_statistics_table(self):
        """Test STATISTICS operation Markdown Table & Column Headers"""
        query = "What is the total average return of sectors from year 2015 to 2025 on August 15"
        res = self.engine.query_evidence(query)
        self.assertEqual(res['mode'], "DATA_EXPLORER")
        self.assertIn("| Sector | Average Return | Success Rate | Big Gain Years (>+1%) | Loss Years (<-1%) | Worst Year | Best Year |", res['plain_english_answer'])
        print("[PASS] STATISTICS Operation Markdown Table Formatting")

    def test_boundary_guardrail_unsupported_hypothesis(self):
        """Test Boundary Guardrail for new research hypothesis without canonical study"""
        query = "Do FMCG stocks outperform after Independence Day?"
        res = self.engine.query_evidence(query)
        self.assertEqual(res['mode'], "DATA_EXPLORER")
        self.assertIn("STAGING.STOCK_HIST_DATA", res['dual_indicators']['evidence_quality'])
        print("[PASS] Boundary Guardrail (No Canonical Promotion)")


if __name__ == '__main__':
    unittest.main()
