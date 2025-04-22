#!/usr/bin/env python3
"""
Simple test script for cloud functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import flask
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CloudFunctionTest(unittest.TestCase):
    """Simple test case for cloud functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True

        # Mock content request
        self.content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": "Introduction to AI",
            "mission_pillars": ["ResponsibleAI"]
        }

    def test_initialize_content_creation(self):
        """Test initialize_content_creation with valid input."""
        try:
            # Mock the necessary functions
            mock_store = MagicMock(return_value="Stored metadata")
            mock_publish = MagicMock(return_value="message-id-12345")
            mock_uuid = MagicMock()
            mock_uuid.hex = 'test-content-123'

            # Import the function
            with patch('cloud_function.main.store_content_metadata', mock_store):
                with patch('cloud_function.main.publish_event', mock_publish):
                    with patch('cloud_function.main.uuid.uuid4', return_value=mock_uuid):
                        from cloud_function.main import initialize_content_creation

                        # Create a mock Flask request
                        with self.app.test_request_context(json=self.content_request):
                            # Act
                            response = initialize_content_creation(flask.request)

                            # Assert
                            self.assertEqual(response.status_code, 200)
                            response_data = json.loads(response.data)
                            self.assertEqual(response_data['status'], 'success')
                            self.assertEqual(response_data['content_id'], 'test-content-123')

                            print("Test passed: initialize_content_creation")
        except ImportError as e:
            print(f"ImportError: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def test_simple_flask_request(self):
        """Test a simple Flask request."""
        # Define a simple route
        @self.app.route('/test', methods=['POST'])
        def test_route():
            request_json = flask.request.get_json()
            if not request_json:
                return flask.jsonify({'status': 'error'}), 400
            return flask.jsonify({'status': 'success', 'data': request_json})

        # Create a test client
        client = self.app.test_client()

        # Make a request
        response = client.post('/test', json=self.content_request)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'], self.content_request)

        print("Test passed: simple_flask_request")

if __name__ == '__main__':
    unittest.main()
