import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.main import app
from services.analog_service import AnalogService

class TestAnalogService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.service = AnalogService()

    def test_find_analogs_service(self):
        query_features = {
            "action": "PAUSE",
            "bps": 0.0,
            "cpi": 4.5,
            "regime": "SIDEWAYS",
            "tone": "NEUTRAL"
        }
        res = self.service.find_analogs(event_type="RBI", current_features=query_features, top_n=5)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["top_analogs"]), 5)
        
        top1 = res["top_analogs"][0]
        self.assertIn("similarity_pct", top1)
        self.assertIn("match_breakdown", top1)
        self.assertIn("outcomes", top1)
        self.assertGreaterEqual(top1["similarity_pct"], 80.0)

    def test_post_analogs_api_endpoint(self):
        payload = {
            "event_type": "RBI",
            "features": {
                "action": "HIKE",
                "bps": 40.0,
                "cpi": 7.8,
                "regime": "SIDEWAYS",
                "tone": "HAWKISH"
            },
            "top_n": 5
        }
        response = self.client.post("/api/v1/rbi/analogs", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(len(data["top_analogs"]), 5)

        # 2022-05-04 (+40 bps Hike) should be the #1 match for exact features!
        top_match_date = data["top_analogs"][0]["event_date"]
        self.assertEqual(top_match_date, "2022-05-04")
        self.assertEqual(data["top_analogs"][0]["similarity_pct"], 100.0)

if __name__ == '__main__':
    unittest.main()
