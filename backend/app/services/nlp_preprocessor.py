"""
ScamShield AI - NLP Preprocessor Service
Handles text cleaning, tokenization, URL/domain extraction, PII masking, and behavioral cue detection.
"""

import re
import hashlib
import unicodedata
from urllib.parse import urlparse

# Regular expressions for URL, Phone, and PII patterns
URL_REGEX = re.compile(
    r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’]))'
)
IP_URL_REGEX = re.compile(r'https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?')
PHONE_REGEX = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?(?:(?:\d{5}[-.\s]?\d{5})|(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})|(?:\d{10,12}))'
)
OTP_CODE_REGEX = re.compile(r'\b\d{4,8}\b(?=.*(?:otp|code|pin|verification))', re.IGNORECASE)

# Behavioral Urgency & Action cues
URGENCY_KEYWORDS = [
    "urgent", "immediately", "right now", "within 24 hours", "within 2 hours",
    "before midnight", "last chance", "expires today", "final notice", "blocked tonight",
    "suspended today", "account freeze", "immediate action required"
]

CALL_TO_ACTION_KEYWORDS = [
    "click here", "click link", "download apk", "install app", "call this number",
    "forward to", "share with", "enter pin", "verify now", "claim prize", "claim now"
]

FINANCIAL_PRESSURE_KEYWORDS = [
    "processing fee", "security deposit", "registration fee", "tax clearance",
    "pay now", "upi payment", "transfer money", "gift card", "crypto deposit"
]

class NLPPreprocessor:
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalizes unicode characters, collapses whitespace, and trims."""
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", str(text))
        # Remove null bytes or non-printable chars
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return " ".join(text.split())

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extracts all full URLs, IP URLs, and shortened links from text."""
        if not text:
            return []
        
        matches = URL_REGEX.findall(text)
        urls = []
        for match in matches:
            url_str = match[0] if isinstance(match, tuple) else match
            url_str = url_str.strip().rstrip(".,;!?)")
            if not url_str.startswith(("http://", "https://")):
                url_str = "http://" + url_str
            if url_str not in urls:
                urls.append(url_str)
        
        # Check IP urls explicitly
        ip_matches = IP_URL_REGEX.findall(text)
        for ip_u in ip_matches:
            if ip_u not in urls:
                urls.append(ip_u)
                
        return urls

    @staticmethod
    def extract_behavioral_signals(text: str) -> dict:
        """Detects urgency, call-to-action pressure, and uppercase shouting."""
        normalized = text.lower()
        
        # Check Urgency
        detected_urgency = [k for k in URGENCY_KEYWORDS if k in normalized]
        
        # Check Calls to Action
        detected_cta = [k for k in CALL_TO_ACTION_KEYWORDS if k in normalized]
        
        # Check Financial Pressure
        detected_finance = [k for k in FINANCIAL_PRESSURE_KEYWORDS if k in normalized]
        
        # Check ALL CAPS ratio
        letters = [c for c in text if c.isalpha()]
        uppercase_ratio = 0.0
        if len(letters) >= 10:
            upper_count = sum(1 for c in letters if c.isupper())
            uppercase_ratio = upper_count / len(letters)
            
        exclamation_count = text.count("!")
        
        return {
            "has_urgency": len(detected_urgency) > 0,
            "urgency_cues": detected_urgency,
            "has_cta": len(detected_cta) > 0,
            "cta_cues": detected_cta,
            "has_financial_pressure": len(detected_finance) > 0,
            "financial_cues": detected_finance,
            "uppercase_ratio": round(uppercase_ratio, 2),
            "is_shouting": uppercase_ratio > 0.4 and len(letters) > 15,
            "exclamation_count": exclamation_count
        }

    @staticmethod
    def mask_pii(text: str) -> str:
        """Redacts phone numbers, email addresses, and potential card/account numbers for privacy."""
        if not text:
            return ""
        
        # Mask phone numbers
        masked = PHONE_REGEX.sub("[PHONE REDACTED]", text)
        
        # Mask emails
        masked = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL REDACTED]', masked)
        
        # Mask 16-digit cards or 12-digit Aadhaar/account sequences
        masked = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD REDACTED]', masked)
        masked = re.sub(r'\b\d{12}\b', '[ACCOUNT/ID REDACTED]', masked)
        
        return masked

    @staticmethod
    def hash_identifier(identifier: str) -> str:
        """Generates a non-reversible SHA-256 hash for logging anonymized user identities."""
        if not identifier:
            return "anonymous"
        cleaned = re.sub(r'\D', '', str(identifier))
        # Standardize to last 10 digits if available
        if len(cleaned) >= 10:
            cleaned = cleaned[-10:]
        salt = "scamshield-privacy-salt-2026"
        return hashlib.sha256(f"{salt}:{cleaned}".encode("utf-8")).hexdigest()

    @staticmethod
    def get_safe_snippet(text: str, max_chars: int = 100) -> str:
        """Returns a sanitized, masked, truncated text snippet for safe audit viewing."""
        masked = NLPPreprocessor.mask_pii(text)
        clean = " ".join(masked.split())
        if len(clean) > max_chars:
            return clean[:max_chars] + "..."
        return clean
