"""Request and response data models for the StadiumIQ chat route.

This module defines lightweight dataclasses used to carry validated request
data between the validation layer and the AI service layer.  No business logic
or I/O operations are performed here.

Main exports:
    ChatMessage, ChatRequest, ChatResponse

Typical usage example:
    request = ChatRequest(
        message="Where is Gate A?",
        persona="Fan",
        language="English",
        history=[],
    )
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChatMessage:
    """A single message in a conversation history turn.

    Attributes:
        role: The sender identifier — either ``"user"`` or ``"assistant"``.
        content: The text body of the message.
    """

    role: str
    content: str


@dataclass
class ChatRequest:
    """Validated incoming request payload for the AI chat endpoint.

    Attributes:
        message: The sanitised user query string.
        persona: The chosen persona name (Fan, Staff, Volunteer, Accessibility).
        language: The target response language name (e.g. "English").
        history: Ordered list of prior conversation turns as role/content dicts.
    """

    message: str
    persona: str
    language: str
    history: List[Dict[str, str]] = field(default_factory=list)

    def to_chat_messages(self) -> List[ChatMessage]:
        """Convert the raw history list into typed ChatMessage objects.

        Returns:
            A list of ChatMessage instances derived from the history field.
        """
        return [
            ChatMessage(
                role=turn.get("role", "user"),
                content=turn.get("content", ""),
            )
            for turn in self.history
        ]


@dataclass
class ChatResponse:
    """Outgoing response payload for the AI chat endpoint.

    Attributes:
        response: The generated assistant response string.
        persona: The persona that was active when the response was generated.
        language: The language in which the response was generated.
    """

    response: str
    persona: str
    language: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the response to a JSON-compatible dictionary.

        Returns:
            A dictionary with ``response``, ``persona``, and ``language`` keys.
        """
        return {
            "response": self.response,
            "persona": self.persona,
            "language": self.language,
        }
