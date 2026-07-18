"""Main test suite for the StadiumIQ application.

This module contains unit tests verifying Flask routing, AI chat functionality,
persona switching, language compatibility, conversation history context, error
handling, health checks, and response structures.

Typical usage example:
    $ python -m pytest tests/test_app.py
"""

import json
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import AppConfig


class StadiumIQTestBase(unittest.TestCase):
    """Base setup class for StadiumIQ tests.

    Sets up a Flask test client with rate limiting disabled.
    """

    def setUp(self) -> None:
        """Initialize the Flask application in testing mode."""
        import os
        from app.routes.chat import response_cache

        # Set environment variable so AppConfig is configured
        os.environ["GROQ_API_KEY"] = "test_key"
        response_cache.clear()

        self.config = AppConfig()

        # Instantiate test app
        class TestConfig(AppConfig):
            GROQ_API_KEY = "test_key"
            TESTING = True

        self.app: Flask = create_app(config_class=TestConfig)
        self.client: FlaskClient = self.app.test_client()

        # Mock the Groq client in services
        self.mock_groq_patcher = patch("app.services.ai_service.Groq")
        self.mock_groq_class = self.mock_groq_patcher.start()

        self.mock_client_instance = MagicMock()
        self.mock_groq_class.return_value = self.mock_client_instance

        # Setup standard mock completion response
        self.mock_completion = MagicMock()
        self.mock_message = MagicMock()
        self.mock_message.content = "Mocked AI Response"
        self.mock_completion.choices = [MagicMock(message=self.mock_message)]
        self.mock_client_instance.chat.completions.create.return_value = self.mock_completion

    def tearDown(self) -> None:
        """Stop mock patchers after each test."""
        self.mock_groq_patcher.stop()


