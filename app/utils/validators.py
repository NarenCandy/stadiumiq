"""Input validation utilities for the StadiumIQ application.

This module validates incoming JSON data for the chat route, ensuring
security checks like null-byte rejection, length limits, XSS basic checks,
and persona/language validity are enforced.
"""

import html
from typing import Any, List
from app.config import AppConfig
from app.models.request_models import ChatRequest
from app.utils.exceptions import ValidationError


def detect_language(message: str, supported_languages: List[str]) -> str:
    """Detect the most likely supported language for a message.

    Args:
        message: The user input message.
        supported_languages: List of supported language names.

    Returns:
        The detected language name, or English as default.
    """
    normalized = message.lower()
    if any(word in normalized for word in ["hola", "gracias", "estadio", "transporte"]):
        return "Spanish"
    if any(word in normalized for word in ["bonjour", "merci", "stade", "transport"]):
        return "French"
    if any(word in normalized for word in ["مرحبا", "شكرا", "استاد", "مواصلات"]):
        return "Arabic"
    if any(word in normalized for word in ["obrigado", "estádio", "transporte", "casa"]):
        return "Portuguese"
    if any(word in normalized for word in ["danke", "stadion", "verkehr", "train"]):
        return "German"
    if any(word in normalized for word in ["こんにちは", "ありがとう", "スタジアム", "交通"]):
        return "Japanese"
    if any(word in normalized for word in ["नमस्ते", "धन्यवाद", "स्टेडियम", "यातायात"]):
        return "Hindi"
    return "English"


def validate_chat_request(data: Any, config: AppConfig) -> ChatRequest:
    """Validate incoming chat request payload.

    Args:
        data: The raw request JSON payload (typically a dictionary).
        config: The active application configuration instance.

    Returns:
        A validated ChatRequest data model.

    Raises:
        ValidationError: If any of the validation constraints fail.
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    # 1. Extract and clean fields
    message: str = data.get("message", "")
    persona: str = data.get("persona", "Fan")
    language: str = data.get("language", "")
    history = data.get("history", [])

    # Ensure message is a string
    if not isinstance(message, str):
        raise ValidationError("Message must be a string.")

    # Trim whitespace
    message = message.strip()

    # 2. Check for Null Bytes
    if "\x00" in message or "\x00" in persona or "\x00" in language:
        raise ValidationError("Null bytes are not allowed in inputs.")

    # 3. Check message length
    if not message:
        raise ValidationError("Message cannot be empty.")
    if len(message) > config.MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message exceeds maximum allowed length of "
            f"{config.MAX_MESSAGE_LENGTH} characters."
        )

    # 4. Check supported persona
    if persona not in config.SUPPORTED_PERSONAS:
        raise ValidationError(
            "Unsupported persona '{persona}'. Supported personas are: "
            f"{', '.join(config.SUPPORTED_PERSONAS)}"
        )

    # 5. Detect language automatically if none is provided or auto mode is requested
    if not isinstance(language, str):
        raise ValidationError("Language must be a string.")

    if not language.strip() or language.strip().lower() == "auto":
        language = detect_language(message, config.SUPPORTED_LANGUAGES)
    elif language not in config.SUPPORTED_LANGUAGES:
        raise ValidationError(
            "Unsupported language '{language}'. Supported languages are: "
            f"{', '.join(config.SUPPORTED_LANGUAGES)}"
        )

    # 6. Validate conversation history structure
    if not isinstance(history, list):
        raise ValidationError("History must be a list of messages.")

    for idx, msg in enumerate(history):
        if not isinstance(msg, dict):
            raise ValidationError(f"History message at index {idx} must be a dictionary.")
        if "role" not in msg or "content" not in msg:
            raise ValidationError(
                f"History message at index {idx} must contain 'role' and 'content'."
            )
        if not isinstance(msg["role"], str) or not isinstance(msg["content"], str):
            raise ValidationError(
                f"History message at index {idx} 'role' and 'content' must be strings."
            )
        if "\x00" in msg["role"] or "\x00" in msg["content"]:
            raise ValidationError("Null bytes are not allowed in history.")

    # Sanitization: Escape HTML tags to prevent simple XSS
    sanitized_message = html.escape(message)

    return ChatRequest(
        message=sanitized_message,
        persona=persona,
        language=language,
        history=history,
    )
