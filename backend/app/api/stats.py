"""
ScamShield AI - Statistics & Analytics Blueprint
Aggregates telemetry, threat categories, risk distribution, and historical trends for the dashboard.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models.scan_record import ScanRecord
from datetime import datetime, timedelta, timezone

stats_bp = Blueprint("stats", __name__, url_prefix="/api")

@stats_bp.route("/stats", methods=["GET"])
def get_dashboard_stats():
    """
    GET /api/stats
    Returns aggregated metrics, category distributions, risk bands, and timeline data.
    """
    total_scans = db.session.query(func.count(ScanRecord.id)).scalar() or 0
    
    if total_scans == 0:
        # Return sensible empty state with baseline defaults
        return jsonify({
            "total_scans": 0,
            "high_risk_count": 0,
            "suspicious_count": 0,
            "caution_count": 0,
            "safe_count": 0,
            "average_risk_score": 0.0,
            "threat_neutralized_rate": 0.0,
            "risk_distribution": [
                {"name": "High Risk (75-100)", "value": 0, "color": "#ef4444"},
                {"name": "Suspicious (50-74)", "value": 0, "color": "#f97316"},
                {"name": "Caution (25-49)", "value": 0, "color": "#eab308"},
                {"name": "Likely Safe (0-24)", "value": 0, "color": "#10b981"}
            ],
            "category_breakdown": [],
            "source_distribution": [],
            "timeline": []
        }), 200

    high_risk_count = db.session.query(func.count(ScanRecord.id)).filter(ScanRecord.risk_level == "HIGH").scalar() or 0
    suspicious_count = db.session.query(func.count(ScanRecord.id)).filter(ScanRecord.risk_level == "SUSPICIOUS").scalar() or 0
    caution_count = db.session.query(func.count(ScanRecord.id)).filter(ScanRecord.risk_level == "CAUTION").scalar() or 0
    safe_count = db.session.query(func.count(ScanRecord.id)).filter(ScanRecord.risk_level == "LOW").scalar() or 0

    avg_score = db.session.query(func.avg(ScanRecord.risk_score)).scalar() or 0.0
    threat_rate = ((high_risk_count + suspicious_count) / total_scans * 100) if total_scans > 0 else 0.0

    # Category Breakdown
    cat_rows = (
        db.session.query(ScanRecord.category, func.count(ScanRecord.id))
        .group_by(ScanRecord.category)
        .order_by(func.count(ScanRecord.id).desc())
        .limit(8)
        .all()
    )
    category_breakdown = [{"category": row[0], "count": row[1]} for row in cat_rows]

    # Source Distribution
    source_rows = (
        db.session.query(ScanRecord.source, func.count(ScanRecord.id))
        .group_by(ScanRecord.source)
        .all()
    )
    source_distribution = [{"source": row[0], "count": row[1]} for row in source_rows]

    # Timeline (Recent scans chronologically)
    recent_records = (
        db.session.query(ScanRecord)
        .order_by(ScanRecord.created_at.desc())
        .limit(20)
        .all()
    )
    timeline = [
        {
            "id": r.id,
            "time": r.created_at.strftime("%H:%M:%S") if r.created_at else "",
            "risk_score": r.risk_score,
            "category": r.category
        }
        for r in reversed(recent_records)
    ]

    return jsonify({
        "total_scans": total_scans,
        "high_risk_count": high_risk_count,
        "suspicious_count": suspicious_count,
        "caution_count": caution_count,
        "safe_count": safe_count,
        "average_risk_score": round(float(avg_score), 1),
        "threat_neutralized_rate": round(threat_rate, 1),
        "risk_distribution": [
            {"name": "High Risk (75-100)", "value": high_risk_count, "color": "#ef4444"},
            {"name": "Suspicious (50-74)", "value": suspicious_count, "color": "#f97316"},
            {"name": "Caution (25-49)", "value": caution_count, "color": "#eab308"},
            {"name": "Likely Safe (0-24)", "value": safe_count, "color": "#10b981"}
        ],
        "category_breakdown": category_breakdown,
        "source_distribution": source_distribution,
        "timeline": timeline
    }), 200