class TestIndexRoute(StadiumIQTestBase):
    """Verifies that the root index route works as expected."""

    def test_index_status_code(self) -> None:
        """Test that root route returns 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_content_type(self) -> None:
        """Test that root route returns HTML."""
        response = self.client.get("/")
        self.assertIn("text/html", response.content_type)

    def test_index_contains_app_title(self) -> None:
        """Test that index page contains StadiumIQ title."""
        response = self.client.get("/")
        self.assertIn(b"StadiumIQ", response.data)

    def test_index_contains_skip_link(self) -> None:
        """Test that index page contains skip-navigation link."""
        response = self.client.get("/")
        self.assertIn(b"skip-link", response.data)


class TestChatRouteBasic(StadiumIQTestBase):
    """Verifies basic post actions on /chat."""

    def test_chat_success(self) -> None:
        """Test that valid chat request yields 200 and mocked answer."""
        response = self.client.post(
            "/chat",
            json={"message": "hello", "persona": "Fan", "language": "English", "history": []},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["response"], "Mocked AI Response")
        self.assertFalse(data["cached"])

    def test_chat_empty_json(self) -> None:
        """Test that empty json body results in ValidationError (400)."""
        response = self.client.post("/chat", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("ValidationError", response.get_json()["type"])

    def test_chat_missing_message(self) -> None:
        """Test that payload without message key returns 400."""
        response = self.client.post(
            "/chat", json={"persona": "Fan", "language": "English", "history": []}
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_cache_works(self) -> None:
        """Test that identical query is cached and returned from LRU cache."""
        payload = {
            "message": "Where is the exit?",
            "persona": "Fan",
            "language": "English",
            "history": [],
        }
        # First call: Uncached
        resp1 = self.client.post("/chat", json=payload)
        self.assertEqual(resp1.status_code, 200)
        self.assertFalse(resp1.get_json()["cached"])

        # Second call: Cached
        resp2 = self.client.post("/chat", json=payload)
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.get_json()["cached"])
        self.assertEqual(resp2.get_json()["response"], "Mocked AI Response")

    def test_chat_non_json_payload(self) -> None:
        """Test that raw text payload triggers a 400 ValidationError."""
        response = self.client.post("/chat", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)

    def test_chat_invalid_types_message(self) -> None:
        """Test that message of non-string type returns 400."""
        response = self.client.post(
            "/chat", json={"message": 1234, "persona": "Fan", "language": "English"}
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_whitespace_only(self) -> None:
        """Test that message with only spaces fails validation."""
        response = self.client.post(
            "/chat", json={"message": "   ", "persona": "Fan", "language": "English"}
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_large_input(self) -> None:
        """Test that message exceeding length constraints is blocked."""
        long_msg = "a" * 2001
        response = self.client.post(
            "/chat", json={"message": long_msg, "persona": "Fan", "language": "English"}
        )
        self.assertEqual(response.status_code, 400)


class TestChatRoutePersona(StadiumIQTestBase):
    """Validates persona switching behaviour."""

    def test_persona_fan(self) -> None:
        """Verify chat with Fan persona."""
        response = self.client.post(
            "/chat", json={"message": "Hello", "persona": "Fan", "language": "English"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["persona"], "Fan")

    def test_persona_staff(self) -> None:
        """Verify chat with Staff persona."""
        response = self.client.post(
            "/chat",
            json={"message": "Report crowd block", "persona": "Staff", "language": "English"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["persona"], "Staff")

    def test_persona_volunteer(self) -> None:
        """Verify chat with Volunteer persona."""
        response = self.client.post(
            "/chat",
            json={"message": "What is my shift?", "persona": "Volunteer", "language": "English"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["persona"], "Volunteer")

    def test_persona_accessibility(self) -> None:
        """Verify chat with Accessibility persona."""
        response = self.client.post(
            "/chat",
            json={
                "message": "Where is the wheelchair elevator?",
                "persona": "Accessibility",
                "language": "English",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["persona"], "Accessibility")

    def test_persona_invalid(self) -> None:
        """Verify that unsupported personas return 400."""
        response = self.client.post(
            "/chat", json={"message": "Hello", "persona": "InvalidPersona", "language": "English"}
        )
        self.assertEqual(response.status_code, 400)


class TestChatRouteLanguage(StadiumIQTestBase):
    """Validates multi-language support (all 8 languages)."""

    def test_lang_english(self) -> None:
        """Verify English works."""
        response = self.client.post("/chat", json={"message": "Hello", "language": "English"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "English")

    def test_lang_spanish(self) -> None:
        """Verify Spanish works."""
        response = self.client.post("/chat", json={"message": "Hola", "language": "Spanish"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Spanish")

    def test_lang_french(self) -> None:
        """Verify French works."""
        response = self.client.post("/chat", json={"message": "Bonjour", "language": "French"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "French")

    def test_lang_arabic(self) -> None:
        """Verify Arabic works."""
        response = self.client.post("/chat", json={"message": "Marhaban", "language": "Arabic"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Arabic")

    def test_lang_portuguese(self) -> None:
        """Verify Portuguese works."""
        response = self.client.post("/chat", json={"message": "Ola", "language": "Portuguese"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Portuguese")

    def test_lang_german(self) -> None:
        """Verify German works."""
        response = self.client.post("/chat", json={"message": "Hallo", "language": "German"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "German")

    def test_lang_japanese(self) -> None:
        """Verify Japanese works."""
        response = self.client.post("/chat", json={"message": "Konnichiwa", "language": "Japanese"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Japanese")

    def test_lang_hindi(self) -> None:
        """Verify Hindi works."""
        response = self.client.post("/chat", json={"message": "Namaste", "language": "Hindi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Hindi")

    def test_lang_invalid(self) -> None:
        """Verify unsupported languages trigger a 400 error."""
        response = self.client.post("/chat", json={"message": "Hello", "language": "Italian"})
        self.assertEqual(response.status_code, 400)

    def test_lang_auto_detect_missing_language(self) -> None:
        """Verify that missing language input falls back to auto-detection."""
        response = self.client.post("/chat", json={"message": "Hola"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "Spanish")

    def test_lang_auto_detect_auto_keyword(self) -> None:
        """Verify that auto detection works when language is explicitly set to auto."""
        response = self.client.post("/chat", json={"message": "Bonjour", "language": "auto"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["language"], "French")


class TestChatRouteHistory(StadiumIQTestBase):
    """Verifies that conversation history is formatted and handled."""

    def test_history_structure_valid(self) -> None:
        """Test with valid message history format."""
        history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
        response = self.client.post(
            "/chat",
            json={
                "message": "how are you?",
                "persona": "Fan",
                "language": "English",
                "history": history,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_history_not_list(self) -> None:
        """Test history of type dict returns 400."""
        response = self.client.post("/chat", json={"message": "hi", "history": "not a list"})
        self.assertEqual(response.status_code, 400)

    def test_history_invalid_item_format(self) -> None:
        """Test history list with string element returns 400."""
        response = self.client.post("/chat", json={"message": "hi", "history": ["invalid item"]})
        self.assertEqual(response.status_code, 400)

    def test_history_missing_fields(self) -> None:
        """Test history list missing role key returns 400."""
        response = self.client.post(
            "/chat", json={"message": "hi", "history": [{"content": "missing role"}]}
        )
        self.assertEqual(response.status_code, 400)

    def test_history_invalid_value_types(self) -> None:
        """Test history list with int content value returns 400."""
        response = self.client.post(
            "/chat", json={"message": "hi", "history": [{"role": "user", "content": 123}]}
        )
        self.assertEqual(response.status_code, 400)

    def test_history_null_bytes(self) -> None:
        """Test history list containing null bytes returns 400."""
        response = self.client.post(
            "/chat",
            json={"message": "hi", "history": [{"role": "user", "content": "null\x00byte"}]},
        )
        self.assertEqual(response.status_code, 400)


class TestChatEdgeCases(StadiumIQTestBase):
    """Verifies edge cases like injection payloads, null-bytes, etc."""

    def test_null_byte_in_message(self) -> None:
        """Verify that null bytes inside message trigger validation error."""
        response = self.client.post("/chat", json={"message": "hello\x00world"})
        self.assertEqual(response.status_code, 400)

    def test_null_byte_in_persona(self) -> None:
        """Verify that null bytes inside persona trigger validation error."""
        response = self.client.post("/chat", json={"message": "hello", "persona": "Fan\x00"})
        self.assertEqual(response.status_code, 400)

    def test_null_byte_in_language(self) -> None:
        """Verify that null bytes inside language trigger validation error."""
        response = self.client.post("/chat", json={"message": "hello", "language": "English\x00"})
        self.assertEqual(response.status_code, 400)

    def test_html_injection_sanitized(self) -> None:
        """Verify that HTML input is properly escaped to prevent injection."""
        payload = {
            "message": "<script>alert('xss')</script>",
            "persona": "Fan",
            "language": "English",
        }
        # Trigger uncached flow
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)

        # Retrieve arguments of client.chat.completions.create
        called_args = self.mock_client_instance.chat.completions.create.call_args[1]
        sent_messages = called_args["messages"]
        user_message_content = sent_messages[-1]["content"]

        self.assertNotIn("<script>", user_message_content)
        self.assertIn("&lt;script&gt;", user_message_content)

    def test_very_long_input(self) -> None:
        """Verify that extreme inputs (e.g. 10000 characters) are blocked."""
        response = self.client.post("/chat", json={"message": "x" * 10000})
        self.assertEqual(response.status_code, 400)

    def test_empty_string_message(self) -> None:
        """Verify that empty message string returns 400."""
        response = self.client.post("/chat", json={"message": ""})
        self.assertEqual(response.status_code, 400)

    def test_special_characters_message(self) -> None:
        """Verify that message with special characters passes validation."""
        response = self.client.post("/chat", json={"message": "!@#$%^&*()_+{}|:<>?`~-=[]\\;',./"})
        self.assertEqual(response.status_code, 200)

    def test_only_newline_message(self) -> None:
        """Verify that a message with only newlines fails validation."""
        response = self.client.post("/chat", json={"message": "\n\n\n"})
        self.assertEqual(response.status_code, 400)

    def test_unicode_message(self) -> None:
        """Verify that emoji/unicode characters are successfully handled."""
        response = self.client.post("/chat", json={"message": "⚽ FIFA 2026! 🗺️"})
        self.assertEqual(response.status_code, 200)

    def test_unicode_language(self) -> None:
        """Verify that unicode strings matching supported languages work."""
        response = self.client.post("/chat", json={"message": "Namaste", "language": "Hindi"})
        self.assertEqual(response.status_code, 200)


class TestErrorHandling(StadiumIQTestBase):
    """Verifies backend custom exception middleware responses."""

    def test_groq_api_failure(self) -> None:
        """Verify that Groq SDK exception returns 502 AIServiceError."""
        self.mock_client_instance.chat.completions.create.side_effect = Exception("API Key Expired")

        response = self.client.post("/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 502)

        data = response.get_json()
        self.assertEqual(data["type"], "AIServiceError")
        self.assertIn("API Key Expired", data["error"])

    def test_unconfigured_api_key(self) -> None:
        """Verify that empty API key returns 502 AIServiceError."""
        import os

        old_val = os.environ.get("GROQ_API_KEY")
        if "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
        try:
            app = create_app()
            client = app.test_client()
            response = client.post("/chat", json={"message": "hello"})
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.get_json()["type"], "AIServiceError")
        finally:
            if old_val is not None:
                os.environ["GROQ_API_KEY"] = old_val

    def test_generic_stadium_iq_error(self) -> None:
        """Verify custom StadiumIQError triggers a 500 JSON response."""
        with patch("app.routes.chat.AIService.generate_response") as mock_gen:
            from app.utils.exceptions import StadiumIQError

            mock_gen.side_effect = StadiumIQError("Custom generic failure")

            response = self.client.post("/chat", json={"message": "hello"})
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json()["type"], "StadiumIQError")

    def test_invalid_cache_size(self) -> None:
        """Verify that negative CACHE_SIZE inside AppConfig triggers ValueError."""
        with self.assertRaises(ValueError):
            AppConfig(CACHE_SIZE=-1)

    def test_empty_model_name(self) -> None:
        """Verify that empty MODEL_NAME inside AppConfig triggers ValueError."""
        with self.assertRaises(ValueError):
            AppConfig(MODEL_NAME="")


class TestHealthRoute(StadiumIQTestBase):
    """Verifies monitoring health route status."""

    def test_health_status(self) -> None:
        """Test health check returns 200 OK."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_health_json_keys(self) -> None:
        """Test health check JSON payload has the required fields."""
        response = self.client.get("/health")
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("model", data)
        self.assertIn("groq_configured", data)
        self.assertIn("timestamp", data)
        self.assertIn("services", data)

    def test_health_groq_connected(self) -> None:
        """Test health shows connected if API key is configured."""
        response = self.client.get("/health")
        data = response.get_json()
        self.assertTrue(data["groq_configured"])
        self.assertEqual(data["services"]["groq_api"], "connected")

    def test_health_groq_disconnected(self) -> None:
        """Test health shows unavailable if API key is empty."""
        import os

        old_val = os.environ.get("GROQ_API_KEY")
        if "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
        try:
            app = create_app()
            client = app.test_client()
            response = client.get("/health")
            data = response.get_json()
            self.assertFalse(data["groq_configured"])
            self.assertEqual(data["services"]["groq_api"], "unavailable")
        finally:
            if old_val is not None:
                os.environ["GROQ_API_KEY"] = old_val

    def test_health_content_type(self) -> None:
        """Test health check content type is application/json."""
        response = self.client.get("/health")
        self.assertEqual(response.content_type, "application/json")

    def test_health_contains_version(self) -> None:
        """Test health contains current app version."""
        response = self.client.get("/health")
        data = response.get_json()
        self.assertEqual(data["version"], "1.0.0")


