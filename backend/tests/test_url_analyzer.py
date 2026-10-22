"""
Unit tests for URL and domain security analyzer
"""

import unittest
from app.services.url_analyzer import URLAnalyzer

class TestURLAnalyzer(unittest.TestCase):
    def test_ip_address_detection(self):
        res = URLAnalyzer.analyze_single_url("http://192.168.1.100/login.apk")
        self.assertTrue(res["is_ip"])
        self.assertGreaterEqual(res["risk_score"], 45.0)

    def test_suspicious_tld_and_brand_spoofing(self):
        res = URLAnalyzer.analyze_single_url("http://sbi-kyc-verify-portal.top")
        self.assertEqual(res["spoofed_brand"], "sbi")
        self.assertGreaterEqual(res["risk_score"], 70.0)
        self.assertIn("High-Risk", res["verdict"])

    def test_official_trusted_domain(self):
        res = URLAnalyzer.analyze_single_url("https://sbi.co.in/portal")
        self.assertTrue(res["is_trusted"])
        self.assertEqual(res["risk_score"], 0.0)
        self.assertEqual(res["verdict"], "Likely Safe URL")

    def test_url_shortener(self):
        res = URLAnalyzer.analyze_single_url("https://bit.ly/3xYqz9")
        self.assertTrue(res["is_shortener"])
        self.assertGreaterEqual(res["risk_score"], 25.0)

if __name__ == "__main__":
    unittest.main()
