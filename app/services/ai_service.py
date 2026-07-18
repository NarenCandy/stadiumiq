"""Groq AI Service for StadiumIQ.

This module handles interactions with the Groq API, selecting the system
prompts for the active persona, maintaining context history, and generating
completions.

Typical usage example:
    config = AppConfig()
    service = AIService(config)
    response = service.generate_response("Hello", "Fan", "English", [])
"""

from typing import Dict, List
from groq import Groq

from app.config import AppConfig
from app.constants import PERSONA_PROMPTS
from app.utils.exceptions import AIServiceError


class AIService:
    """Service class encapsulating Groq API interactions."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the AI Service.

        Args:
            config: The configuration object containing API keys and model parameters.

        Raises:
            AIServiceError: If the Groq API key is not configured.
        """
        self.config: AppConfig = config
        if not self.config.is_configured:
            raise AIServiceError("Groq API key is not configured.")

        # Initialize the Groq client
        try:
            self.client: Groq = Groq(api_key=self.config.GROQ_API_KEY)
        except Exception as e:
            raise AIServiceError(f"Failed to initialize Groq client: {e}") from e

    def generate_response(
        self,
        message: str,
        persona: str,
        language: str,
        history: List[Dict[str, str]],
    ) -> str:
        """Generate a response using the Groq chat completion API.

        Args:
            message: The current user message.
            persona: The target persona (e.g. Fan, Staff).
            language: The target response language.
            history: Previous conversation messages.

        Returns:
            The generated response string from the Groq API.

        Raises:
            AIServiceError: If the Groq client API call fails.
        """
        try:
            # Retrieve the appropriate system prompt or default to Fan
            system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["Fan"])
            system_prompt += f" Always respond in {language}."

            messages = [{"role": "system", "content": system_prompt}]

            # Load the last 10 messages for context window stability
            for msg in history[-10:]:
                messages.append(
                    {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                )

            messages.append({"role": "user", "content": message})

            # Create the chat completion request
            response = self.client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=messages,  # type: ignore
                max_tokens=1000,
                temperature=0.7,
            )

            # Extract the generated content
            content = response.choices[0].message.content
            if not content:
                raise AIServiceError("Empty response received from Groq API.")

            return str(content)

        except Exception as e:
            raise AIServiceError(f"Groq API completion failure: {e}") from e
