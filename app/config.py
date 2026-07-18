"""Configuration settings for StadiumIQ.

This module contains the AppConfig class which parses environment variables,
defines default values, and validates configuration parameters.

Typical usage example:
    config = AppConfig()
    if config.is_configured:
        print("Configured successfully!")
"""

from dataclasses import dataclass, field
import os
from typing import List


@dataclass
class AppConfig:
    """Application configuration with validation.

    Attributes:
        GROQ_API_KEY: API key for Groq service.
        MODEL_NAME: Groq model to use for inference.
        MAX_MESSAGE_LENGTH: Maximum allowed message length.
        CACHE_SIZE: Capacity of the LRU cache for chat responses.
        SUPPORTED_LANGUAGES: List of supported language names.
        SUPPORTED_PERSONAS: List of supported user personas.
    """

    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    MAX_MESSAGE_LENGTH: int = 2000
    CACHE_SIZE: int = 128
    SUPPORTED_LANGUAGES: List[str] = field(
        default_factory=lambda: [
            "English",
            "Spanish",
            "French",
            "Arabic",
            "Portuguese",
            "German",
            "Japanese",
            "Hindi",
        ]
    )
    SUPPORTED_PERSONAS: List[str] = field(
        default_factory=lambda: ["Fan", "Staff", "Volunteer", "Accessibility"]
    )

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If configurations constraints are violated.
        """
        if self.MAX_MESSAGE_LENGTH <= 0:
            raise ValueError("MAX_MESSAGE_LENGTH must be positive")
        if not self.MODEL_NAME:
            raise ValueError("MODEL_NAME cannot be empty")
        if self.CACHE_SIZE <= 0:
            raise ValueError("CACHE_SIZE must be positive")

    @property
    def is_configured(self) -> bool:
        """Check if app is properly configured with API key.

        Returns:
            Boolean status indicating if GROQ_API_KEY is present.
        """
        return bool(self.GROQ_API_KEY)
