"""
Integration tests for error handling in the Agentic AI Content Creation System.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import sys
import os
import uuid
import flask
import google.api_core.exceptions

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the modules under test
from cloud_function.main import initialize_content_creation, select_template, generate_content_plan
from cloud_function.utils import store_content_metadata, publish_event, call_vertex_ai

class TestErrorHandlingIntegration(unittest.TestCase):
    """Integration tests for error handling in the Agentic AI Content Creation System."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True
        
        # Test content ID
        self.test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Mock content request
        self.content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": "Introduction to Generative AI",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_firestore_error_during_initialization(self, mock_publish, mock_store):
        """Test error handling when Firestore fails during content initialization."""
        # Arrange
        mock_store.side_effect = google.api_core.exceptions.InternalServerError("Firestore connection error")
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 500)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Error initializing content creation', response_data['message'])
            
            # Verify that store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify that publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_pubsub_error_during_initialization(self, mock_uuid, mock_publish, mock_store):
        """Test error handling when Pub/Sub fails during content initialization."""
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.side_effect = Exception("Pub/Sub connection error")
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 500)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Error initializing content creation', response_data['message'])
            
            # Verify that store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify that publish_event was called
            mock_publish.assert_called_once()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_content_not_found_during_template_selection(self, mock_publish, mock_firestore):
        """Test error handling when content is not found during template selection."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content not found
        mock_content_ref.get.return_value.to_dict.return_value = None
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        select_template(event, None)
        
        # Assert
        # Verify that the content was not updated
        mock_content_ref.update.assert_not_called()
        
        # Verify that publish_event was not called
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_no_matching_template_found(self, mock_publish, mock_firestore):
        """Test error handling when no matching template is found."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'NonExistentType',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock template query
        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        
        # Mock empty template result
        mock_query.stream.return_value = []
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        select_template(event, None)
        
        # Assert
        # Verify that the content was updated with an error
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['metadata.status'], 'template_not_found')
        self.assertIn('No matching template found', update_args['error'])
        
        # Verify that publish_event was not called
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.publish_event')
    def test_vertex_ai_error_during_content_plan_generation(self, mock_publish, mock_call_vertex, mock_firestore):
        """Test error handling when Vertex AI fails during content plan generation."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            },
            'template': {
                'type': 'LearningModule',
                'sections': ['Introduction', 'Core Concepts']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI error
        mock_call_vertex.side_effect = Exception("Vertex AI API error")
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with an error
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['metadata.status'], 'plan_generation_failed')
        self.assertIn('Error generating content plan', update_args['error'])
        
        # Verify that publish_event was not called
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.publish_event')
    def test_non_json_response_from_vertex_ai(self, mock_publish, mock_call_vertex, mock_firestore):
        """Test error handling when Vertex AI returns a non-JSON response."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            },
            'template': {
                'type': 'LearningModule',
                'sections': ['Introduction', 'Core Concepts']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock non-JSON response
        mock_call_vertex.return_value = "This is not valid JSON"
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the raw plan
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['content.plan']['raw_plan'], "This is not valid JSON")
        self.assertIn('Failed to parse content plan as JSON', update_args['content.plan']['error'])
        
        # Verify that publish_event was called
        mock_publish.assert_called_once()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_missing_required_parameters(self, mock_uuid, mock_publish, mock_store):
        """Test error handling when required parameters are missing."""
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        
        # Create a mock Flask request with missing title
        with self.app.test_request_context(json={
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            # Missing title
            "mission_pillars": ["ResponsibleAI"]
        }):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('Missing required parameters', response_data['message'])
            
            # Verify that store_content_metadata was not called
            mock_store.assert_not_called()
            
            # Verify that publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_no_request_data(self, mock_publish, mock_store):
        """Test error handling when no request data is provided."""
        # Create a mock Flask request with no JSON data
        with self.app.test_request_context():
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'error')
            self.assertIn('No request data provided', response_data['message'])
            
            # Verify that store_content_metadata was not called
            mock_store.assert_not_called()
            
            # Verify that publish_event was not called
            mock_publish.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_firestore_error_during_template_selection(self, mock_publish, mock_firestore):
        """Test error handling when Firestore fails during template selection."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock Firestore error
        mock_content_ref.get.side_effect = google.api_core.exceptions.InternalServerError("Firestore connection error")
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        select_template(event, None)
        
        # Assert
        # Verify that the content was updated with an error
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['metadata.status'], 'template_selection_failed')
        self.assertIn('Error selecting template', update_args['error'])
        
        # Verify that publish_event was not called
        mock_publish.assert_not_called()

if __name__ == '__main__':
    unittest.main()
