"""Request and Response models for the StadiumIQ chat route.

This module provides data models for validating and mapping incoming JSON requests
and outgoing responses.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChatMessage:
    """Represents a single message in the chat history.

    Attributes:
        role: The sender of the message, either 'user' or 'assistant'.
        content: The text content of the message.
    """

    role: str
    content: str


@dataclass
class ChatRequest:
    """Represents the incoming request payload for the AI chat.

    Attributes:
        message: The user's query message.
        persona: The chosen persona (e.g. Fan, Staff, Volunteer, Accessibility).
        language: The target language for the response.
        history: The list of prior messages in the conversation session.
    """

    message: str
    persona: str
    language: str
    history: List[Dict[str, str]] = field(default_factory=list)

    def to_chat_messages(self) -> List[ChatMessage]:
        """Convert raw history dictionaries into a list of ChatMessage objects.

        Returns:
            A list of ChatMessage instances.
        """
        messages: List[ChatMessage] = []
        for msg in self.history:
            messages.append(
                ChatMessage(role=msg.get("role", "user"), content=msg.get("content", ""))
            )
        return messages


@dataclass
class ChatResponse:
    """Represents the outgoing response payload.

    Attributes:
        response: The generated assistant response string.
        persona: The active assistant persona.
        language: The active language.
    """

    response: str
    persona: str
    language: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the response object to a serializable dictionary.

        Returns:
            A dictionary containing response, persona, and language keys.
        """
        return {
            "response": self.response,
            "persona": self.persona,
            "language": self.language,
        }
