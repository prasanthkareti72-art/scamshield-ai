"""
ScamShield AI - Analysis REST API Blueprint
Provides interactive message & URL scanning endpoint with database logging.
"""

from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.scan_record import ScanRecord
from app.services.risk_engine import RiskEngine
from app.services.nlp_preprocessor import NLPPreprocessor
from app.services.twilio_service import TwilioService

analyze_bp = Blueprint("analyze", __name__, url_prefix="/api")

@analyze_bp.route("/analyze", methods=["POST"])
def analyze_content():
    """
    POST /api/analyze
    Analyzes submitted message text or URL and stores anonymized scan audit record.
    """
    data = request.get_json(silent=True) or {}
    message_text = data.get("message", "").strip()
    source = data.get("source", "web_dashboard")
    user_id = data.get("user_id", "web-user")

    if not message_text:
        return jsonify({
            "error": "Missing message content to analyze. Please provide a message or URL string."
        }), 400

    api_key = current_app.config.get("GOOGLE_FACT_CHECK_API_KEY", "")
    
    # 1. Run Risk Scoring Engine
    analysis = RiskEngine.evaluate(message_text, user_identifier=user_id, api_key=api_key)
    
    # 2. Format WhatsApp-style preview message
    whatsapp_preview = TwilioService.format_whatsapp_response(analysis)

    # 3. Privacy-preserving Database Persistence
    user_hash = NLPPreprocessor.hash_identifier(user_id)
    masked_snippet = NLPPreprocessor.get_safe_snippet(message_text, max_chars=140)
    urls_detected = analysis.get("url_analysis", {}).get("detailed_results", [])
    
    try:
        record = ScanRecord(
            source=source,
            user_identifier_hash=user_hash,
            risk_score=analysis["estimated_risk_score"],
            risk_level=analysis["risk_band"],
            classification=analysis["classification"],
            category=analysis["category"],
            masked_content_snippet=masked_snippet,
            content_length=len(message_text),
            has_url=analysis.get("url_analysis", {}).get("has_urls", False),
            urls_detected=[u.get("url") for u in urls_detected],
            detected_indicators=analysis["warning_signs"],
            advice_list=analysis["safety_advice"],
            url_risk_score=analysis.get("url_analysis", {}).get("highest_risk_score", 0.0),
            ml_fake_news_prob=analysis.get("fake_news_analysis", {}).get("fake_news_probability", 0.0),
            ml_scam_prob=analysis.get("scam_analysis", {}).get("ml_scam_probability", 0.0),
            fact_check_matched=analysis.get("fake_news_analysis", {}).get("fact_check_verification", {}).get("verified_match", False),
            fact_check_source=analysis.get("fake_news_analysis", {}).get("fact_check_verification", {}).get("source"),
            confidence_level=analysis["confidence_level"],
            explanation_summary=analysis["explanation"]
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id
        scan_uuid = record.scan_uuid
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to persist scan record: {e}")
        record_id = None
        scan_uuid = None

    return jsonify({
        "success": True,
        "scan_id": record_id,
        "scan_uuid": scan_uuid,
        "analysis": analysis,
        "whatsapp_preview": whatsapp_preview
    }), 200
