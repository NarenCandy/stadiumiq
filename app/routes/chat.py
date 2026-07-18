"""Chat and health endpoints route module for StadiumIQ.

This module defines the blueprint and handler functions for the AI chat interface
and service health check monitoring.
"""

import time
from typing import Tuple
from flask import Blueprint, Response, current_app, jsonify, render_template, request

from app import limiter
from app.services.ai_service import AIService
from app.utils.cache import LRUCache
from app.utils.validators import validate_chat_request

# Initialize Flask Blueprint
chat_bp: Blueprint = Blueprint("chat", __name__)

# Global cache for AI responses
response_cache: LRUCache = LRUCache(max_size=128)


@chat_bp.route("/")
def index() -> str:
    """Render the main index page.

    Returns:
        The rendered templates/index.html content.
    """
    return render_template("index.html")


@chat_bp.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat() -> Tuple[Response, int]:
    """Process incoming chat messages, generate responses, and manage caching.

    Returns:
        A tuple of JSON response containing the generated answer, and HTTP status code.
    """
    config = current_app.config["APP_CONFIG"]

    # 1. Parse and validate JSON input
    raw_data = request.get_json(silent=True) or {}
    chat_req = validate_chat_request(raw_data, config)

    # 2. Check LRU Cache
    cache_key = f"{chat_req.persona}:{chat_req.language}:{chat_req.message.lower()}"
    cached_response = response_cache.get(cache_key)

    if cached_response is not None:
        return (
            jsonify(
                {
                    "response": cached_response,
                    "persona": chat_req.persona,
                    "language": chat_req.language,
                    "cached": True,
                }
            ),
            200,
        )

    # 3. Invoke Groq AI Service
    ai_service = AIService(config)
    ai_response = ai_service.generate_response(
        message=chat_req.message,
        persona=chat_req.persona,
        language=chat_req.language,
        history=chat_req.history,
    )

    # 4. Save to Cache
    response_cache.set(cache_key, ai_response)

    return (
        jsonify(
            {
                "response": ai_response,
                "persona": chat_req.persona,
                "language": chat_req.language,
                "cached": False,
            }
        ),
        200,
    )


@chat_bp.route("/health", methods=["GET"])
def health() -> Tuple[Response, int]:
    """Health check endpoint for monitoring.

    Returns:
        A tuple containing the JSON service status and the HTTP status code.
    """
    config = current_app.config["APP_CONFIG"]
    return (
        jsonify(
            {
                "status": "ok",
                "model": config.MODEL_NAME,
                "groq_configured": config.is_configured,
                "version": "1.0.0",
                "timestamp": time.time(),
                "services": {"groq_api": "connected" if config.is_configured else "unavailable"},
            }
        ),
        200,
    )
