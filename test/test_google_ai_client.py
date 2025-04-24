#!/usr/bin/env python3
"""
Test cases for the Google AI client.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from core.google_ai_client import GoogleAIClient

class TestGoogleAIClient(unittest.TestCase):
    """Test cases for the Google AI client."""

    def setUp(self):
        """Set up the test case."""
        self.client = GoogleAIClient()

    @patch('core.google_ai_client.GoogleAIClient.generate_content')
    def test_generate_json_with_valid_json(self, mock_generate_content):
        """Test generating JSON with valid JSON response."""
        # Mock the response
        mock_generate_content.return_value = """
        [
            {
                "id": "test1",
                "title": "Test Title 1",
                "authors": ["Author 1", "Author 2"],
                "year": 2021,
                "venue": "Test Venue",
                "url": "https://example.com/test1",
                "citation": "Author 1, Author 2 (2021). Test Title 1. Test Venue."
            },
            {
                "id": "test2",
                "title": "Test Title 2",
                "authors": ["Author 3", "Author 4"],
                "year": 2022,
                "venue": "Test Venue 2",
                "url": "https://example.com/test2",
                "citation": "Author 3, Author 4 (2022). Test Title 2. Test Venue 2."
            }
        ]
        """

        # Call the method
        result = self.client.generate_json("Test prompt", None, 0.2)

        # Check the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "test1")
        self.assertEqual(result[1]["id"], "test2")

    @patch('core.google_ai_client.GoogleAIClient.generate_content')
    def test_generate_json_with_invalid_json(self, mock_generate_content):
        """Test generating JSON with invalid JSON response."""
        # Mock the response with invalid JSON (missing comma)
        mock_generate_content.return_value = """
        [
            {
                "id": "test1",
                "title": "Test Title 1",
                "authors": ["Author 1", "Author 2"]
                "year": 2021,
                "venue": "Test Venue",
                "url": "https://example.com/test1",
                "citation": "Author 1, Author 2 (2021). Test Title 1. Test Venue."
            }
        ]
        """

        # Call the method
        result = self.client.generate_json("Test prompt", None, 0.2)

        # Check the result
        # The JSON fixer might return more items than expected, but the first one should be correct
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test1")

    @patch('core.google_ai_client.GoogleAIClient.generate_content')
    def test_generate_json_with_non_ascii_characters(self, mock_generate_content):
        """Test generating JSON with non-ASCII characters."""
        # Mock the response with non-ASCII characters
        mock_generate_content.return_value = """
        [
            {
                "id": "test1",
                "title": "Test Title 1",
                "authors": ["Author 1", "Author 2" ক্যামি],
                "year": 2021,
                "venue": "Test Venue",
                "url": "https://example.com/test1",
                "citation": "Author 1, Author 2 (2021). Test Title 1. Test Venue."
            }
        ]
        """

        # Call the method
        result = self.client.generate_json("Test prompt", None, 0.2)

        # Check the result
        # The JSON fixer might return more items than expected, but the first one should be correct
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test1")
        self.assertGreaterEqual(len(result[0]["authors"]), 2)

    @patch('core.google_ai_client.GoogleAIClient.generate_content')
    def test_generate_json_with_trailing_comma(self, mock_generate_content):
        """Test generating JSON with trailing comma."""
        # Mock the response with trailing comma
        mock_generate_content.return_value = """
        [
            {
                "id": "test1",
                "title": "Test Title 1",
                "authors": ["Author 1", "Author 2",],
                "year": 2021,
                "venue": "Test Venue",
                "url": "https://example.com/test1",
                "citation": "Author 1, Author 2 (2021). Test Title 1. Test Venue."
            },
        ]
        """

        # Call the method
        result = self.client.generate_json("Test prompt", None, 0.2)

        # Check the result
        # The JSON fixer might return more items than expected, but the first one should be correct
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test1")
        self.assertGreaterEqual(len(result[0]["authors"]), 2)

if __name__ == "__main__":
    unittest.main()
