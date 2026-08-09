import unittest
import sys
import os

# Add workspace path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.main import app

class TestRBIRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_rbi_metrics_endpoint_all(self):
        # Test GET /api/v1/rbi/metrics with stance=ALL
        response = self.client.get("/api/v1/rbi/metrics?stance=ALL")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["stance"], "ALL")
        self.assertEqual(data["event_count"], 15)
        
        # Verify summary structure
        self.assertIn("summary", data)
        self.assertTrue(len(data["summary"]) > 0)
        first_row = data["summary"][0]
        self.assertIn("window", first_row)
        self.assertIn("mean_return", first_row)
        self.assertIn("win_rate", first_row)

    def test_rbi_metrics_endpoint_pause(self):
        # Test GET /api/v1/rbi/metrics with stance=PAUSE
        response = self.client.get("/api/v1/rbi/metrics?stance=PAUSE")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["stance"], "PAUSE")
        self.assertEqual(data["event_count"], 3) # 2021-02-05, 2024-02-08, 2025-02-07

        # Verify sectors structure
        self.assertIn("sectors", data)
        self.assertTrue(len(data["sectors"]) > 0)
        first_sec = data["sectors"][0]
        self.assertIn("sector", first_sec)
        self.assertIn("mean_return", first_sec)

        # Verify champions and laggards structure
        self.assertIn("champions", data)
        self.assertIn("laggards", data)
        self.assertTrue(len(data["champions"]) <= 5)
        self.assertTrue(len(data["laggards"]) <= 5)

    def test_rbi_metrics_invalid_stance(self):
        # Test invalid stance
        response = self.client.get("/api/v1/rbi/metrics?stance=INVALID")
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
