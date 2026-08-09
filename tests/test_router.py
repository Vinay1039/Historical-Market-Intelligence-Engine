"""
===============================================================================
 LEVEL 2: ROUTER TESTS
 tests/test_router.py
===============================================================================
"""

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ai_evidence_engine import HMIEResearchEngine


class TestRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HMIEResearchEngine()

    def test_routing_matrix(self):
        matrix = [
            ("Does Holi outperform Diwali?", "GOVERNED_RESEARCH"),
            ("Top stocks on Holi", "DATA_EXPLORER"),
            ("What happens to Banking stocks after RBI policy decision meetings", "GOVERNED_RESEARCH"),
            ("Compare sectors on Republic Day", "DATA_EXPLORER")
        ]

        for q, expected in matrix:
            res = self.engine.extract_entities(q)
            self.assertEqual(res['mode'], expected, f"Failed for query: {q}")
            print(f"[PASS Level 2 Router] '{q[:30]}...' -> {expected}")


if __name__ == '__main__':
    unittest.main()
