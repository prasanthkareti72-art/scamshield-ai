"""
ScamShield AI - FactCheckItem Model
Stores verified fact-checking records from reputable debunking organizations (PIB, AltNews, Snopes, BoomLive).
"""

from datetime import datetime, timezone
from app.extensions import db

class FactCheckItem(db.Model):
    __tablename__ = "fact_check_items"

    id = db.Column(db.Integer, primary_key=True)
    claim_text = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(255), index=True)
    verdict = db.Column(db.String(50), nullable=False) # 'FALSE', 'MISLEADING', 'ALTERED_IMAGE', 'SCAM'
    source_organization = db.Column(db.String(100), nullable=False) # 'PIB Fact Check', 'Snopes', 'BoomLive'
    source_url = db.Column(db.String(500), nullable=True)
    debunk_summary = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "claim_text": self.claim_text,
            "keywords": self.keywords,
            "verdict": self.verdict,
            "source_organization": self.source_organization,
            "source_url": self.source_url,
            "debunk_summary": self.debunk_summary,
            "published_date": self.published_date.isoformat() if self.published_date else None
        }