class TestResponseFormat(StadiumIQTestBase):
    """Verifies JSON format structures returned from chat routes."""

    def test_chat_response_format_keys(self) -> None:
        """Test chat response contains all correct keys."""
        response = self.client.post("/chat", json={"message": "test format"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("response", data)
        self.assertIn("persona", data)
        self.assertIn("language", data)
        self.assertIn("cached", data)

    def test_chat_response_types(self) -> None:
        """Test that returned fields have correct types."""
        response = self.client.post("/chat", json={"message": "test types"})
        data = response.get_json()
        self.assertIsInstance(data["response"], str)
        self.assertIsInstance(data["persona"], str)
        self.assertIsInstance(data["language"], str)
        self.assertIsInstance(data["cached"], bool)

    def test_chat_response_fallback_default(self) -> None:
        """Test that omitted persona/language keys fallback to defaults."""
        response = self.client.post("/chat", json={"message": "defaults"})
        data = response.get_json()
        self.assertEqual(data["persona"], "Fan")
        self.assertEqual(data["language"], "English")

    def test_chat_response_header_prevent_caching(self) -> None:
        """Test that chat response header doesn't allow browser caching."""
        response = self.client.post("/chat", json={"message": "test headers"})
        # We don't want the browser to cache POST results
        self.assertIn("no-store", response.headers.get("Cache-Control", ""))

    def test_chat_response_headers_csp_present(self) -> None:
        """Test that response carries security middleware CSP headers."""
        response = self.client.post("/chat", json={"message": "test headers"})
        self.assertIn("Content-Security-Policy", response.headers)
