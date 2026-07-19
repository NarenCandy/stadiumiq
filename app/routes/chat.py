"""Chat and health check endpoint handlers for StadiumIQ.

This module defines the Flask Blueprint and route handler functions for the
AI chat interface and the service health check endpoint.  All business logic,
validation, and AI service calls are delegated to their respective modules;
this module contains only HTTP request/response handling.

Main exports:
    chat_bp, response_cache

Typical usage example:
    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp)
"""

import logging
import time
from typing import Tuple
from uuid import uuid4

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from app import limiter
from app.constants import CACHE_SIZE, HTTP_OK
from app.services.ai_service import AIService
from app.utils.cache import LRUCache
from app.utils.validators import validate_chat_request

logger: logging.Logger = logging.getLogger(__name__)

chat_bp: Blueprint = Blueprint("chat", __name__)
response_cache: LRUCache = LRUCache(max_size=CACHE_SIZE)

_APP_VERSION: str = "1.0.0"


@chat_bp.route("/")
def index() -> str:
    """Render the main index page.

    Returns:
        The rendered HTML content of templates/index.html.
    """
    return render_template("index.html")


@chat_bp.route("/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat() -> Tuple[Response, int]:
    """Handle an incoming AI chat request.

    Validates input, checks the LRU cache, invokes the AI service on a cache
    miss, stores the result, and returns a JSON response.

    Returns:
        A tuple of (JSON Response, HTTP status code).

    Raises:
        ValidationError: Propagated to the global error handler on bad input.
        AIServiceError: Propagated to the global error handler on API failure.
    """
    config = current_app.config["APP_CONFIG"]
    raw_payload = request.get_json(silent=True) or {}
    chat_request = validate_chat_request(raw_payload, config)
    session_id = _generate_session_id()

    logger.debug(
        "Chat request received",
        extra={
            "persona": chat_request.persona,
            "language": chat_request.language,
            "session_id": session_id,
        },
    )

    cached_response = _get_cached_response(chat_request)
    if cached_response is not None:
        logger.debug(
            "Serving response from cache",
            extra={"persona": chat_request.persona, "language": chat_request.language},
        )
        return _build_response(
            response_text=cached_response,
            persona=chat_request.persona,
            language=chat_request.language,
            is_cached=True,
            session_id=session_id,
        )

    ai_response = _invoke_ai_service(chat_request, config)
    _store_in_cache(chat_request, ai_response)

    return _build_response(
        response_text=ai_response,
        persona=chat_request.persona,
        language=chat_request.language,
        is_cached=False,
        session_id=session_id,
    )


@chat_bp.route("/health", methods=["GET"])
def health() -> Tuple[Response, int]:
    """Return the current service health status.

    Returns:
        A tuple of (JSON Response with health fields, HTTP status code).
    """
    config = current_app.config["APP_CONFIG"]
    groq_status = "connected" if config.is_configured else "unavailable"
    return (
        jsonify(
            {
                "status": "ok",
                "model": config.MODEL_NAME,
                "groq_configured": config.is_configured,
                "version": _APP_VERSION,
                "timestamp": time.time(),
                "services": {"groq_api": groq_status},
            }
        ),
        HTTP_OK,
    )


# ---------------------------------------------------------------------------
# Private helpers — each does exactly one thing
# ---------------------------------------------------------------------------


def _generate_session_id() -> str:
    """Generate a unique session identifier for the current request.

    Returns:
        A UUID4 string suitable for use as a session identifier.
    """
    return str(uuid4())


def _build_cache_key(chat_request: object) -> str:
    """Construct a deterministic LRU cache key from request fields.

    Args:
        chat_request: A ChatRequest instance with persona, language, and
            message attributes.

    Returns:
        A colon-delimited cache key string.
    """
    return (
        f"{chat_request.persona}:{chat_request.language}:"  # type: ignore[attr-defined]
        f"{chat_request.message.lower()}"  # type: ignore[attr-defined]
    )


def _get_cached_response(chat_request: object) -> object:
    """Look up a cached response for the given request.

    Args:
        chat_request: A ChatRequest instance.

    Returns:
        The cached response string if present, otherwise None.
    """
    cache_key = _build_cache_key(chat_request)
    return response_cache.get(cache_key)


def _invoke_ai_service(chat_request: object, config: object) -> str:
    """Instantiate AIService and generate a response for the request.

    Args:
        chat_request: A validated ChatRequest instance.
        config: The AppConfig instance.

    Returns:
        The generated response string.
    """
    service = AIService(config)  # type: ignore[arg-type]
    return service.generate_response(
        message=chat_request.message,  # type: ignore[attr-defined]
        persona=chat_request.persona,  # type: ignore[attr-defined]
        language=chat_request.language,  # type: ignore[attr-defined]
        history=chat_request.history,  # type: ignore[attr-defined]
    )


def _store_in_cache(chat_request: object, response_text: str) -> None:
    """Store a generated response in the LRU cache.

    Args:
        chat_request: A ChatRequest instance used to build the cache key.
        response_text: The response string to cache.
    """
    cache_key = _build_cache_key(chat_request)
    response_cache.set(cache_key, response_text)


def _build_response(
    response_text: str,
    persona: str,
    language: str,
    is_cached: bool,
    session_id: str,
) -> Tuple[Response, int]:
    """Serialise a chat response into a Flask JSON tuple.

    Args:
        response_text: The AI-generated or cached response string.
        persona: The active persona name.
        language: The active language name.
        is_cached: Whether the response was served from the LRU cache.
        session_id: The unique session identifier for this request.

    Returns:
        A tuple of (JSON Response, HTTP_OK status code).
    """
    return (
        jsonify(
            {
                "response": response_text,
                "persona": persona,
                "language": language,
                "cached": is_cached,
                "session_id": session_id,
            }
        ),
        HTTP_OK,
    )
