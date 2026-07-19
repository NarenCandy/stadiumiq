"""Configuration settings for StadiumIQ.

This module contains the AppConfig dataclass which reads environment variables,
applies sensible defaults, and validates all configuration parameters at
startup.  All list-typed config values are imported from app.constants so
there is a single source of truth.

Main exports:
    AppConfig

Typical usage example:
    config = AppConfig()
    if config.is_configured:
        print("Groq API key present — ready to serve requests.")
"""

import os
from dataclasses import dataclass, field
from typing import List

from app.constants import (
    CACHE_SIZE,
    DEFAULT_MODEL,
    MAX_MESSAGE_LENGTH,
    SUPPORTED_LANGUAGES,
    SUPPORTED_PERSONAS,
)


@dataclass
class AppConfig:
    """Application configuration with environment-variable sourcing and validation.

    All values are read from environment variables with safe defaults.
    Validation is performed in ``__post_init__`` so misconfigured deployments
    fail fast at startup rather than at runtime.

    Attributes:
        GROQ_API_KEY: API key for the Groq inference service.
        MODEL_NAME: Groq model identifier used for chat completions.
        MAX_MESSAGE_LENGTH: Maximum number of characters accepted per message.
        CACHE_SIZE: Maximum number of entries stored in the LRU response cache.
        SUPPORTED_LANGUAGES: Ordered list of language names accepted by the API.
        SUPPORTED_PERSONAS: Ordered list of persona names accepted by the API.
    """

    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    MODEL_NAME: str = DEFAULT_MODEL
    MAX_MESSAGE_LENGTH: int = MAX_MESSAGE_LENGTH
    CACHE_SIZE: int = CACHE_SIZE
    SUPPORTED_LANGUAGES: List[str] = field(default_factory=lambda: list(SUPPORTED_LANGUAGES))
    SUPPORTED_PERSONAS: List[str] = field(default_factory=lambda: list(SUPPORTED_PERSONAS))

    def __post_init__(self) -> None:
        """Validate configuration after initialisation.

        Raises:
            ValueError: If MAX_MESSAGE_LENGTH is not a positive integer.
            ValueError: If MODEL_NAME is empty.
            ValueError: If CACHE_SIZE is not a positive integer.
        """
        if self.MAX_MESSAGE_LENGTH <= 0:
            raise ValueError("MAX_MESSAGE_LENGTH must be positive")
        if not self.MODEL_NAME:
            raise ValueError("MODEL_NAME cannot be empty")
        if self.CACHE_SIZE <= 0:
            raise ValueError("CACHE_SIZE must be positive")

    @property
    def is_configured(self) -> bool:
        """Check whether the application is configured with a Groq API key.

        Returns:
            True if GROQ_API_KEY is a non-empty string, False otherwise.
        """
        return bool(self.GROQ_API_KEY)
