"""
Integration tests for cloud functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import sys
import os
import uuid

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the modules under test
from cloud_function.main import initialize_content_creation, select_template, generate_content_plan
from cloud_function.utils import store_content_metadata, publish_event, call_vertex_ai

class TestCloudFunctionIntegration(unittest.TestCase):
    """Integration tests for cloud functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a unique ID for test content
        self.test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Mock content request
        self.content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": "Introduction to Generative AI",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
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
                "By the end of this module, learners will be able to define generative AI and explain its key components.",
                "Learners will identify at least three common applications of generative AI in business contexts.",
                "Learners will recognize potential ethical issues in generative AI applications and suggest at least one mitigation strategy."
            ],
            "key_concepts": {
                "Introduction & Context": [
                    "Definition of generative AI",
                    "Distinction from traditional AI",
                    "Recent developments and breakthroughs"
                ],
                "Core Concepts": [
                    "How generative models work",
                    "Types of generative AI (text, image, code)",
                    "Key architectures (transformers, diffusion models)"
                ]
            }
        }
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_end_to_end_content_creation_workflow(self, mock_uuid, mock_publish, mock_store):
        """Test the end-to-end content creation workflow."""
        # Step 1: Initialize content creation
        
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock Flask request
        mock_request = MagicMock()
        mock_request.get_json.return_value = self.content_request
        mock_request.json = self.content_request
        
        # Act - Initialize content creation
        init_response = initialize_content_creation(mock_request)
        
        # Assert
        self.assertEqual(init_response.status_code, 200)
        init_data = json.loads(init_response.data)
        self.assertEqual(init_data['status'], 'success')
        self.assertEqual(init_data['content_id'], self.test_content_id)
        
        # Verify store_content_metadata was called with correct parameters
        mock_store.assert_called_once()
        store_args = mock_store.call_args[0]
        self.assertEqual(store_args[0], self.test_content_id)
        metadata = store_args[1]
        self.assertEqual(metadata['metadata']['title'], self.content_request['title'])
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        publish_args = mock_publish.call_args[0]
        self.assertEqual(publish_args[0], 'content-creation-events')
        self.assertEqual(publish_args[1]['content_id'], self.test_content_id)
        self.assertEqual(publish_args[1]['action'], 'select_template')
        
        # Step 2: Select template
        
        # Reset mocks
        mock_store.reset_mock()
        mock_publish.reset_mock()
        
        # Arrange
        mock_firestore = MagicMock()
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        
        mock_template_doc = MagicMock()
        mock_template_doc.to_dict.return_value = self.template
        mock_query.stream.return_value = [mock_template_doc]
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Select template
        with patch('cloud_function.main.firestore.Client', return_value=mock_db):
            select_template(event, None)
        
        # Assert
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('template', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'template_selected')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        publish_args = mock_publish.call_args[0]
        self.assertEqual(publish_args[0], 'content-creation-events')
        self.assertEqual(publish_args[1]['content_id'], self.test_content_id)
        self.assertEqual(publish_args[1]['action'], 'generate_content_plan')
        
        # Step 3: Generate content plan
        
        # Reset mocks
        mock_publish.reset_mock()
        mock_content_ref.reset_mock()
        
        # Arrange
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            },
            'template': self.template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        mock_call_vertex = MagicMock(return_value=json.dumps(self.content_plan))
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': self.test_content_id,
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Generate content plan
        with patch('cloud_function.main.firestore.Client', return_value=mock_db):
            with patch('cloud_function.main.call_vertex_ai', mock_call_vertex):
                generate_content_plan(event, None)
        
        # Assert
        # Verify call to Vertex AI
        mock_call_vertex.assert_called_once()
        prompt = mock_call_vertex.call_args[0][0]
        self.assertIn(self.content_request['title'], prompt)
        self.assertIn(self.content_request['audience_level'], prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.plan', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generated')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        publish_args = mock_publish.call_args[0]
        self.assertEqual(publish_args[0], 'content-creation-events')
        self.assertEqual(publish_args[1]['content_id'], self.test_content_id)
        self.assertEqual(publish_args[1]['action'], 'populate_sections')
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_error_handling_in_workflow(self, mock_publish, mock_store):
        """Test error handling in the content creation workflow."""
        # Arrange
        mock_store.side_effect = Exception("Database connection error")
        
        # Create a mock Flask request
        mock_request = MagicMock()
        mock_request.get_json.return_value = self.content_request
        mock_request.json = self.content_request
        
        # Act - Initialize content creation with a database error
        init_response = initialize_content_creation(mock_request)
        
        # Assert
        self.assertEqual(init_response.status_code, 500)
        init_data = json.loads(init_response.data)
        self.assertEqual(init_data['status'], 'error')
        self.assertIn('Database connection error', init_data['message'])
        
        # Verify store_content_metadata was called
        mock_store.assert_called_once()
        
        # Verify publish_event was not called
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_template_not_found_handling(self, mock_publish, mock_firestore):
        """Test handling of template not found in the workflow."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        mock_content_data = {
            'metadata': {
                'title': 'Test Content',
                'type': 'NonExistentType',  # Type that doesn't match any template
                'audience': 'Beginner',
                'mission_pillars': ['ResponsibleAI']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
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
        
        # Act - Select template with no matching template
        select_template(event, None)
        
        # Assert
        # Verify Firestore update with error
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'template_not_found')
        self.assertIn('error', update_args)
        self.assertIn('No matching template found', update_args['error'])
        
        # Verify publish_event was not called
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_vertex_ai_error_handling(self, mock_publish, mock_firestore, mock_call_vertex):
        """Test handling of Vertex AI errors in the workflow."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            },
            'template': self.template
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
        
        # Act - Generate content plan with Vertex AI error
        generate_content_plan(event, None)
        
        # Assert
        # Verify Firestore update with error
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generation_failed')
        self.assertIn('error', update_args)
        self.assertIn('Vertex AI API error', update_args['error'])
        
        # Verify publish_event was not called
        mock_publish.assert_not_called()

if __name__ == '__main__':
    unittest.main()
