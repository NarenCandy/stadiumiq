"""Custom exception hierarchy for the StadiumIQ application.

This module defines a structured exception hierarchy rooted at
StadiumIQError. All application-specific exceptions inherit from this base
class, enabling callers to catch all domain errors with a single except clause
while still distinguishing the error type.

Exception hierarchy:
    StadiumIQError (base)
    ├── AIServiceError    — Groq API failures
    ├── ValidationError   — Input validation failures
    ├── CacheError        — LRU cache operation failures
    ├── ConfigurationError — Application configuration issues
    └── TransportationError — Transportation data lookup failures

Example:
    try:
        response = ai_service.generate_response(message, persona)
    except AIServiceError as error:
        logger.error("AI service failed: %s", error)
        raise
"""


class StadiumIQError(Exception):
    """Base exception class for all StadiumIQ application errors.

    All project-specific exceptions must subclass this class so that a single
    ``except StadiumIQError`` clause can catch the entire hierarchy when
    required by error handlers.
    """


class AIServiceError(StadiumIQError):
    """Exception raised when interactions with the Groq API fail.

    Raised by AIService when the Groq client cannot be initialised, when
    all retry attempts are exhausted, or when the API returns an empty or
    invalid response.
    """


class ValidationError(StadiumIQError):
    """Exception raised when incoming request input fails validation.

    Raised by the validator utilities when a field value violates length
    limits, contains forbidden characters, references an unsupported persona
    or language, or exhibits spam-like repetition.
    """


class CacheError(StadiumIQError):
    """Exception raised during LRU cache access or mutation failures.

    Raised by LRUCache when an unexpected error occurs during get, set, or
    clear operations.
    """


class ConfigurationError(StadiumIQError):
    """Raised when application configuration is invalid or incomplete.

    Example:
        if not config.GROQ_API_KEY:
            raise ConfigurationError("GROQ_API_KEY is required")
    """


class TransportationError(StadiumIQError):
    """Exception raised when transportation data cannot be resolved.

    Raised by AIService or route handlers when a requested host city has no
    entry in TRANSPORT_INFO or when the transportation lookup fails
    unexpectedly.
    """
