"""
Test cases for the Content Generation component.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import base64
import sys

# Add the parent directory to the path to import the cloud_function module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud_function.main import generate_content_plan
import test.config as config

class TestContentGeneration(unittest.TestCase):
    """Test cases for the Content Generation component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load test content plans
        self.content_plans = {}
        for filename in os.listdir(config.CONTENT_PLANS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(config.CONTENT_PLANS_DIR, filename), 'r') as f:
                    plan = json.load(f)
                    self.content_plans[plan['id']] = plan
        
        # Load test templates
        self.templates = {}
        for filename in os.listdir(config.TEMPLATES_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(config.TEMPLATES_DIR, filename), 'r') as f:
                    template = json.load(f)
                    self.templates[template['type']] = template
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_content_plan_generation(self, mock_publish, mock_firestore, mock_call_vertex):
        """TC3.3 - Learning Objective Alignment: Test content plan generation with SMART objectives."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        plan = self.content_plans.get('plan_learning_beginner')
        template = self.templates.get(config.ContentTypes.LEARNING_MODULE)
        
        mock_content_data = {
            'metadata': {
                'title': plan['title'],
                'type': plan['content_type'],
                'audience': plan['audience_level'],
                'mission_pillars': plan['mission_pillars']
            },
            'template': template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_call_vertex.return_value = json.dumps({
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
        })
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test_content_1',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify the call to Vertex AI
        mock_call_vertex.assert_called_once()
        prompt = mock_call_vertex.call_args[0][0]
        self.assertIn("You are an expert content planner", prompt)
        self.assertIn(plan['title'], prompt)
        self.assertIn(plan['audience_level'], prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test_content_1')
        mock_content_ref.update.assert_called_once()
        
        # Verify the update contains the content plan
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.plan', update_args)
        self.assertIn('metadata.status', update_args)
        self.assertEqual(update_args['metadata.status'], 'plan_generated')
        self.assertIn('workflow.current_stage', update_args)
        self.assertEqual(update_args['workflow.current_stage'], 'section_population')
        
        # Verify the event was published
        mock_publish.assert_called_once()
        publish_args = mock_publish.call_args[0]
        self.assertEqual(publish_args[0], 'content-creation-events')
        self.assertEqual(publish_args[1]['content_id'], 'test_content_1')
        self.assertEqual(publish_args[1]['action'], 'populate_sections')
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_content_plan_json_error_handling(self, mock_publish, mock_firestore, mock_call_vertex):
        """Test handling of non-JSON responses from Vertex AI."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        plan = self.content_plans.get('plan_learning_beginner')
        template = self.templates.get(config.ContentTypes.LEARNING_MODULE)
        
        mock_content_data = {
            'metadata': {
                'title': plan['title'],
                'type': plan['content_type'],
                'audience': plan['audience_level'],
                'mission_pillars': plan['mission_pillars']
            },
            'template': template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response with non-JSON text
        mock_call_vertex.return_value = "This is not valid JSON but should be handled gracefully."
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test_content_1',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        
        # Verify the update contains the raw text as a fallback
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.plan', update_args)
        self.assertEqual(update_args['content.plan']['raw_plan'], "This is not valid JSON but should be handled gracefully.")
        
        # Verify the event was still published
        mock_publish.assert_called_once()
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_content_plan_error_handling(self, mock_publish, mock_firestore, mock_call_vertex):
        """Test error handling in content plan generation."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response to return None (content not found)
        mock_content_ref.get.return_value.to_dict.return_value = None
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test_content_1',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify Vertex AI was not called
        mock_call_vertex.assert_not_called()
        
        # Verify no Firestore update was made
        mock_content_ref.update.assert_not_called()
        
        # Verify no event was published
        mock_publish.assert_not_called()
    
    @patch('cloud_function.main.call_vertex_ai')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.publish_event')
    def test_content_plan_audience_analysis(self, mock_publish, mock_firestore, mock_call_vertex):
        """TC3.1 - Audience Analysis: Test audience-specific content planning."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        plan = self.content_plans.get('plan_case_study')
        template = self.templates.get(config.ContentTypes.CASE_STUDY)
        
        mock_content_data = {
            'metadata': {
                'title': plan['title'],
                'type': plan['content_type'],
                'audience': plan['audience_level'],
                'mission_pillars': plan['mission_pillars']
            },
            'template': template
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_call_vertex.return_value = json.dumps({
            "learning_objectives": [
                "By examining this case study, intermediate practitioners will understand how to implement RAG for customer support.",
                "Readers will be able to evaluate the performance improvements achieved through RAG implementation.",
                "Practitioners will identify key challenges and solutions in RAG deployment for customer support."
            ],
            "key_concepts": {
                "Introduction & Context": [
                    "Customer support challenges addressed by RAG",
                    "Previous solution limitations",
                    "Technical environment and constraints"
                ],
                "Solution Design": [
                    "RAG architecture selection",
                    "Knowledge base preparation",
                    "Integration with existing systems"
                ]
            }
        })
        
        # Create a mock Pub/Sub event
        event_data = {
            'content_id': 'test_content_2',
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act
        generate_content_plan(event, None)
        
        # Assert
        # Verify the prompt includes audience information
        mock_call_vertex.assert_called_once()
        prompt = mock_call_vertex.call_args[0][0]
        self.assertIn("Audience level: Intermediate", prompt)
        
        # Verify the content plan includes audience-specific elements
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        content_plan = json.loads(mock_call_vertex.return_value)
        self.assertIn("intermediate practitioners", content_plan["learning_objectives"][0])

if __name__ == '__main__':
    unittest.main()
