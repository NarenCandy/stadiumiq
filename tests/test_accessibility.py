"""Accessibility compliance tests for StadiumIQ.

This module parses the index.html template dynamically to verify accessibility compliance
rules such as lang attributes, skip links, semantic layout regions, role logs, and ARIA
expandable labels.

Typical usage example:
    $ python -m pytest tests/test_accessibility.py
"""

import unittest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import AppConfig


class TestHTMLAccessibility(unittest.TestCase):
    """Verifies compliance with WCAG 2.1 accessibility criteria."""

    def setUp(self) -> None:
        """Initialize the application in testing mode."""
        import os

        os.environ["GROQ_API_KEY"] = "test_key"

        class TestConfig(AppConfig):
            GROQ_API_KEY = "test_key"
            TESTING = True

        self.app: Flask = create_app(config_class=TestConfig)
        self.client: FlaskClient = self.app.test_client()
        # Retrieve the index page content once
        response = self.client.get("/")
        self.html: str = response.data.decode("utf-8")

    def test_lang_attribute_set(self) -> None:
        """WCAG 1.1: Ensure the lang attribute is declared on the html tag."""
        self.assertIn('<html lang="en">', self.html)

    def test_skip_link_present(self) -> None:
        """WCAG 2.4.1: Ensure skip navigation link is defined first in the body."""
        self.assertIn('class="skip-link"', self.html)
        self.assertIn('href="#main-content"', self.html)

    def test_semantic_landmarks_present(self) -> None:
        """Ensure core landmarks (header, aside, main, footer, nav) are defined."""
        self.assertIn("<header", self.html)
        self.assertIn("<aside", self.html)
        self.assertIn("<main", self.html)
        self.assertIn("<footer", self.html)
        self.assertIn("<nav", self.html)

    def test_aria_roles_and_labels(self) -> None:
        """Verify role attributes and aria-labels exist on landmarks."""
        self.assertIn('role="banner"', self.html)
        self.assertIn('role="complementary"', self.html)
        self.assertIn('role="main"', self.html)
        self.assertIn('role="contentinfo"', self.html)

    def test_chat_log_region(self) -> None:
        """Ensure chat output message container utilizes role='log' and live region."""
        self.assertIn('role="log"', self.html)
        self.assertIn('aria-live="polite"', self.html)

    def test_interactive_elements_labeled(self) -> None:
        """Verify aria-labeling on form controls and icon-only buttons."""
        self.assertIn('aria-label="Select Language"', self.html)
        self.assertIn('aria-label="Clear chat history"', self.html)
        self.assertIn('aria-label="Send message"', self.html)

    def test_viewport_meta_scalable(self) -> None:
        """Ensure zoom functionality is supported for visual impairments."""
        self.assertIn('name="viewport"', self.html)
        self.assertIn("width=device-width", self.html)
        # Verify we didn't disable user scaling (e.g. user-scalable=no)
        self.assertNotIn("user-scalable=no", self.html)
        self.assertNotIn("user-scalable=0", self.html)
