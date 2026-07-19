"""WSGI entry point for the StadiumIQ application.

This module creates the Flask application via the app factory and exposes it
as ``app`` for WSGI servers such as gunicorn or uWSGI.  When run directly it
starts a local development server on the port specified by the PORT environment
variable (defaulting to 5000).

Main exports:
    app

Typical usage example:
    $ gunicorn wsgi:app
    $ python wsgi.py
"""

import os

from flask import Flask

from app import create_app

app: Flask = create_app()

if __name__ == "__main__":
    port: int = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
