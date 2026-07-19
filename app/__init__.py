"""Flask application factory for StadiumIQ.

This module creates and configures the Flask application instance, registers
the chat Blueprint, initialises rate limiting, attaches security-header
middleware, and registers global error handlers for all custom exception types.

Main exports:
    create_app, limiter

Typical usage example:
    from app import create_app
    app = create_app()
"""

import logging
from typing import Any, Tuple

from flask import Flask, Response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import AppConfig
from app.constants import (
    HTTP_BAD_GATEWAY,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_TOO_MANY_REQUESTS,
)
from app.utils.exceptions import AIServiceError, StadiumIQError, ValidationError

logger: logging.Logger = logging.getLogger(__name__)

limiter: Limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day"],
    storage_uri="memory://",
)


def create_app(config_class: type[AppConfig] = AppConfig) -> Flask:
    """Create and configure the Flask application instance.

    Registers the chat Blueprint, security headers, rate limiting, and global
    error handlers. Rate limiting is disabled automatically when the app is in
    TESTING mode.

    Args:
        config_class: Configuration class to use for app setup. Defaults to
            AppConfig.

    Returns:
        A fully configured Flask application instance with all blueprints,
        middleware, and extensions registered.

    Raises:
        ValueError: If configuration validation fails during setup.
    """
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    config = config_class()
    app.config.from_object(config)
    app.config["APP_CONFIG"] = config

    _configure_rate_limiter(app)
    limiter.init_app(app)

    _register_security_headers(app)
    _register_blueprint(app)
    _register_error_handlers(app)

    return app


def _configure_rate_limiter(app: Flask) -> None:
    """Enable or disable the rate limiter based on the TESTING flag.

    Args:
        app: The Flask application instance.
    """
    if app.config.get("TESTING"):
        limiter.enabled = False
    else:
        limiter.enabled = True


def _register_security_headers(app: Flask) -> None:
    """Attach an after_request hook that injects security headers.

    Args:
        app: The Flask application instance.
    """

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Inject strict security headers into every outgoing HTTP response.

        Args:
            response: The outgoing Flask Response object.

        Returns:
            The response with security headers applied.
        """
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Content-Security-Policy"] = _build_csp_header()
        return response


def _build_csp_header() -> str:
    """Build the Content-Security-Policy header value string.

    Returns:
        A CSP directive string allowing CDNs required by Three.js, GSAP,
        and Google Fonts.
    """
    return (
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


def _register_blueprint(app: Flask) -> None:
    """Import and register the chat Blueprint with the application.

    Args:
        app: The Flask application instance.
    """
    from app.routes.chat import chat_bp

    app.register_blueprint(chat_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register global JSON error handlers for all custom exception types.

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> Tuple[Response, int]:
        """Return a 400 JSON response for ValidationError exceptions.

        Args:
            error: The raised ValidationError instance.

        Returns:
            A tuple of (JSON Response, 400 status code).
        """
        logger.warning("Validation error: %s", str(error))
        return jsonify({"error": str(error), "type": "ValidationError"}), HTTP_BAD_REQUEST

    @app.errorhandler(AIServiceError)
    def handle_ai_service_error(error: AIServiceError) -> Tuple[Response, int]:
        """Return a 502 JSON response for AIServiceError exceptions.

        Args:
            error: The raised AIServiceError instance.

        Returns:
            A tuple of (JSON Response, 502 status code).
        """
        logger.error("AI service error: %s", str(error))
        return jsonify({"error": str(error), "type": "AIServiceError"}), HTTP_BAD_GATEWAY

    @app.errorhandler(StadiumIQError)
    def handle_stadium_iq_error(error: StadiumIQError) -> Tuple[Response, int]:
        """Return a 500 JSON response for base StadiumIQError exceptions.

        Args:
            error: The raised StadiumIQError instance.

        Returns:
            A tuple of (JSON Response, 500 status code).
        """
        logger.error("StadiumIQ error: %s", str(error))
        return (
            jsonify({"error": str(error), "type": "StadiumIQError"}),
            HTTP_INTERNAL_SERVER_ERROR,
        )

    @app.errorhandler(HTTP_TOO_MANY_REQUESTS)
    def handle_rate_limit(error: Any) -> Tuple[Response, int]:
        """Return a 429 JSON response when a rate limit is exceeded.

        Args:
            error: The rate-limit error detail object.

        Returns:
            A tuple of (JSON Response, 429 status code).
        """
        return (
            jsonify(
                {
                    "error": "Too many requests. Please try again later.",
                    "type": "RateLimitError",
                }
            ),
            HTTP_TOO_MANY_REQUESTS,
        )
