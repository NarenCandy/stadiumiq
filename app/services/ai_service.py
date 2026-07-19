"""Groq AI service for StadiumIQ.

This module encapsulates all interactions with the Groq chat completion API.
It builds persona-specific system prompts from constants, assembles message
history, retries transient failures with exponential back-off, validates
generated responses, and logs every significant operation.

No Flask imports or HTTP handling appear here — all concerns are purely AI
service logic.

Main exports:
    AIService

Typical usage example:
    service = AIService(config)
    response = service.generate_response(
        message="Where is Gate A?",
        persona="Fan",
        language="English",
        history=[],
    )
"""

import logging
import time
from typing import Any, Dict, List, Optional

from groq import Groq

from app.config import AppConfig
from app.constants import (
    DEFAULT_MODEL,
    ERROR_NO_API_KEY,
    MAX_COMPLETION_TOKENS,
    MAX_HISTORY_LENGTH,
    MAX_MESSAGE_LENGTH,
    PERSONA_SYSTEM_PROMPTS,
    REQUEST_TIMEOUT_SECONDS,
)
from app.utils.exceptions import AIServiceError

logger: logging.Logger = logging.getLogger(__name__)

_MAX_RETRY_ATTEMPTS: int = 3
_RETRY_BASE_DELAY_SECONDS: float = 0.5
_COMPLETION_TEMPERATURE: float = 0.7


class AIService:
    """Encapsulate all Groq API interactions for the StadiumIQ assistant.

    Handles prompt construction, message history assembly, API calls with
    retry logic, response extraction, and response validation.

    Attributes:
        config: The application configuration object.
        client: The authenticated Groq SDK client instance.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialise the AI service and validate configuration.

        Args:
            config: Application configuration containing GROQ_API_KEY and
                MODEL_NAME.

        Raises:
            AIServiceError: If GROQ_API_KEY is absent or the Groq client
                cannot be constructed.
        """
        self.config: AppConfig = config
        if not self.config.is_configured:
            raise AIServiceError(ERROR_NO_API_KEY)
        self.client: Groq = self._create_groq_client()

    def _create_groq_client(self) -> Groq:
        """Construct and return an authenticated Groq client.

        Returns:
            An initialised Groq client instance.

        Raises:
            AIServiceError: If the Groq SDK raises any exception during
                construction.
        """
        try:
            return Groq(api_key=self.config.GROQ_API_KEY)
        except Exception as error:
            raise AIServiceError(
                f"Failed to initialise Groq client: {error}"
            ) from error

    def generate_response(
        self,
        message: str,
        persona: str,
        language: str,
        history: List[Dict[str, str]],
    ) -> str:
        """Generate an AI response for the given message and context.

        Orchestrates prompt construction, message assembly, API invocation,
        content extraction, and response validation as discrete steps.

        Args:
            message: The sanitised user message string.
            persona: The active persona name (e.g. "Fan", "Staff").
            language: The target language for the response (e.g. "English").
            history: List of prior conversation turns as dicts with "role"
                and "content" keys.

        Returns:
            The generated assistant response as a plain string.

        Raises:
            AIServiceError: If the Groq API call fails after all retries, or
                if the response is empty or oversized.
        """
        try:
            system_prompt = self._build_system_prompt(
                persona=persona, language=language
            )
            messages = self._build_messages(
                message=message,
                history=history,
                system_prompt=system_prompt,
            )
            completion = self._create_completion(messages=messages)
            content = self._extract_content(response=completion)
            self._validate_response(content=content)
            logger.debug(
                "Response generated successfully",
                extra={"persona": persona, "language": language},
            )
            return content
        except AIServiceError:
            raise
        except Exception as error:
            raise AIServiceError(
                f"Groq API completion failure: {error}"
            ) from error

    def _build_system_prompt(self, persona: str, language: str) -> str:
        """Construct the persona-specific system prompt for this request.

        Looks up the prompt from PERSONA_SYSTEM_PROMPTS and appends a
        language instruction.

        Args:
            persona: The active persona name.
            language: The target response language.

        Returns:
            A fully composed system prompt string.
        """
        base_prompt = PERSONA_SYSTEM_PROMPTS.get(
            persona, PERSONA_SYSTEM_PROMPTS["Fan"]
        )
        return f"{base_prompt} Always respond in {language}."

    def _build_messages(
        self,
        message: str,
        history: List[Dict[str, str]],
        system_prompt: str,
    ) -> List[Dict[str, str]]:
        """Assemble the full message list for the Groq completion request.

        Prepends the system prompt, appends the last MAX_HISTORY_LENGTH
        history turns, and appends the current user message.

        Args:
            message: The current user message.
            history: The conversation history list.
            system_prompt: The fully composed system prompt string.

        Returns:
            An ordered list of message dicts ready for the Groq API.
        """
        assembled: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        for turn in history[-MAX_HISTORY_LENGTH:]:
            assembled.append(
                {
                    "role": str(turn.get("role", "user")),
                    "content": str(turn.get("content", "")),
                }
            )
        assembled.append({"role": "user", "content": message})
        return assembled

    def _create_completion(
        self, messages: List[Dict[str, str]]
    ) -> Any:
        """Call the Groq chat completion endpoint with retry and back-off.

        Retries up to _MAX_RETRY_ATTEMPTS times on any exception.  Logs each
        attempt at INFO level and each failure at WARNING level.

        Args:
            messages: The assembled message list for the API payload.

        Returns:
            The raw Groq completion response object.

        Raises:
            AIServiceError: If all retry attempts are exhausted.
        """
        last_error: Optional[Exception] = None
        model_name = self.config.MODEL_NAME or DEFAULT_MODEL

        for attempt in range(_MAX_RETRY_ATTEMPTS):
            try:
                logger.info(
                    "Calling Groq completion API",
                    extra={"attempt": attempt + 1, "model": model_name},
                )
                return self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=MAX_COMPLETION_TOKENS,
                    temperature=_COMPLETION_TEMPERATURE,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except Exception as error:
                last_error = error
                logger.warning(
                    "Groq API attempt failed",
                    extra={
                        "attempt": attempt + 1,
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                    },
                )
                is_final_attempt = attempt == _MAX_RETRY_ATTEMPTS - 1
                if not is_final_attempt:
                    time.sleep(_RETRY_BASE_DELAY_SECONDS * (attempt + 1))

        raise AIServiceError(
            f"Groq API request failed after {_MAX_RETRY_ATTEMPTS} attempts: {last_error}"
        ) from last_error

    def _extract_content(self, response: Any) -> str:
        """Extract and normalise the text content from a Groq response object.

        Args:
            response: The raw completion response object returned by the Groq
                SDK.

        Returns:
            The stripped response content string.

        Raises:
            AIServiceError: If the response has no choices or the content is
                empty.
        """
        has_choices = hasattr(response, "choices") and bool(response.choices)
        if not has_choices:
            raise AIServiceError("Empty response received from Groq API.")

        response_message = response.choices[0].message
        content = getattr(response_message, "content", "")
        if not content:
            raise AIServiceError("Empty response received from Groq API.")
        return str(content).strip()

    def _validate_response(self, content: str) -> None:
        """Validate the generated response string before returning it.

        Args:
            content: The extracted response content string.

        Raises:
            AIServiceError: If the content is empty, whitespace-only, or
                exceeds MAX_MESSAGE_LENGTH.
        """
        is_empty = not content or content.isspace()
        if is_empty:
            raise AIServiceError("Generated response was empty.")
        if len(content) > MAX_MESSAGE_LENGTH:
            raise AIServiceError("Generated response exceeds allowed size.")
