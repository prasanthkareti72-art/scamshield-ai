"""
ScamShield AI - Scam & Phishing Detection Module
Combines ML text classifier with specialized rule-based regex and keyword scanners
for financial fraud, credential harvesting, lottery scams, and impersonation.
"""

import os
import json
import re
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATTERNS_PATH = os.path.join(BASE_DIR, "data", "scam_patterns.json")
MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "scam_model.pkl")

class ScamDetector:
    _patterns = None
    _model = None

    @classmethod
    def load_patterns(cls):
        """Loads structured pattern rules from JSON."""
        if cls._patterns is None:
            if os.path.exists(PATTERNS_PATH):
                with open(PATTERNS_PATH, "r", encoding="utf-8") as f:
                    cls._patterns = json.load(f)
            else:
                cls._patterns = {"categories": {}, "url_rules": {}}
        return cls._patterns

    @classmethod
    def get_model(cls):
        """Lazy loads ML scam classifier."""
        if cls._model is None:
            if os.path.exists(MODEL_PATH):
                try:
                    cls._model = joblib.load(MODEL_PATH)
                except Exception as e:
                    print(f"[WARN] Failed to load scam_model.pkl: {e}")
                    cls._model = None
        return cls._model

    @staticmethod
    def analyze(text: str) -> dict:
        """
        Scans message for known scam categories, regex signatures, and ML probability.
        """
        patterns_data = ScamDetector.load_patterns()
        categories_db = patterns_data.get("categories", {})
        
        matched_categories = []
        indicators = []
        recommended_advice = []
        text_lower = text.lower()
        
        # 1. Evaluate Rule-based categories
        for cat_key, cat_info in categories_db.items():
            matched_keywords = [kw for kw in cat_info.get("keywords", []) if kw in text_lower]
            matched_regex = False
            
            for regex_str in cat_info.get("regex_patterns", []):
                try:
                    if re.search(regex_str, text):
                        matched_regex = True
                        break
                except Exception:
                    continue

            # If regex matched or at least 2 key phrases matched
            if matched_regex or len(matched_keywords) >= 2:
                matched_categories.append({
                    "category_id": cat_key,
                    "name": cat_info["name"],
                    "severity": cat_info["severity"],
                    "base_risk": cat_info["base_risk"],
                    "description": cat_info["description"]
                })
                indicators.append(f"Detected pattern for {cat_info['name']}")
                recommended_advice.extend(cat_info.get("advice", []))
            elif len(matched_keywords) == 1:
                # Weak cue
                indicators.append(f"Suspicious keyword match: '{matched_keywords[0]}'")

        # 2. ML Scam Classifier Prediction
        model = ScamDetector.get_model()
        ml_prob = 0.0
        model_available = False

        if model is not None:
            try:
                # [prob_safe, prob_scam]
                probs = model.predict_proba([text])[0]
                ml_prob = float(probs[1])
                model_available = True
            except Exception as e:
                print(f"[WARN] Scam ML prediction error: {e}")
                model_available = False

        # Identify Primary Category
        primary_cat = None
        highest_base_risk = 0.0

        if matched_categories:
            # Sort by base_risk descending
            matched_categories.sort(key=lambda x: x["base_risk"], reverse=True)
            primary_cat = matched_categories[0]["category_id"]
            highest_base_risk = matched_categories[0]["base_risk"]
        elif ml_prob > 0.65:
            primary_cat = "GENERAL_SUSPICIOUS_PHISHING"
            highest_base_risk = ml_prob * 100
            indicators.append("Linguistic patterns align closely with known phishing templates")

        # Deduplicate indicators and advice
        unique_indicators = list(dict.fromkeys(indicators))
        unique_advice = list(dict.fromkeys(recommended_advice))

        # Default advice if none triggered
        if not unique_advice:
            unique_advice = [
                "Never share OTPs, passwords, or personal banking credentials.",
                "Always verify unexpected communications directly through official channels."
            ]

        return {
            "has_scam_match": len(matched_categories) > 0 or ml_prob > 0.70,
            "primary_category": primary_cat,
            "matched_categories": matched_categories,
            "highest_base_risk": highest_base_risk,
            "ml_scam_probability": round(ml_prob * 100, 1),
            "model_available": model_available,
            "indicators": unique_indicators,
            "advice": unique_advice
        }
