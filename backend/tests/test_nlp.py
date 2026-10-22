"""
Unit tests for NLP Preprocessor service
"""

import unittest
from app.services.nlp_preprocessor import NLPPreprocessor

class TestNLPPreprocessor(unittest.TestCase):
    def test_url_extraction(self):
        text = "Check this out: https://secure-bank.xyz/login and also http://192.168.1.1/admin"
        urls = NLPPreprocessor.extract_urls(text)
        self.assertIn("https://secure-bank.xyz/login", urls)
        self.assertIn("http://192.168.1.1/admin", urls)

    def test_pii_masking(self):
        text = "Call me at +91 98765 43210 or card 4111-2222-3333-4444"
        masked = NLPPreprocessor.mask_pii(text)
        self.assertNotIn("98765", masked)
        self.assertNotIn("4111-2222", masked)
        self.assertIn("[PHONE REDACTED]", masked)
        self.assertIn("[CARD REDACTED]", masked)

    def test_behavioral_signals(self):
        text = "URGENT ACTION REQUIRED IMMEDIATELY! ACCOUNT BLOCKED TONIGHT!"
        signals = NLPPreprocessor.extract_behavioral_signals(text)
        self.assertTrue(signals["has_urgency"])
        self.assertTrue(signals["is_shouting"])
        self.assertGreater(signals["uppercase_ratio"], 0.5)

    def test_identifier_hashing(self):
        phone1 = "+91 98765 43210"
        phone2 = "9876543210"
        hash1 = NLPPreprocessor.hash_identifier(phone1)
        hash2 = NLPPreprocessor.hash_identifier(phone2)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64) # SHA-256 length

if __name__ == "__main__":
    unittest.main()
