"""
Unit tests for cloud_function/main.py
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import flask
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules under test
from cloud_function.main import initialize_content_creation, select_template, generate_content_plan

class TestCloudFunctionMain(unittest.TestCase):
    """Unit tests for the main cloud functions."""
    
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
        
        # Mock template
        self.template = {
            "type": "LearningModule",
            "content": "# Learning Module Template\n\n**1. Introduction & Context:**\nProvide an overview of the topic and why it matters.\n\n**2. Core Concepts:**\nExplain the fundamental concepts and principles.\n\n**3. Practical Applications:**\nShow how the concepts are applied in real-world scenarios.\n\n**4. Hands-on Exercise:**\nInclude interactive elements for practical learning.\n\n**5. Responsible AI & Sustainability in Practice:**\nAddress ethical considerations and sustainability aspects.\n\n**6. Further Resources:**\nProvide additional reading and learning materials.",
            "audience_levels": ["Beginner", "Intermediate", "Expert"],
            "sections": [
                "1. Introduction & Context",
                "2. Core Concepts",
                "3. Practical Applications",
                "4. Hands-on Exercise",
                "5. Responsible AI & Sustainability in Practice",
                "6. Further Resources"
            ]
        }
        
        # Mock content plan
        self.content_plan = {
            "learning_objectives": [
                "By the end of this module, learners will be able to define AI and explain its key components.",
                "Learners will identify at least three common applications of AI in business contexts.",
                "Learners will recognize potential ethical issues in AI applications and suggest at least one mitigation strategy."
            ],
            "key_concepts": {
                "Introduction & Context": [
                    "Definition of AI",
                    "Brief history of AI development",
                    "Current state of AI technology"
                ],
                "Core Concepts": [
                    "Machine learning fundamentals",
                    "Neural networks",
                    "Natural language processing"
                ]
            }
        }
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_initialize_content_creation_valid(self, mock_uuid, mock_publish, mock_store):
        """Test initialize_content_creation with valid input."""
        # Arrange
        mock_uuid.return_value = MagicMock(hex='test-content-123')
        mock_store.return_value = "Stored metadata for content test-content-123"
        mock_publish.return_value = "message-id-12345"
        
        # Act
        with self.app.test_request_context(json=self.content_request):
            result = initialize_content_creation(flask.request)
        
        # Assert
        self.assertEqual(result.status_code, 200)
        result_data = json.loads(result.data)
        self.assertEqual(result_data['status'], 'success')
        self.assertIn('content_id', result_data)
        self.assertEqual(result_data['content_id'], 'test-content-123')
        
        # Verify store_content_metadata was called with correct parameters
        mock_store.assert_called_once()
        args = mock_store.call_args[0]
        self.assertEqual(args[0], 'test-content-123')
        metadata = args[1]
        self.assertEqual(metadata['metadata']['title'], self.content_request['title'])
        self.assertEqual(metadata['metadata']['type'], self.content_request['content_type'])
        self.assertEqual(metadata['metadata']['audience'], self.content_request['audience_level'])
        self.assertEqual(metadata['metadata']['mission_pillars'], self.content_request['mission_pillars'])
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], 'test-content-123')
        self.assertEqual(args[1]['action'], 'select_template')
    
    def test_initialize_content_creation_missing_params(self):
        """Test initialize_content_creation with missing parameters."""
        # Act
        with self.app.test_request_context(json={
            'audience_level': 'Beginner',
            'mission_pillars': ['ResponsibleAI']
        }):
            result = initialize_content_creation(flask.request)
        
        # Assert
        self.assertEqual(result.status_code, 400)
        result_data = json.loads(result.data)
        self.assertEqual(result_data['status'], 'error')
        self.assertIn('Missing required parameters', result_data['message'])
    
    def test_initialize_content_creation_no_json(self):
        """Test initialize_content_creation with no JSON data."""
        # Act
        with self.app.test_request_context():
            result = initialize_content_creation(flask.request)
        
        # Assert
        self.assertEqual(result.status_code, 400)
        result_data = json.loads(result.data)
        self.assertEqual(result_data['status'], 'error')
        self.assertIn('No request data provided', result_data['message'])
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_initialize_content_creation_store_error(self, mock_uuid, mock_publish, mock_store):
        """Test initialize_content_creation with an error in store_content_metadata."""
        # Arrange
        mock_uuid.return_value = MagicMock(hex='test-content-123')
        mock_store.side_effect = Exception("Database connection error")
        
        # Act
        with self.app.test_request_context(json=self.content_request):
            result = initialize_content_creation(flask.request)
        
        # Assert
        self.assertEqual(result.status_code, 500)
        result_data = json.loads(result.data)
        self.assertEqual(result_data['status'], 'error')
        self.assertIn('Error initializing content creation', result_data['message'])
        self.assertIn('Database connection error', result_data['message'])
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_select_template_success(self, mock_publish, mock_firestore):
        """Test select_template with a successful template selection."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        # Mock content document
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        mock_content_data = {
            'metadata': {
                'title': 'Introduction to AI',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock template query
        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        
        # Mock template result
        mock_template_doc = MagicMock()
        mock_template_doc.to_dict.return_value = self.template
        mock_query.stream.return_value = [mock_template_doc]
        
        # Mock Pub/Sub event
        event_data = {
            'content_id': 'test-content-123',
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        select_template(event, None)
        
        # Assert
        # Verify Firestore queries
        mock_db.collection.assert_any_call('content-items')
        mock_db.collection().document.assert_called_with('test-content-123')
        mock_db.collection.assert_any_call('templates')
        mock_db.collection().where.assert_called_with('type', '==', 'LearningModule')
        mock_query.where.assert_called_with('audience_levels', 'array_contains', 'Beginner')
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('template', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'template_selected')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], 'test-content-123')
        self.assertEqual(args[1]['action'], 'generate_content_plan')
    
    @patch('cloud_function.main.firestore.Client')
    def test_select_template_no_template(self, mock_firestore):
        """Test select_template when no matching template is found."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        # Mock content document
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        mock_content_data = {
            'metadata': {
                'title': 'Introduction to AI',
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
        
        # Mock Pub/Sub event
        event_data = {
            'content_id': 'test-content-123',
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        select_template(event, None)
        
        # Assert
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'template_not_found')
        self.assertIn('error', update_args)
        self.assertIn('No matching template found', update_args['error'])
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_generate_content_plan(self, mock_publish, mock_firestore, mock_call_vertex):
        """Test the content plan generation process."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'metadata': {
                'title': 'Introduction to AI',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            },
            'template': self.template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_call_vertex.return_value = json.dumps(self.content_plan)
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test-content-123',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify Firestore queries
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test-content-123')
        
        # Verify call to Vertex AI
        mock_call_vertex.assert_called_once()
        prompt = mock_call_vertex.call_args[0][0]
        self.assertIn('Introduction to AI', prompt)
        self.assertIn('Beginner', prompt)
        self.assertIn('ResponsibleAI', prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.plan', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generated')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], 'test-content-123')
        self.assertEqual(args[1]['action'], 'populate_sections')
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    def test_generate_content_plan_vertex_error(self, mock_firestore, mock_call_vertex):
        """Test content plan generation with a Vertex AI error."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'metadata': {
                'title': 'Introduction to AI',
                'type': 'LearningModule',
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            },
            'template': self.template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI error
        mock_call_vertex.side_effect = Exception("Vertex AI API error")
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test-content-123',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify Firestore update with error
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generation_failed')
        self.assertIn('error', update_args)
        self.assertIn('Vertex AI API error', update_args['error'])

if __name__ == '__main__':
    unittest.main()
