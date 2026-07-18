"""Flask Application Factory for StadiumIQ.

This module initializes the Flask application, registers routes, sets up
rate limiting, adds security headers middleware, and defines global error
handlers.
"""

from typing import Any, Tuple
from flask import Flask, Response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import AppConfig
from app.utils.exceptions import StadiumIQError, ValidationError, AIServiceError

# Initialize global rate limiter
limiter: Limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day"],
    storage_uri="memory://",
)


def create_app(config_class: type[AppConfig] = AppConfig) -> Flask:
    """Create and configure a Flask application instance.

    Args:
        config_class: The configuration class to instantiate.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Load configuration
    config = config_class()
    app.config.from_object(config)
    app.config["APP_CONFIG"] = config

    # If in testing mode, disable rate limiting
    if app.config.get("TESTING"):
        limiter.enabled = False
    else:
        limiter.enabled = True

    # Initialize extensions
    limiter.init_app(app)

    # Security Headers Middleware
    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Add strict security headers to every HTTP response.

        Args:
            response: Outgoing Flask Response object.

        Returns:
            Flask Response object with security headers applied.
        """
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

        # Allow Three.js, GSAP, and Google Fonts CDNs in Content Security Policy
        csp_directives = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com "
            "https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "img-src 'self' data:; "
            "media-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp_directives
        return response

    # Register blueprint routes
    from app.routes.chat import chat_bp

    app.register_blueprint(chat_bp)

    # Global Error Handlers for custom exceptions
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> Tuple[Response, int]:
        """Handle custom ValidationError and return 400 JSON.

        Args:
            error: The raised ValidationError.

        Returns:
            JSON Response and status code.
        """
        response = jsonify({"error": str(error), "type": "ValidationError"})
        return response, 400

    @app.errorhandler(AIServiceError)
    def handle_ai_service_error(error: AIServiceError) -> Tuple[Response, int]:
        """Handle custom AIServiceError and return 502 JSON.

        Args:
            error: The raised AIServiceError.

        Returns:
            JSON Response and status code.
        """
        response = jsonify({"error": str(error), "type": "AIServiceError"})
        return response, 502

    @app.errorhandler(StadiumIQError)
    def handle_stadium_iq_error(error: StadiumIQError) -> Tuple[Response, int]:
        """Handle base custom StadiumIQError and return 500 JSON.

        Args:
            error: The raised StadiumIQError.

        Returns:
            JSON Response and status code.
        """
        response = jsonify({"error": str(error), "type": "StadiumIQError"})
        return response, 500

    @app.errorhandler(429)
    def ratelimit_handler(error: Any) -> Tuple[Response, int]:
        """Handle rate limit exceedances and return 429 JSON.

        Args:
            error: RateLimit exception details.

        Returns:
            JSON Response and status code.
        """
        response = jsonify(
            {
                "error": "Too many requests. Please try again later.",
                "type": "RateLimitError",
            }
        )
        return response, 429

    return app
