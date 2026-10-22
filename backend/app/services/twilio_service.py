"""
ScamShield AI - Twilio WhatsApp Service
Handles Twilio webhook signature validation, WhatsApp markdown formatting,
and TwiML / REST client response delivery.
"""

import os
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

class TwilioService:
    @staticmethod
    def validate_request(request, auth_token: str, verify_enabled: bool = True) -> bool:
        """
        Validates the X-Twilio-Signature header on incoming webhooks to prevent spoofing.
        Can be bypassed during local testing / ngrok sandbox development.
        """
        if not verify_enabled or not auth_token:
            return True

        validator = RequestValidator(auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        url = request.url
        post_vars = request.form.to_dict()

        return validator.validate(url, post_vars, signature)

    @staticmethod
    def format_whatsapp_response(analysis: dict) -> str:
        """
        Formats risk evaluation into a concise, professional WhatsApp message.
        Follows standard cybersecurity incident reporting style.
        """
        score = int(analysis.get("estimated_risk_score", 0))
        risk_band = analysis.get("risk_band", "LOW")
        category = analysis.get("category", "Uncategorized")
        warnings = analysis.get("warning_signs", [])[:4]
        advice = analysis.get("safety_advice", [])[:3]
        confidence = analysis.get("confidence_level", "Medium")

        # Select risk badge
        if risk_band == "HIGH":
            risk_header = "⚠️ Risk Level: HIGH"
        elif risk_band == "SUSPICIOUS":
            risk_header = "⚠️ Risk Level: SUSPICIOUS"
        elif risk_band == "CAUTION":
            risk_header = "🟡 Risk Level: CAUTION"
        else:
            risk_header = "🟢 Risk Level: LOW (LIKELY SAFE)"

        warning_bullets = "\n".join(f"• {w}" for w in warnings)
        advice_bullets = "\n".join(f"• {a}" for a in advice)

        # Check for URL findings
        url_analysis = analysis.get("url_analysis", {})
        url_section = ""
        if url_analysis.get("has_urls"):
            highest_url = url_analysis.get("highest_risk_score", 0)
            url_verdict = url_analysis.get("overall_verdict", "URL Checked")
            url_section = f"\n🔗 Link Security: {url_verdict} (Risk: {int(highest_url)}/100)\n"

        message = (
            f"🛡️ *ScamShield AI Analysis*\n\n"
            f"{risk_header}\n\n"
            f"📊 *Estimated Risk Score:* {score}/100\n\n"
            f"🔎 *Category:* {category}\n"
            f"{url_section}\n"
            f"🚩 *Warning Signs:*\n{warning_bullets}\n\n"
            f"✅ *Safety Advice:*\n{advice_bullets}\n\n"
            f"ℹ️ *Confidence:* {confidence}\n"
            f"_{analysis.get('disclaimer')}_"
        )

        return message

    @staticmethod
    def generate_twiml_reply(reply_text: str) -> str:
        """Returns standard TwiML XML string to respond synchronously to Twilio webhooks."""
        resp = MessagingResponse()
        resp.message(reply_text)
        return str(resp)

    @staticmethod
    def send_direct_message(to_whatsapp_number: str, text: str, account_sid: str, auth_token: str, from_number: str) -> bool:
        """Sends an outbound WhatsApp message via Twilio REST API."""
        if not account_sid or not auth_token:
            return False
        try:
            client = Client(account_sid, auth_token)
            # Ensure numbers have 'whatsapp:' prefix
            if not to_whatsapp_number.startswith("whatsapp:"):
                to_whatsapp_number = f"whatsapp:{to_whatsapp_number}"
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"

            client.messages.create(
                body=text,
                from_=from_number,
                to=to_whatsapp_number
            )
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send outbound Twilio message: {e}")
            return False
