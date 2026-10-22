"""
ScamShield AI - History Blueprint
Provides paginated, filterable audit logs of past scans without exposing raw PII.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.scan_record import ScanRecord

history_bp = Blueprint("history", __name__, url_prefix="/api/history")

@history_bp.route("", methods=["GET"])
def get_history():
    """
    GET /api/history
    Query parameters:
    - limit: int (default 30)
    - offset: int (default 0)
    - risk_level: str ('HIGH', 'SUSPICIOUS', 'CAUTION', 'LOW')
    - category: str
    - search: str (filters masked snippet)
    """
    limit = min(int(request.args.get("limit", 30)), 100)
    offset = int(request.args.get("offset", 0))
    risk_level = request.args.get("risk_level")
    category = request.args.get("category")
    search = request.args.get("search", "").strip()

    query = ScanRecord.query

    if risk_level:
        query = query.filter(ScanRecord.risk_level == risk_level.upper())
    if category:
        query = query.filter(ScanRecord.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(ScanRecord.masked_content_snippet.ilike(f"%{search}%"))

    total = query.count()
    records = query.order_by(ScanRecord.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        "total": total,
        "limit": limit,
        "offset": offset,
        "records": [r.to_dict() for r in records]
    }), 200

@history_bp.route("/<int:record_id>", methods=["GET"])
def get_single_record(record_id: int):
    """GET /api/history/<id> - Returns full audit details for a specific scan."""
    record = ScanRecord.query.get_or_404(record_id)
    return jsonify(record.to_dict()), 200

@history_bp.route("/clear", methods=["POST"])
def clear_history():
    """POST /api/history/clear - Dev helper to reset audit history."""
    try:
        deleted = db.session.query(ScanRecord).delete()
        db.session.commit()
        return jsonify({"success": True, "deleted_count": deleted}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
