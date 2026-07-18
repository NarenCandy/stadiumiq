"""Main entry point for the StadiumIQ application.

This module initializes the Flask app using the app factory and exposes it
for WSGI servers like gunicorn.

Typical usage example:
    $ python app.py
"""

import os
from flask import Flask
from app import create_app

app: Flask = create_app()

if __name__ == "__main__":
    # Retrieve port from environment, defaulting to 5000 for local runs
    port: int = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
