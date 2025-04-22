"""
Integration tests for the content creation workflow.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import uuid
import base64
import sys

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the modules under test
from cloud_function.main import initialize_content_creation, select_template, generate_content_plan

class TestContentCreationWorkflow(unittest.TestCase):
    """Integration tests for the content creation workflow."""
    
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
            },
            "practical_examples": [
                "Text generation for customer service responses",
                "Image creation for marketing materials",
                "Code completion for software development"
            ],
            "visual_elements": [
                "Diagram comparing traditional and generative AI",
                "Flowchart of generative AI process",
                "Examples of generative AI outputs"
            ],
            "source_requirements": [
                "Recent statistics on generative AI adoption (last 1-2 years)",
                "Technical papers on generative AI architectures",
                "Case studies of successful implementations",
                "Ethical guidelines from reputable organizations"
            ],
            "mission_pillar_integration": {
                "ResponsibleAI": [
                    "Bias in training data and outputs",
                    "Privacy implications of generative models",
                    "Transparency and explainability challenges"
                ],
                "Inclusion": [
                    "Accessibility of generative AI tools",
                    "Representation in training data",
                    "Language support and cultural sensitivity"
                ]
            }
        }
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    def test_initialize_content_creation(self, mock_publish, mock_store):
        """Test the initialization of content creation."""
        # Arrange
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.get_json.return_value = self.content_request
        
        # Act
        with patch('uuid.uuid4', return_value=MagicMock(hex=self.test_content_id)):
            response = initialize_content_creation(mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('content_id', response_data)
        
        # Verify store_content_metadata was called with correct parameters
        mock_store.assert_called_once()
        args = mock_store.call_args[0]
        self.assertEqual(args[0], response_data['content_id'])
        metadata = args[1]
        self.assertEqual(metadata['metadata']['title'], self.content_request['title'])
        self.assertEqual(metadata['metadata']['type'], self.content_request['content_type'])
        self.assertEqual(metadata['metadata']['audience'], self.content_request['audience_level'])
        self.assertEqual(metadata['metadata']['mission_pillars'], self.content_request['mission_pillars'])
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], response_data['content_id'])
        self.assertEqual(args[1]['action'], 'select_template')
        
        # Return the content ID for use in subsequent tests
        return response_data['content_id']
    
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_select_template(self, mock_publish, mock_firestore):
        """Test the template selection process."""
        # Arrange
        content_id = self.test_initialize_content_creation()
        
        # Mock Firestore client and document
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the template query
        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        
        # Mock the template result
        mock_template_doc = MagicMock()
        mock_template_doc.to_dict.return_value = self.template
        mock_query.stream.return_value = [mock_template_doc]
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': content_id,
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
        mock_db.collection().document.assert_called_with(content_id)
        mock_db.collection.assert_any_call('templates')
        mock_db.collection().where.assert_called_with('type', '==', self.content_request['content_type'])
        mock_query.where.assert_called_with('audience_levels', 'array_contains', self.content_request['audience_level'])
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('template', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'template_selected')
        self.assertIn('workflow.current_stage', update_args)
        self.assertEqual(update_args['workflow.current_stage'], 'content_planning')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], content_id)
        self.assertEqual(args[1]['action'], 'generate_content_plan')
        
        # Return the content ID for use in subsequent tests
        return content_id
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_generate_content_plan(self, mock_publish, mock_firestore, mock_call_vertex):
        """Test the content plan generation process."""
        # Arrange
        content_id = self.test_select_template()
        
        # Mock Firestore client and document
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
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
        
        # Mock the Vertex AI response
        mock_call_vertex.return_value = json.dumps(self.content_plan)
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': content_id,
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
        mock_db.collection().document.assert_called_with(content_id)
        
        # Verify call to Vertex AI
        mock_call_vertex.assert_called_once()
        prompt = mock_call_vertex.call_args[0][0]
        self.assertIn(self.content_request['title'], prompt)
        self.assertIn(self.content_request['audience_level'], prompt)
        for pillar in self.content_request['mission_pillars']:
            self.assertIn(pillar, prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.plan', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generated')
        self.assertIn('workflow.current_stage', update_args)
        self.assertEqual(update_args['workflow.current_stage'], 'section_population')
        
        # Verify publish_event was called with correct parameters
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], 'content-creation-events')
        self.assertEqual(args[1]['content_id'], content_id)
        self.assertEqual(args[1]['action'], 'populate_sections')
    
    def test_end_to_end_content_creation_workflow(self):
        """Test the end-to-end content creation workflow."""
        # This test calls the other test methods in sequence to simulate the workflow
        self.test_generate_content_plan()

if __name__ == '__main__':
    unittest.main()
