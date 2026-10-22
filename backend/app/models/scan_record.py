"""
ScamShield AI - ScanRecord Model
Stores privacy-preserving analysis audit history without persisting plaintext PII.
"""

import json
import uuid
from datetime import datetime, timezone
from app.extensions import db

class ScanRecord(db.Model):
    __tablename__ = "scan_records"

    id = db.Column(db.Integer, primary_key=True)
    scan_uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Anonymized user identifier (SHA-256 hash, zero raw phone numbers or PII)
    user_identifier_hash = db.Column(db.String(64), nullable=True, index=True)
    source = db.Column(db.String(32), default="web_dashboard", index=True)  # 'whatsapp', 'web_dashboard', 'api'
    
    # Risk Metrics
    risk_score = db.Column(db.Float, nullable=False, index=True)  # 0 to 100
    risk_level = db.Column(db.String(20), nullable=False, index=True)  # 'LOW', 'CAUTION', 'SUSPICIOUS', 'HIGH'
    classification = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)
    
    # Content Metadata (Masked & Redacted)
    masked_content_snippet = db.Column(db.String(255), nullable=True)
    content_length = db.Column(db.Integer, default=0)
    has_url = db.Column(db.Boolean, default=False)
    
    # Evidence & Indicators (stored as serialized JSON strings for SQLite & Postgres compatibility)
    urls_detected_json = db.Column(db.Text, default="[]")
    detected_indicators_json = db.Column(db.Text, default="[]")
    advice_list_json = db.Column(db.Text, default="[]")
    
    # Diagnostic component scores
    url_risk_score = db.Column(db.Float, default=0.0)
    ml_fake_news_prob = db.Column(db.Float, default=0.0)
    ml_scam_prob = db.Column(db.Float, default=0.0)
    fact_check_matched = db.Column(db.Boolean, default=False)
    fact_check_source = db.Column(db.String(100), nullable=True)
    
    confidence_level = db.Column(db.String(20), default="Medium")
    explanation_summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="completed")

    @property
    def urls_detected(self):
        try:
            return json.loads(self.urls_detected_json or "[]")
        except Exception:
            return []

    @urls_detected.setter
    def urls_detected(self, value):
        self.urls_detected_json = json.dumps(value or [])

    @property
    def detected_indicators(self):
        try:
            return json.loads(self.detected_indicators_json or "[]")
        except Exception:
            return []

    @detected_indicators.setter
    def detected_indicators(self, value):
        self.detected_indicators_json = json.dumps(value or [])

    @property
    def advice_list(self):
        try:
            return json.loads(self.advice_list_json or "[]")
        except Exception:
            return []

    @advice_list.setter
    def advice_list(self, value):
        self.advice_list_json = json.dumps(value or [])

    def to_dict(self):
        return {
            "id": self.id,
            "scan_uuid": self.scan_uuid,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "user_identifier_hash": self.user_identifier_hash[:8] + "..." if self.user_identifier_hash else "Anonymous",
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
            "classification": self.classification,
            "category": self.category,
            "masked_content_snippet": self.masked_content_snippet,
            "content_length": self.content_length,
            "has_url": self.has_url,
            "urls_detected": self.urls_detected,
            "detected_indicators": self.detected_indicators,
            "advice_list": self.advice_list,
            "url_risk_score": round(self.url_risk_score, 1),
            "ml_fake_news_prob": round(self.ml_fake_news_prob, 2),
            "ml_scam_prob": round(self.ml_scam_prob, 2),
            "fact_check_matched": self.fact_check_matched,
            "fact_check_source": self.fact_check_source,
            "confidence_level": self.confidence_level,
            "explanation_summary": self.explanation_summary,
            "status": self.status
        }
