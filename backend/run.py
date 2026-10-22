"""
ScamShield AI - Application Entrypoint
Runs the Flask application factory.
"""

import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    print(f"[*] Starting ScamShield AI Backend on http://127.0.0.1:{port} (Debug: {debug})")
    app.run(host="127.0.0.1", port=port, debug=debug)
