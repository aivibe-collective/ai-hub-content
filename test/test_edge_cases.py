"""
Edge case tests for the Agentic AI Content Creation System.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import flask
import base64
import sys
import os
import uuid

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules under test
from cloud_function.main import initialize_content_creation, select_template, generate_content_plan

class TestEdgeCases(unittest.TestCase):
    """Edge case tests for the Agentic AI Content Creation System."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True
        
        # Test content ID
        self.test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_with_empty_mission_pillars(self, mock_publish, mock_store):
        """Test initializing content creation with empty mission pillars."""
        # Arrange
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock Flask request with empty mission pillars
        with self.app.test_request_context(json={
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": "Introduction to AI",
            "mission_pillars": []  # Empty mission pillars
        }):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            
            # Verify that store_content_metadata was called with empty mission pillars
            metadata_arg = mock_store.call_args[0][1]
            self.assertEqual(metadata_arg['metadata']['mission_pillars'], [])
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_with_very_long_title(self, mock_publish, mock_store):
        """Test initializing content creation with a very long title."""
        # Arrange
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a very long title (1000 characters)
        very_long_title = "A" * 1000
        
        # Create a mock Flask request with a very long title
        with self.app.test_request_context(json={
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": very_long_title,
            "mission_pillars": ["ResponsibleAI"]
        }):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            
            # Verify that store_content_metadata was called with the very long title
            metadata_arg = mock_store.call_args[0][1]
            self.assertEqual(metadata_arg['metadata']['title'], very_long_title)
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_select_template_with_no_audience_level(self, mock_publish, mock_firestore):
        """Test selecting a template with no audience level."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data with no audience level
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'LearningModule',
                # No audience level
                'mission_pillars': ['ResponsibleAI']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock template query
        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        
        # Mock template result
        mock_template = {
            "type": "LearningModule",
            "content": "# Learning Module Template",
            "audience_levels": ["Beginner", "Intermediate", "Expert"],
            "sections": [
                "1. Introduction & Context",
                "2. Core Concepts"
            ]
        }
        mock_template_doc = MagicMock()
        mock_template_doc.to_dict.return_value = mock_template
        mock_query.stream.return_value = [mock_template_doc]
        
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
        # Verify that the query was called with only the content type
        mock_db.collection.assert_called_with('templates')
        mock_db.collection.return_value.where.assert_called_with('type', '==', 'LearningModule')
        
        # Verify that the content was updated with the template
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['template'], mock_template)
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.publish_event')
    def test_generate_content_plan_with_invalid_json_response(self, mock_publish, mock_call_vertex, mock_firestore):
        """Test generating a content plan with an invalid JSON response from Vertex AI."""
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
                "type": "LearningModule",
                "content": "# Learning Module Template",
                "audience_levels": ["Beginner", "Intermediate", "Expert"],
                "sections": [
                    "1. Introduction & Context",
                    "2. Core Concepts"
                ]
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call with invalid JSON response
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
        # Verify that the content was updated with the raw text
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['content.plan']['raw_plan'], "This is not valid JSON")
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_with_special_characters(self, mock_publish, mock_store):
        """Test initializing content creation with special characters in the title."""
        # Arrange
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a title with special characters
        title_with_special_chars = "Introduction to AI: <script>alert('XSS')</script> & Other \"Topics\""
        
        # Create a mock Flask request with special characters in the title
        with self.app.test_request_context(json={
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": title_with_special_chars,
            "mission_pillars": ["ResponsibleAI"]
        }):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            
            # Verify that store_content_metadata was called with the title containing special characters
            metadata_arg = mock_store.call_args[0][1]
            self.assertEqual(metadata_arg['metadata']['title'], title_with_special_chars)
    
    @patch('cloud_function.main.firestore.Client')
    def test_select_template_with_nonexistent_content(self, mock_firestore):
        """Test selecting a template for nonexistent content."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock nonexistent content
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
        # Verify that no update was attempted
        mock_content_ref.update.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    def test_generate_content_plan_with_empty_template(self, mock_call_vertex, mock_firestore):
        """Test generating a content plan with an empty template."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data with empty template
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            },
            'template': {}  # Empty template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call
        mock_content_plan = {
            "learning_objectives": [
                "Objective 1"
            ]
        }
        mock_call_vertex.return_value = json.dumps(mock_content_plan)
        
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
        # Verify that the content was updated with the content plan
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['content.plan'], mock_content_plan)
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_with_unicode_characters(self, mock_publish, mock_store):
        """Test initializing content creation with Unicode characters in the title."""
        # Arrange
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a title with Unicode characters
        unicode_title = "Introduction à l'IA: 人工智能简介 and その他のトピック"
        
        # Create a mock Flask request with Unicode characters in the title
        with self.app.test_request_context(json={
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": unicode_title,
            "mission_pillars": ["ResponsibleAI"]
        }):
            # Act
            response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            
            # Verify that store_content_metadata was called with the Unicode title
            metadata_arg = mock_store.call_args[0][1]
            self.assertEqual(metadata_arg['metadata']['title'], unicode_title)

if __name__ == '__main__':
    unittest.main()
