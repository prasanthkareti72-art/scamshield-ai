"""
ScamShield AI - Models Package Init
"""

from app.models.scan_record import ScanRecord
from app.models.domain_reputation import DomainReputation
from app.models.fact_check_item import FactCheckItem

__all__ = ["ScanRecord", "DomainReputation", "FactCheckItem"]
