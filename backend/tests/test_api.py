"""
Unit tests for REST API endpoints
"""

import unittest
import json
from app import create_app
from app.extensions import db

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_analyze_endpoint(self):
        payload = {
            "message": "Urgent: Your HDFC netbanking will be suspended today. Enter your PIN and OTP on http://hdfc-verify-login.xyz to restore.",
            "source": "web_dashboard"
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("analysis", data)
        self.assertGreaterEqual(data["analysis"]["estimated_risk_score"], 75.0)

    def test_whatsapp_simulator_endpoint(self):
        payload = {
            "message": "Congratulations! You won ₹25,000 lottery cash prize! Forward to 10 friends.",
            "sender_phone": "+919876543210"
        }
        res = self.client.post("/api/webhook/simulate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("ScamShield AI Analysis", data["bot_reply"])

    def test_stats_and_history_endpoints(self):
        # Insert a test scan first
        self.client.post("/api/analyze", json={"message": "Safe meeting notes for project discussion."})
        
        stats_res = self.client.get("/api/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats_data = stats_res.get_json()
        self.assertGreaterEqual(stats_data["total_scans"], 1)

        hist_res = self.client.get("/api/history")
        self.assertEqual(hist_res.status_code, 200)
        hist_data = hist_res.get_json()
        self.assertGreaterEqual(hist_data["total"], 1)

    def test_rules_endpoint(self):
        res = self.client.get("/api/rules")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("rules_engine", data)

if __name__ == "__main__":
    unittest.main()
