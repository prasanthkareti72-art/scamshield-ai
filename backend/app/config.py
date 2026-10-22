"""
ScamShield AI - Application Configuration
Supports Development, Testing, and Production configurations with privacy defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "scamshield-secure-session-key-prod")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
    VERIFY_TWILIO_SIGNATURE = os.getenv("VERIFY_TWILIO_SIGNATURE", "False").lower() in ("true", "1", "t")

    # Fact-Checking Configuration
    GOOGLE_FACT_CHECK_API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
    USE_MOCK_FACT_CHECK_DB = os.getenv("USE_MOCK_FACT_CHECK_DB", "True").lower() in ("true", "1", "t")

    # Privacy by Design Settings
    HASH_PHONE_NUMBERS = os.getenv("HASH_PHONE_NUMBERS", "True").lower() in ("true", "1", "t")
    MASK_SENSITIVE_TEXT = os.getenv("MASK_SENSITIVE_TEXT", "True").lower() in ("true", "1", "t")
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR / 'instance' / 'scamshield.sqlite'}"
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    VERIFY_TWILIO_SIGNATURE = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///scamshield.sqlite")
    VERIFY_TWILIO_SIGNATURE = True

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
