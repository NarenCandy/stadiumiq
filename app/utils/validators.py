"""Input validation utilities for the StadiumIQ application.

This module validates all incoming JSON data for the chat route, enforcing
security checks (null-byte rejection, HTML escaping), length limits, persona
and language validity, conversation history structure, and spam detection.

No I/O operations or external service calls are performed here; this module
operates entirely on in-memory data structures.

Main exports:
    validate_chat_request, detect_language

Typical usage example:
    from app.utils.validators import validate_chat_request
    chat_request = validate_chat_request(request.get_json(), config)
"""

import html
import logging
import re
from typing import Any, List

from app.config import AppConfig
from app.constants import (
    ERROR_EMPTY_MESSAGE,
    ERROR_HISTORY_FORMAT,
    ERROR_INVALID_LANGUAGE,
    ERROR_INVALID_PERSONA,
    ERROR_MESSAGE_TOO_LONG,
    ERROR_NULL_BYTES,
    ERROR_REPETITIVE_MESSAGE,
    SUPPORTED_LANGUAGES,
    SUPPORTED_PERSONAS,
)
from app.models.request_models import ChatRequest
from app.utils.exceptions import ValidationError

logger: logging.Logger = logging.getLogger(__name__)


def detect_language(message: str, supported_languages: List[str]) -> str:
    """Detect the most likely supported language from message content.

    Uses simple keyword matching to identify Spanish, French, Arabic,
    Portuguese, German, Japanese, and Hindi.  Defaults to English when no
    language-specific keywords are found.

    Args:
        message: The raw user message string to inspect.
        supported_languages: List of language names the application supports.

    Returns:
        A language name string drawn from ``supported_languages``.
    """
    normalized_message = message.lower()
    language_keywords = {
        "Spanish": ["hola", "gracias", "estadio", "transporte"],
        "French": ["bonjour", "merci", "stade", "transport"],
        "Arabic": ["مرحبا", "شكرا", "استاد", "مواصلات"],
        "Portuguese": ["obrigado", "estádio", "transporte", "casa"],
        "German": ["danke", "stadion", "verkehr", "train"],
        "Japanese": ["こんにちは", "ありがとう", "スタジアム", "交通"],
        "Hindi": ["नमस्ते", "धन्यवाद", "स्टेडियम", "यातायात"],
    }
    for language_name, keywords in language_keywords.items():
        if any(word in normalized_message for word in keywords):
            return language_name
    return "English"


