"""
ScamShield AI - Explainable Risk Scoring Engine
Integrates signals from NLP preprocessor, URL analyzer, scam pattern matcher,
fake news classifier, and verified fact-checking databases into a 0-100 risk score.
"""

from app.services.nlp_preprocessor import NLPPreprocessor
from app.services.url_analyzer import URLAnalyzer
from app.services.scam_detector import ScamDetector
from app.services.fake_news_detector import FakeNewsDetector

class RiskEngine:
    @staticmethod
    def evaluate(text: str, user_identifier: str = "", api_key: str = "") -> dict:
        """
        Executes end-to-end multi-factor risk assessment.
        Returns explainable score (0-100), classification, warnings, URL analysis, and advice.
        """
        normalized_text = NLPPreprocessor.normalize_text(text)
        
        # 1. Extract URLs and Behavioral Cues
        extracted_urls = NLPPreprocessor.extract_urls(normalized_text)
        behavior = NLPPreprocessor.extract_behavioral_signals(normalized_text)
        url_results = URLAnalyzer.analyze_urls(extracted_urls)
        
        # 2. Run Domain Scanners
        scam_results = ScamDetector.analyze(normalized_text)
        fake_news_results = FakeNewsDetector.analyze(normalized_text, api_key=api_key)
        
        warning_signs = []
        safety_advice = []
        is_news = fake_news_results["is_news_claim"]
        has_scam_cue = scam_results["has_scam_match"]
        highest_url_risk = url_results["highest_risk_score"]
        
        # Add behavioral warnings
        if behavior["has_urgency"]:
            warning_signs.append(f"High-pressure artificial urgency: '{', '.join(behavior['urgency_cues'][:2])}'")
        if behavior["is_shouting"]:
            warning_signs.append("Excessive capitalization / sensational shouting formatting")
        if behavior["has_financial_pressure"]:
            warning_signs.append("Demands for advance payments, processing fees, or deposits")

        # 3. Intent Determination & Scoring Logic
        # Case A: Phishing / Scam / Financial Fraud
        if has_scam_cue or highest_url_risk >= 50 or "otp" in normalized_text.lower():
            primary_cat = scam_results["primary_category"] or "PHISHING_URL_SCAM"
            base_risk = scam_results["highest_base_risk"] or 70.0
            
            # Combine signals: Base risk (50%) + ML Scam Model (25%) + URL Risk (25%)
            ml_contrib = scam_results["ml_scam_probability"] * 0.25
            url_contrib = highest_url_risk * 0.25
            score = (base_risk * 0.50) + ml_contrib + url_contrib
            
            # Boost for urgency and OTP requests
            if behavior["has_urgency"]:
                score += 8.0
            if "otp" in normalized_text.lower() or "pin" in normalized_text.lower():
                score += 10.0
                
            score = min(99.0, max(20.0, score))
            
            # Determine Classification
            if score >= 75:
                classification = "High-Risk Phishing" if highest_url_risk > 50 else "Possible Scam"
            elif score >= 50:
                classification = "Suspicious"
            else:
                classification = "Caution"

            # Populate category name
            cat_name = "Possible Scam"
            if scam_results["matched_categories"]:
                cat_name = scam_results["matched_categories"][0]["name"]
            elif highest_url_risk >= 70:
                cat_name = "High-Risk Phishing Link"

            warning_signs.extend(scam_results["indicators"])
            warning_signs.extend(url_results["all_indicators"])
            safety_advice.extend(scam_results["advice"])
            confidence = "High" if (scam_results["has_scam_match"] and highest_url_risk > 40) else "Medium"

        # Case B: News Claim / Misinformation (Separated logic as required)
        elif is_news and not has_scam_cue:
            fact_check = fake_news_results["fact_check_verification"]
            ml_fake_prob = fake_news_results["fake_news_probability"]
            
            if fact_check["verified_match"]:
                # Confirmed debunk by accredited organization
                score = 92.0
                classification = "Likely Fake News"
                cat_name = "Debunked Misinformation"
                warning_signs.append(f"Verified FALSE by {fact_check['source']}: {fact_check['summary']}")
                safety_advice.append("Do not forward or share this claim. It has been conclusively debunked by accredited fact-checkers.")
                confidence = "High (Verified by Fact-Checking Registry)"
            elif ml_fake_prob >= 70 and fake_news_results["textual_indicators"]:
                score = round(ml_fake_prob, 1)
                classification = "Likely Fake News"
                cat_name = "Suspected Viral Hoax"
                warning_signs.extend(fake_news_results["textual_indicators"])
                safety_advice.append("Check official government or mainstream press sources before believing or forwarding.")
                confidence = "Medium (Statistical NLP Model)"
            elif 35 <= ml_fake_prob < 70:
                score = 42.0
                classification = "Suspicious"
                cat_name = "Unverified Claim"
                warning_signs.append("Insufficient verifiable data to confirm or refute claim")
                warning_signs.extend(fake_news_results["textual_indicators"])
                safety_advice.append("Exercise caution. Verify facts against official gazettes or trusted news bureaus.")
                confidence = "Low (Unable to conclusively verify)"
            else:
                score = 15.0
                classification = "Likely Safe"
                cat_name = "Credible News / Announcement"
                safety_advice.append("Standard news report tone. Exercise general critical reading.")
                confidence = "Medium"

        # Case C: General Conversational / Benign Text
        else:
            if highest_url_risk > 20:
                score = highest_url_risk
                classification = "Caution" if score < 50 else "Suspicious"
                cat_name = "Unverified Link"
                warning_signs.extend(url_results["all_indicators"])
                safety_advice.append("Exercise caution before opening unfamiliar links.")
                confidence = "Medium"
            else:
                score = 8.0
                classification = "Likely Safe"
                cat_name = "General Communication"
                safety_advice.append("No immediate scam or phishing indicators detected.")
                confidence = "High"

        # URL Specific Advice if URLs exist
        if url_results["has_urls"]:
            safety_advice.append("Do not enter login credentials, passwords, or OTPs on unverified web pages.")
            if highest_url_risk >= 50:
                safety_advice.insert(0, "DO NOT click the link. It exhibits indicators of phishing or brand impersonation.")

        # Normalize score to 0 - 100
        final_score = round(min(100.0, max(0.0, score)), 1)
        
        # Standard Risk Bands:
        # 0–24: Low Risk
        # 25–49: Caution
        # 50–74: Suspicious
        # 75–100: High Risk
        if final_score >= 75:
            risk_band = "HIGH"
            risk_band_label = "High Risk"
        elif final_score >= 50:
            risk_band = "SUSPICIOUS"
            risk_band_label = "Suspicious"
        elif final_score >= 25:
            risk_band = "CAUTION"
            risk_band_label = "Caution"
        else:
            risk_band = "LOW"
            risk_band_label = "Low Risk"

        # Deduplicate warnings and advice
        unique_warnings = list(dict.fromkeys(warning_signs))
        unique_advice = list(dict.fromkeys(safety_advice))

        if not unique_warnings:
            unique_warnings = ["No suspicious keywords or deceptive URL structures detected."]

        disclaimer = (
            "Note: This is an automated algorithmic risk assessment based on pattern analysis and machine learning, "
            "not a definitive legal finding or guarantee. Always exercise personal vigilance."
        )

        explanation = (
            f"The submitted message received an estimated risk score of {int(final_score)}/100 ({risk_band_label}). "
            f"Evaluated as {cat_name} based on "
            f"{len(unique_warnings)} detected indicator(s) and linguistic analysis."
        )

        return {
            "estimated_risk_score": final_score,
            "risk_band": risk_band,
            "risk_band_label": risk_band_label,
            "classification": classification,
            "category": cat_name,
            "warning_signs": unique_warnings,
            "safety_advice": unique_advice,
            "url_analysis": url_results,
            "fake_news_analysis": fake_news_results,
            "scam_analysis": {
                "matched_categories": scam_results["matched_categories"],
                "ml_scam_probability": scam_results["ml_scam_probability"]
            },
            "confidence_level": confidence,
            "disclaimer": disclaimer,
            "explanation": explanation
        }
