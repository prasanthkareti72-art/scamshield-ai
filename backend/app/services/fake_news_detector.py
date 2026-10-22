"""
ScamShield AI - Fake News Detection Module
Utilizes trained TF-IDF + Logistic Regression model, linguistic analysis,
and fact-checking verification.
"""

import os
import joblib
from app.services.fact_checker import FactChecker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "fake_news_model.pkl")

# Textual indicators of viral misinformation and pseudoscience
SENSATIONAL_MARKERS = [
    "shocking truth", "secret cure", "big pharma is hiding", "doctors are shocked",
    "miracle cure", "share before deleted", "share before it gets deleted",
    "proud moment", "declared by unesco", "nasa confirmed", "cosmic rays tonight",
    "switch off your phone", "turn off your phone", "save a life", "100% immune"
]

NEWS_CLAIM_KEYWORDS = [
    "announced", "ministry", "government", "cabinet", "reserve bank", "rbi", "who",
    "study", "scientists", "court", "parliament", "isro", "nasa", "pmo",
    "breaking", "alert", "curfew", "order", "subsidy", "disease", "virus"
]

class FakeNewsDetector:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy loader for serialized Fake News classifier."""
        if cls._model is None:
            if os.path.exists(MODEL_PATH):
                try:
                    cls._model = joblib.load(MODEL_PATH)
                except Exception as e:
                    print(f"[WARN] Failed to load fake_news_model.pkl: {e}")
                    cls._model = None
        return cls._model

    @staticmethod
    def is_news_claim(text: str) -> bool:
        """Determines if the text reads like a news report, public directive, or viral claim."""
        text_lower = text.lower()
        matches = [kw for kw in NEWS_CLAIM_KEYWORDS if kw in text_lower]
        return len(matches) >= 1 or len(text.split()) > 15

    @staticmethod
    def detect_textual_indicators(text: str) -> list[str]:
        """Detects linguistic red flags associated with fabricated viral claims."""
        indicators = []
        text_lower = text.lower()

        for marker in SENSATIONAL_MARKERS:
            if marker in text_lower:
                indicators.append(f"Sensationalist / conspiracy phrasing detected: '{marker.title()}'")

        if text.count("!") >= 3:
            indicators.append("Excessive exclamation marks (sensationalist urgency)")

        if "forward to" in text_lower or "share to" in text_lower or "send to" in text_lower:
            indicators.append("Calls to virally redistribute to groups or contacts")

        if any(w in text_lower for w in ["100% cure", "instant cure", "cures cancer", "cure in 3 days"]):
            indicators.append("Unsubstantiated medical miracle claim with no clinical citation")

        if "switch off" in text_lower and "cosmic" in text_lower:
            indicators.append("Known urban legend regarding cosmic rays / radiation")

        return list(dict.fromkeys(indicators))

    @staticmethod
    def analyze(text: str, api_key: str = "") -> dict:
        """
        Runs ML prediction, rule-based indicator detection, and accredited fact-check verification.
        """
        is_claim = FakeNewsDetector.is_news_claim(text)
        indicators = FakeNewsDetector.detect_textual_indicators(text)
        
        # 1. Fact-Check Verification against accredited databases
        fact_check_result = FactChecker.verify_claim(text, api_key=api_key)
        
        # 2. ML Model Prediction
        model = FakeNewsDetector.get_model()
        ml_prob = 0.5 # neutral default fallback
        model_available = False

        if model is not None:
            try:
                # predict_proba returns [prob_genuine, prob_fake]
                probs = model.predict_proba([text])[0]
                ml_prob = float(probs[1]) # probability of being fake news (class 1)
                model_available = True
            except Exception as e:
                print(f"[WARN] Error running fake news model: {e}")
                model_available = False

        # Calculate confidence level
        if fact_check_result["verified_match"]:
            confidence = "High (Verified by accredited fact-checker)"
            # If accredited fact-checker marked it FALSE, risk probability is 0.95+
            final_prob = 0.95
        elif model_available:
            confidence = "Medium (Statistical ML Prediction)"
            final_prob = ml_prob
            # If strong textual indicators exist, boost probability
            if len(indicators) >= 2:
                final_prob = min(0.95, final_prob + 0.20)
        else:
            confidence = "Low (Rule-based heuristics fallback)"
            final_prob = 0.80 if len(indicators) > 0 else 0.30

        return {
            "is_news_claim": is_claim,
            "fake_news_probability": round(final_prob * 100, 1),
            "model_available": model_available,
            "confidence": confidence,
            "textual_indicators": indicators,
            "fact_check_verification": fact_check_result
        }
