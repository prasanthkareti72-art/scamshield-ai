"""
Unit tests for Risk Scoring Engine
"""

import unittest
from app.services.risk_engine import RiskEngine

class TestRiskEngine(unittest.TestCase):
    def test_lottery_scam_scoring(self):
        msg = "Congratulations! You won ₹50,000 cash prize. Click http://win-prize.top immediately and forward to 10 friends to claim!"
        res = RiskEngine.evaluate(msg)
        self.assertGreaterEqual(res["estimated_risk_score"], 75.0)
        self.assertEqual(res["risk_band"], "HIGH")
        self.assertIn("Possible Scam", res["classification"])
        self.assertTrue(len(res["warning_signs"]) > 0)
        self.assertTrue(len(res["safety_advice"]) > 0)

    def test_bank_kyc_fraud_scoring(self):
        msg = "Urgent: Your SBI account will be blocked tonight at 9:30 PM due to pending KYC update. Click http://sbi-kyc-verify.xyz to update PAN."
        res = RiskEngine.evaluate(msg)
        self.assertGreaterEqual(res["estimated_risk_score"], 75.0)
        self.assertEqual(res["risk_band"], "HIGH")

    def test_safe_message_scoring(self):
        msg = "Hey Rahul, let's meet at the library around 4 PM to discuss our project slides."
        res = RiskEngine.evaluate(msg)
        self.assertLess(res["estimated_risk_score"], 25.0)
        self.assertEqual(res["risk_band"], "LOW")
        self.assertEqual(res["classification"], "Likely Safe")

    def test_fake_news_debunked_scoring(self):
        msg = "NASA confirmed that Earth will face 6 days of total darkness starting next week due to a massive solar storm! Prepare candles now!"
        res = RiskEngine.evaluate(msg)
        self.assertGreaterEqual(res["estimated_risk_score"], 70.0)
        self.assertIn("Fake News", res["classification"])

if __name__ == "__main__":
    unittest.main()
