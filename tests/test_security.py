"""Security validation tests for the StadiumIQ application.

This module tests that all required security headers (CSP, HSTS, X-Frame-Options)
are correctly injected into outgoing responses, and validates input sanitization,
null byte rejection, and vulnerability management.

Typical usage example:
    $ python -m pytest tests/test_security.py
"""

import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import AppConfig


class TestSecurityHeaders(unittest.TestCase):
    """Verifies presence of security headers on all endpoints."""

    def setUp(self) -> None:
        """Initialize the application under test settings."""
        import os

        os.environ["GROQ_API_KEY"] = "test_key"

        class TestConfig(AppConfig):
            GROQ_API_KEY = "test_key"
            TESTING = True

        self.app: Flask = create_app(config_class=TestConfig)
        self.client: FlaskClient = self.app.test_client()

    def test_x_frame_options_header(self) -> None:
        """Test X-Frame-Options is DENY to prevent clickjacking."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")

    def test_x_content_type_options_header(self) -> None:
        """Test X-Content-Type-Options is nosniff to prevent MIME sniffing."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")

    def test_x_xss_protection_header(self) -> None:
        """Test X-XSS-Protection is enabled with block mode."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")

    def test_referrer_policy_header(self) -> None:
        """Test Referrer-Policy header is configured for privacy."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("Referrer-Policy"), "no-referrer-when-downgrade")

    def test_hsts_header(self) -> None:
        """Test HSTS is configured to enforce HTTPS connections."""
        response = self.client.get("/")
        self.assertEqual(
            response.headers.get("Strict-Transport-Security"), "max-age=31536000; includeSubDomains"
        )

    def test_content_security_policy_header(self) -> None:
        """Test CSP header exists and defines strict loading policies."""
        response = self.client.get("/")
        csp = response.headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("https://cdnjs.cloudflare.com", csp)
        self.assertIn("https://unpkg.com", csp)


class TestInputSanitization(unittest.TestCase):
    """Verifies script escaping and rejection of malicious inputs."""

    def setUp(self) -> None:
        """Initialize the application under test settings."""
        import os
        from app.routes.chat import response_cache

        os.environ["GROQ_API_KEY"] = "test_key"
        response_cache.clear()

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

    def tearDown(self) -> None:
        """Stop mock patchers after each test."""
        self.mock_groq_patcher.stop()

    @patch("app.routes.chat.AIService.generate_response")
    def test_html_tag_escaping(self, mock_generate: MagicMock) -> None:
        """Test that HTML tag inputs are escaped to prevent XSS markup injection."""
        mock_generate.return_value = "Mocked Response"
        self.client.post("/chat", json={"message": "<div>test</div>"})

        # Verify the message passed to generate_response is escaped
        mock_generate.assert_called_once()
        called_args = mock_generate.call_args[1]
        self.assertEqual(called_args["message"], "&lt;div&gt;test&lt;/div&gt;")

    def test_null_byte_rejection_chat(self) -> None:
        """Test that null bytes in chat message return 400."""
        response = self.client.post("/chat", json={"message": "abc\x00def"})
        self.assertEqual(response.status_code, 400)

    def test_rate_limiter_in_production(self) -> None:
        """Test that rate limiting is initialized when TESTING is False."""
        # Create an app explicitly in production mode (non-testing)
        import os

        os.environ["GROQ_API_KEY"] = "test_key"

        class ProdConfig(AppConfig):
            GROQ_API_KEY = "test_key"
            TESTING = False

        prod_app = create_app(config_class=ProdConfig)
        from app import limiter

        self.assertTrue(limiter.enabled)

    def test_input_max_length_strictly_enforced(self) -> None:
        """Test that a message matching max length limit (2000 chars) succeeds."""
        response = self.client.post("/chat", json={"message": "a" * 2000})
        # If API key test_key is invalid or mocked, we just check that it does not return 400 ValidationError
        self.assertNotEqual(response.status_code, 400)

    def test_input_over_max_length_rejected(self) -> None:
        """Test that message of 2001 chars returns 400 ValidationError."""
        response = self.client.post("/chat", json={"message": "a" * 2001})
        self.assertEqual(response.status_code, 400)
