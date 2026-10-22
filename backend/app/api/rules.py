"""
ScamShield AI - Rules & Model Telemetry Blueprint
Exposes detection rule weights, pattern definitions, and ML evaluation metrics for transparency.
"""

import os
import json
from flask import Blueprint, jsonify
from app.services.scam_detector import ScamDetector

rules_bp = Blueprint("rules", __name__, url_prefix="/api/rules")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METRICS_PATH = os.path.join(BASE_DIR, "data", "models", "model_metrics.json")

@rules_bp.route("", methods=["GET"])
def get_rules_and_metrics():
    """
    GET /api/rules
    Returns active scam categories, detection thresholds, and AI/ML model performance metrics.
    """
    patterns = ScamDetector.load_patterns()
    
    # Load model evaluation metrics
    metrics_data = {}
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            metrics_data = {}

    return jsonify({
        "status": "active",
        "rules_engine": {
            "categories": patterns.get("categories", {}),
            "url_rules": patterns.get("url_rules", {}),
            "risk_bands": {
                "LOW": {"range": "0-24", "label": "Low Risk / Likely Safe"},
                "CAUTION": {"range": "25-49", "label": "Caution Advised"},
                "SUSPICIOUS": {"range": "50-74", "label": "Suspicious / Possible Scam"},
                "HIGH": {"range": "75-100", "label": "High Risk / Confirmed Scam"}
            }
        },
        "model_metrics": metrics_data
    }), 200
