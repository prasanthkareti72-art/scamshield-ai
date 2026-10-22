"""
ScamShield AI - Application Factory
Initializes Flask application, registers blueprints, database extensions, and security middleware.
"""

import os
import logging
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, cors

import tempfile

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    instance_path = os.path.abspath(tempfile.gettempdir()) if os.getenv("VERCEL") else None
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # Initialize Extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    from app.api.analyze import analyze_bp
    from app.api.webhook import webhook_bp
    from app.api.stats import stats_bp
    from app.api.history import history_bp
    from app.api.rules import rules_bp

    app.register_blueprint(analyze_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(rules_bp)

    # Root Health Check
    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "ScamShield AI",
            "version": "1.0.0",
            "environment": config_name
        }), 200

    # Serve Built Frontend in Standalone Mode
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    if os.path.exists(frontend_dist):
        from flask import send_from_directory

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            if path.startswith("api") or path.startswith("health"):
                return jsonify({"error": "Endpoint not found", "status_code": 404}), 404
            target_file = os.path.join(frontend_dist, path)
            if path and os.path.exists(target_file):
                return send_from_directory(frontend_dist, path)
            return send_from_directory(frontend_dist, "index.html")

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        app.logger.error(f"Internal Server Error: {e}")
        return jsonify({"error": "Internal server error occurred", "status_code": 500}), 500

    # Database table initialization & optional seeding
    with app.app_context():
        db.create_all()
        seed_initial_demo_records(app)

    return app

def seed_initial_demo_records(app):
    """Seeds a few baseline anonymized demo scans if database is fresh."""
    from app.models.scan_record import ScanRecord
    from app.services.risk_engine import RiskEngine
    from app.services.nlp_preprocessor import NLPPreprocessor

    try:
        count = ScanRecord.query.count()
        if count == 0:
            app.logger.info("Database empty: seeding demo security telemetry records...")
            demo_messages = [
                {
                    "text": "Congratulations! You won ₹50,000 cash prize in Kaun Banega Crorepati WhatsApp Lucky Draw! Click http://kbc-lucky-winner.xyz/claim immediately and forward to 10 contacts to claim.",
                    "source": "whatsapp_webhook",
                    "user": "+919876500001"
                },
                {
                    "text": "Dear customer, your SBI account KYC has expired. Your netbanking access will be blocked tonight at 9:30 PM. Update now at http://sbi-kyc-portal-update.top to avoid deactivation.",
                    "source": "whatsapp_webhook",
                    "user": "+919876500002"
                },
                {
                    "text": "BREAKING: NASA confirmed Earth will be in 6 days of total darkness starting next week due to unprecedented solar storm! Forward to save lives!",
                    "source": "whatsapp_webhook",
                    "user": "+919876500003"
                },
                {
                    "text": "Work from home part-time: Earn ₹4,000 daily by liking YouTube videos and rating hotels on Google Maps. No experience needed. Join Telegram: t.me/daily_task_vip",
                    "source": "web_dashboard",
                    "user": "+919876500004"
                },
                {
                    "text": "Hey team, the monthly project review meeting is rescheduled to Thursday 3:00 PM in Conference Room B. See the agenda on the shared drive.",
                    "source": "web_dashboard",
                    "user": "+919876500005"
                }
            ]

            for item in demo_messages:
                analysis = RiskEngine.evaluate(item["text"])
                urls_detected = analysis.get("url_analysis", {}).get("detailed_results", [])
                user_hash = NLPPreprocessor.hash_identifier(item["user"])
                masked = NLPPreprocessor.get_safe_snippet(item["text"])
                rec = ScanRecord(
                    source=item["source"],
                    user_identifier_hash=user_hash,
                    risk_score=analysis["estimated_risk_score"],
                    risk_level=analysis["risk_band"],
                    classification=analysis["classification"],
                    category=analysis["category"],
                    masked_content_snippet=masked,
                    content_length=len(item["text"]),
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
                db.session.add(rec)
            db.session.commit()
            app.logger.info("Successfully seeded 5 initial demo records.")
    except Exception as e:
        db.session.rollback()
        app.logger.warning(f"Demo seeding skipped: {e}")