def validate_chat_request(data: Any, config: AppConfig) -> ChatRequest:
    """Validate and normalise an incoming chat request payload.

    Performs the following checks in order:
    1. Verifies the payload is a dictionary.
    2. Extracts and type-checks ``message``, ``persona``, ``language``, and
       ``history`` fields.
    3. Rejects null bytes in any string field.
    4. Strips leading/trailing whitespace from string fields.
    5. Rejects empty or whitespace-only messages.
    6. Enforces ``MAX_MESSAGE_LENGTH``.
    7. Rejects highly repetitive (spam-like) messages.
    8. Validates ``persona`` against ``SUPPORTED_PERSONAS``.
    9. Auto-detects language when ``language`` is empty or ``"auto"``;
       rejects unsupported language strings.
    10. Validates ``history`` structure.
    11. HTML-escapes the message to prevent injection.

    Args:
        data: The raw parsed JSON payload from the HTTP request.
        config: The application configuration object.

    Returns:
        A fully validated and sanitised ChatRequest instance.

    Raises:
        ValidationError: If any field fails validation.
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    message: str = data.get("message", "")
    persona: str = data.get("persona", "Fan")
    language: str = data.get("language", "")
    history: Any = data.get("history", [])

    _check_message_type(message)
    _check_null_bytes(message=message, persona=persona, language=language)

    message = message.strip()
    persona = persona.strip() if isinstance(persona, str) else persona
    language = language.strip() if isinstance(language, str) else language

    _check_message_length(message=message, config=config)
    _check_persona(persona)
    language = _resolve_language(language=language, message=message)
    _check_history(history)

    sanitized_message = html.escape(message)
    return ChatRequest(
        message=sanitized_message,
        persona=persona,
        language=language,
        history=history,
    )


# ---------------------------------------------------------------------------
# Private helper functions — each validates exactly one concern
# ---------------------------------------------------------------------------


def _check_message_type(message: Any) -> None:
    """Verify that the message field is a string.

    Args:
        message: The raw value from the JSON payload.

    Raises:
        ValidationError: If message is not a string.
    """
    if not isinstance(message, str):
        raise ValidationError("Message must be a string.")


def _check_null_bytes(message: str, persona: str, language: str) -> None:
    """Reject any string field that contains null bytes.

    Args:
        message: The message string to inspect.
        persona: The persona string to inspect.
        language: The language string to inspect.

    Raises:
        ValidationError: If any of the three fields contain a null byte.
    """
    for field_value in (message, persona, language):
        if isinstance(field_value, str) and "\x00" in field_value:
            logger.warning("Null byte detected in request field")
            raise ValidationError(ERROR_NULL_BYTES)


def _check_message_length(message: str, config: AppConfig) -> None:
    """Reject empty messages and messages that exceed the configured length limit.

    Args:
        message: The stripped message string.
        config: Application configuration providing MAX_MESSAGE_LENGTH.

    Raises:
        ValidationError: If the message is empty, whitespace-only, repetitive,
            or exceeds the maximum allowed length.
    """
    if not message:
        raise ValidationError(ERROR_EMPTY_MESSAGE)
    if len(message) > config.MAX_MESSAGE_LENGTH:
        raise ValidationError(ERROR_MESSAGE_TOO_LONG)
    if _is_repetitive(message):
        logger.warning("Repetitive content detected in message")
        raise ValidationError(ERROR_REPETITIVE_MESSAGE)


def _check_persona(persona: Any) -> None:
    """Verify that the persona is one of the four supported values.

    Args:
        persona: The persona value from the request payload.

    Raises:
        ValidationError: If the persona is not a recognised string.
    """
    if not isinstance(persona, str) or persona not in SUPPORTED_PERSONAS:
        logger.warning("Invalid persona requested", extra={"persona": persona})
        raise ValidationError(ERROR_INVALID_PERSONA)


def _resolve_language(language: str, message: str) -> str:
    """Return a supported language name, auto-detecting when necessary.

    Args:
        language: The language string from the request (may be empty or "auto").
        message: The user message used for auto-detection when language is unset.

    Returns:
        A language name string that appears in SUPPORTED_LANGUAGES.

    Raises:
        ValidationError: If language is a non-empty, non-"auto" string that is
            not in SUPPORTED_LANGUAGES.
    """
    if not isinstance(language, str):
        raise ValidationError("Language must be a string.")
    if not language or language.lower() == "auto":
        return detect_language(message, SUPPORTED_LANGUAGES)
    if language not in SUPPORTED_LANGUAGES:
        logger.warning("Unsupported language requested", extra={"language": language})
        raise ValidationError(ERROR_INVALID_LANGUAGE)
    return language


def _check_history(history: Any) -> None:
    """Validate the structure of the conversation history list.

    Args:
        history: The raw history value from the request payload.

    Raises:
        ValidationError: If history is not a list, or if any item is malformed.
    """
    if not isinstance(history, list):
        raise ValidationError(ERROR_HISTORY_FORMAT)
    _validate_history_items(history)


def _validate_history_items(history: List[Any]) -> None:
    """Validate each individual item in the history list.

    Args:
        history: A list of purported conversation history dictionaries.

    Raises:
        ValidationError: If any item is not a dict, missing required keys, has
            incorrect value types, or contains null bytes.
    """
    for index, item in enumerate(history):
        if not isinstance(item, dict):
            raise ValidationError(
                f"History message at index {index} must be a dictionary."
            )
        if "role" not in item or "content" not in item:
            raise ValidationError(
                f"History message at index {index} must contain 'role' and 'content'."
            )
        if not isinstance(item["role"], str) or not isinstance(item["content"], str):
            raise ValidationError(
                f"History message at index {index} 'role' and 'content' must be strings."
            )
        if "\x00" in item["role"] or "\x00" in item["content"]:
            raise ValidationError(ERROR_NULL_BYTES)


def _is_repetitive(message: str) -> bool:
    """Detect highly repetitive content indicative of spam or noise.

    A message is considered repetitive when it contains repeated patterns
    or phrases that make it look like spam. This implementation uses:
    1. Single word repetition (e.g., "hello hello hello")
    2. Repeated short sequences (e.g., "gate A gate A gate A")
    3. Character-level repetition (e.g., "aaaaa")
    4. Balanced detection with thresholds optimized for short messages

    Args:
        message: The stripped message string to analyse.

    Returns:
        True if the message is deemed repetitive, False otherwise.
    """
    # Remove extra whitespace and normalize case
    normalized = ' '.join(message.lower().split())
    
    # Too short to analyze meaningfully
    if len(normalized) < 10:
        return False
    
    words = normalized.split()
    
    # Check 1: Single word repetition (all words identical)
    if len(words) >= 3 and len(set(words)) == 1:
        return True
    
    # Check 2: Character-level repetition (e.g., "aaaaaa")
    if len(normalized) >= 6:
        unique_chars = set(normalized.replace(' ', ''))
        if len(unique_chars) == 1:
            return True
    
    # Check 3: Word frequency dominance
    if len(words) >= 4:
        word_counts: dict[str, int] = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If most frequent word appears > 50% of the time
        max_count = max(word_counts.values())
        if max_count / len(words) > 0.5:
            return True
    
    # Check 4: Pattern repetition detection using sliding window
    # Look for repeated sequences of 2-3 words
    if len(words) >= 6:
        for window_size in range(2, 4):
            if window_size * 2 > len(words):
                continue
            
            windows = []
            for i in range(len(words) - window_size + 1):
                window = ' '.join(words[i:i + window_size])
                windows.append(window)
            
            # Check if any window appears multiple times
            window_counts: dict[str, int] = {}
            for window in windows:
                window_counts[window] = window_counts.get(window, 0) + 1
            
            max_window_count = max(window_counts.values()) if window_counts else 0
            # If a window appears at least twice and covers significant portion
            if max_window_count >= 2 and max_window_count * window_size / len(words) > 0.5:
                return True
    
    return False
