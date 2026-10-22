"""
ScamShield AI - DomainReputation Model
Maintains known suspicious, spoofed, shortener, and trusted domain reputation metadata.
"""

from datetime import datetime, timezone
from app.extensions import db

class DomainReputation(db.Model):
    __tablename__ = "domain_reputations"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False) # 'known_phishing', 'typosquat', 'shortener', 'trusted'
    is_suspicious = db.Column(db.Boolean, default=False, index=True)
    reputation_score = db.Column(db.Integer, default=0) # -100 (malicious) to +100 (trusted)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_verified = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "category": self.category,
            "is_suspicious": self.is_suspicious,
            "reputation_score": self.reputation_score,
            "last_verified": self.last_verified.isoformat() if self.last_verified else None,
            "notes": self.notes
        }
