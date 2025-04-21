"""
Test cases for the Cloud Functions.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import sys
from flask import Flask, Response

# Add the parent directory to the path to import the cloud_function module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud_function.main import initialize_content_creation
from test import config

class TestCloudFunctions(unittest.TestCase):
    """Test cases for the Cloud Functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = Flask(__name__)
        self.app.testing = True
        
        # Load test content plans
        self.content_plans = {}
        for filename in os.listdir(config.CONTENT_PLANS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(config.CONTENT_PLANS_DIR, filename), 'r') as f:
                    plan = json.load(f)
                    self.content_plans[plan['id']] = plan
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation_valid(self, mock_publish, mock_store):
        """Test initialize_content_creation with valid input."""
        # Arrange
        mock_store.return_value = "Stored metadata for content test-12345678"
        mock_publish.return_value = "message-id-12345"
        
        # Create a test request
        plan = self.content_plans.get('plan_learning_beginner')
        with self.app.test_request_context(
            json={
                'content_type': plan['content_type'],
                'audience_level': plan['audience_level'],
                'title': plan['title'],
                'mission_pillars': plan['mission_pillars']
            }
        ):
            # Act
            response = initialize_content_creation(MagicMock())
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertIn('content_id', response_data)
            self.assertIn(plan['content_type'].lower(), response_data['content_id'])
            
            # Verify store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify publish_event was called
            mock_publish.assert_called_once_with('content-creation-events', {
                'content_id': response_data['content_id'],
                'action': 'select_template'
            })
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation_missing_params(self, mock_publish, mock_store):
        """Test initialize_content_creation with missing parameters."""
        # Create a test request with missing parameters
        with self.app.test_request_context(
            json={
                'audience_level': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            }
        ):
            # Act
            response = initialize_content_creation(MagicMock())
            
            # Assert
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Missing required parameters', response_data['message'])
            
            # Verify store_content_metadata was not called
            mock_store.assert_not_called()
            
            # Verify publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation_no_json(self, mock_publish, mock_store):
        """Test initialize_content_creation with no JSON data."""
        # Create a test request with no JSON data
        with self.app.test_request_context():
            # Act
            response = initialize_content_creation(MagicMock())
            
            # Assert
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('No request data provided', response_data['message'])
            
            # Verify store_content_metadata was not called
            mock_store.assert_not_called()
            
            # Verify publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation_store_error(self, mock_publish, mock_store):
        """Test initialize_content_creation with an error in store_content_metadata."""
        # Arrange
        mock_store.side_effect = Exception("Database connection error")
        
        # Create a test request
        plan = self.content_plans.get('plan_learning_beginner')
        with self.app.test_request_context(
            json={
                'content_type': plan['content_type'],
                'audience_level': plan['audience_level'],
                'title': plan['title'],
                'mission_pillars': plan['mission_pillars']
            }
        ):
            # Act
            response = initialize_content_creation(MagicMock())
            
            # Assert
            self.assertEqual(response.status_code, 500)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Database connection error', response_data['message'])
            
            # Verify store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation_publish_error(self, mock_publish, mock_store):
        """Test initialize_content_creation with an error in publish_event."""
        # Arrange
        mock_store.return_value = "Stored metadata for content test-12345678"
        mock_publish.side_effect = Exception("Pub/Sub connection error")
        
        # Create a test request
        plan = self.content_plans.get('plan_learning_beginner')
        with self.app.test_request_context(
            json={
                'content_type': plan['content_type'],
                'audience_level': plan['audience_level'],
                'title': plan['title'],
                'mission_pillars': plan['mission_pillars']
            }
        ):
            # Act
            response = initialize_content_creation(MagicMock())
            
            # Assert
            self.assertEqual(response.status_code, 500)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Pub/Sub connection error', response_data['message'])
            
            # Verify store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify publish_event was called
            mock_publish.assert_called_once()

if __name__ == '__main__':
    unittest.main()
