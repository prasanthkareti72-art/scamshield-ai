"""
ScamShield AI - Vercel Serverless Entrypoint
Exports Flask WSGI app to Vercel's Python runtime.
"""

import os
import sys

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set production environment flag for Vercel
os.environ["FLASK_ENV"] = "production"
os.environ["VERCEL"] = "1"

from app import create_app

app = create_app("production")

# Vercel WSGI entrypoint
# app variable is exported
