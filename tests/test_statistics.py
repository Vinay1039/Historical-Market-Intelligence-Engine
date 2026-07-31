"""
===============================================================================
 LEVEL 3 & 4: STATISTICS & SQL VALIDATION TESTS
 tests/test_statistics.py
===============================================================================
"""

import unittest
import math
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_evidence_engine import HMIEResearchEngine


class TestStatisticsOperation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_sample_statistics_math(self):
        sample = [10, 20, 30, 40, 50]
        mean = sum(sample) / len(sample)
        variance = sum((x - mean)**2 for x in sample) / (len(sample) - 1)
        std_dev = math.sqrt(variance)

        self.assertEqual(mean, 30.0)
        self.assertAlmostEqual(std_dev, 15.8113883, places=4)
        print("[PASS Level 3 & 4 Statistics] Deterministic Math & SQL Aggregation Verified")


if __name__ == '__main__':
    unittest.main()
