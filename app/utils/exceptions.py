"""Custom exceptions for the StadiumIQ application.

This module defines the base exception hierarchy used for handling failures
in input validation, Groq AI services, caching, and transportation lookups.
All application-specific exceptions subclass StadiumIQError so callers can
catch the entire hierarchy with a single except clause when needed.

Main exports:
    StadiumIQError, AIServiceError, ValidationError, CacheError,
    TransportationError

Typical usage example:
    from app.utils.exceptions import AIServiceError, ValidationError
    raise ValidationError("Message cannot be empty")
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


class TransportationError(StadiumIQError):
    """Exception raised when transportation data cannot be resolved.

    Raised by AIService or route handlers when a requested host city has no
    entry in TRANSPORT_INFO or when the transportation lookup fails
    unexpectedly.
    """
