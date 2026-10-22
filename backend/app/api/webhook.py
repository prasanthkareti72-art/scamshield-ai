"""
ScamShield AI - WhatsApp Webhook Blueprint
Processes inbound Twilio WhatsApp webhooks, validates signatures,
records audits, and returns TwiML responses.
"""

from flask import Blueprint, request, Response, jsonify, current_app
from app.extensions import db
from app.models.scan_record import ScanRecord
from app.services.risk_engine import RiskEngine
from app.services.nlp_preprocessor import NLPPreprocessor
from app.services.twilio_service import TwilioService

webhook_bp = Blueprint("webhook", __name__, url_prefix="/api/webhook")

# Cache to prevent duplicate webhook processing for the same Twilio MessageSid
PROCESSED_MESSAGE_SIDS = set()

@webhook_bp.route("/whatsapp", methods=["GET"])
def webhook_health():
    """Health check endpoint to test Twilio webhook reachability."""
    return jsonify({
        "status": "online",
        "service": "ScamShield AI WhatsApp Webhook",
        "signature_verification": current_app.config.get("VERIFY_TWILIO_SIGNATURE", False)
    }), 200

@webhook_bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    POST /api/webhook/whatsapp
    Twilio WhatsApp incoming webhook handler.
    """
    auth_token = current_app.config.get("TWILIO_AUTH_TOKEN", "")
    verify_sig = current_app.config.get("VERIFY_TWILIO_SIGNATURE", False)

    # 1. Validate Twilio Request Signature
    if verify_sig and auth_token:
        if not TwilioService.validate_request(request, auth_token, verify_enabled=True):
            current_app.logger.warning("Rejected invalid Twilio webhook signature.")
            return Response("Invalid Twilio Signature", status=403)

    # 2. Extract Twilio Parameters
    message_sid = request.form.get("MessageSid", "").strip()
    from_user = request.form.get("From", "").strip() # e.g. "whatsapp:+919876543210"
    body_text = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", 0) or 0)

    # Handle duplicate webhook delivery
    if message_sid:
        if message_sid in PROCESSED_MESSAGE_SIDS:
            current_app.logger.info(f"Duplicate MessageSid {message_sid} ignored.")
            return Response("", status=200, mimetype="text/xml")
        PROCESSED_MESSAGE_SIDS.add(message_sid)
        if len(PROCESSED_MESSAGE_SIDS) > 2000:
            PROCESSED_MESSAGE_SIDS.clear()

    # Handle Media without text
    if not body_text and num_media > 0:
        reply_text = (
            "🛡️ *ScamShield AI*\n\n"
            "We received your media attachment. Please forward or paste the accompanying "
            "*text message, caption, or link* so our AI can perform a complete risk analysis."
        )
        twiml = TwilioService.generate_twiml_reply(reply_text)
        return Response(twiml, status=200, mimetype="text/xml")

    if not body_text:
        reply_text = (
            "🛡️ *ScamShield AI Active*\n\n"
            "Forward any suspicious message, news claim, or link to this bot to receive an immediate security risk analysis."
        )
        twiml = TwilioService.generate_twiml_reply(reply_text)
        return Response(twiml, status=200, mimetype="text/xml")

    # 3. Analyze Content via Risk Engine
    api_key = current_app.config.get("GOOGLE_FACT_CHECK_API_KEY", "")
    analysis = RiskEngine.evaluate(body_text, user_identifier=from_user, api_key=api_key)
    
    # 4. Generate WhatsApp formatted response
    reply_message = TwilioService.format_whatsapp_response(analysis)

    # 5. Persist Privacy-Preserving Audit Record
    user_hash = NLPPreprocessor.hash_identifier(from_user)
    masked_snippet = NLPPreprocessor.get_safe_snippet(body_text, max_chars=140)
    urls_detected = analysis.get("url_analysis", {}).get("detailed_results", [])

    try:
        record = ScanRecord(
            source="whatsapp_webhook",
            user_identifier_hash=user_hash,
            risk_score=analysis["estimated_risk_score"],
            risk_level=analysis["risk_band"],
            classification=analysis["classification"],
            category=analysis["category"],
            masked_content_snippet=masked_snippet,
            content_length=len(body_text),
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
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error persisting WhatsApp scan: {e}")

    # 6. Return TwiML response
    twiml_xml = TwilioService.generate_twiml_reply(reply_message)
    return Response(twiml_xml, status=200, mimetype="text/xml")

@webhook_bp.route("/simulate", methods=["POST"])
def simulate_whatsapp_interaction():
    """
    POST /api/webhook/simulate
    Provides a live WhatsApp sandbox simulator for the frontend dashboard
    without requiring external Twilio credentials.
    """
    data = request.get_json(silent=True) or {}
    message_text = data.get("message", "").strip()
    simulated_phone = data.get("sender_phone", "+919876543210")

    if not message_text:
        return jsonify({"error": "Message text is required"}), 400

    api_key = current_app.config.get("GOOGLE_FACT_CHECK_API_KEY", "")
    analysis = RiskEngine.evaluate(message_text, user_identifier=simulated_phone, api_key=api_key)
    bot_reply = TwilioService.format_whatsapp_response(analysis)

    # Persist record under source='whatsapp_simulator'
    user_hash = NLPPreprocessor.hash_identifier(simulated_phone)
    masked_snippet = NLPPreprocessor.get_safe_snippet(message_text, max_chars=140)
    urls_detected = analysis.get("url_analysis", {}).get("detailed_results", [])

    try:
        record = ScanRecord(
            source="whatsapp_simulator",
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
    except Exception as e:
        db.session.rollback()
        record_id = None

    return jsonify({
        "success": True,
        "scan_id": record_id,
        "user_message": message_text,
        "bot_reply": bot_reply,
        "analysis": analysis
    }), 200
