"""Custom exceptions for the StadiumIQ application.

This module defines the base exceptions used for handling failures
in input validation, Groq AI services, and caching.
"""


class StadiumIQError(Exception):
    """Base exception class for all StadiumIQ errors."""

    pass


class AIServiceError(StadiumIQError):
    """Exception raised when calls to the Groq API fail."""

    pass


class ValidationError(StadiumIQError):
    """Exception raised when incoming request input fails validation."""

    pass


class CacheError(StadiumIQError):
    """Exception raised during cache access or mutation failures."""

    pass
