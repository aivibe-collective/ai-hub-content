"""
Integration tests for source collection workflow.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import sys
import os
import uuid
import flask

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the modules under test
from cloud_function.main import initialize_content_creation
from cloud_run.research_service.app import identify_source_needs, research_sources, evaluate_source

class TestSourceCollectionIntegration(unittest.TestCase):
    """Integration tests for source collection workflow."""
    
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
        
        # Test content text
        self.content_text = """
        # Introduction to Generative AI
        
        Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns. The transformer architecture, which relies on attention mechanisms, has been particularly successful for text generation tasks.
        
        ## Practical Applications
        
        Businesses are using generative AI for customer service automation, content creation, and code generation. These applications can significantly improve productivity and enable new capabilities.
        """
        
        # Test source needs
        self.source_needs = [
            {
                "statement": "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function.",
                "type": "statistical",
                "context": "Introduction section discussing adoption rates",
                "requirements": {
                    "recency": "Last 2 years",
                    "authority": "Industry report or survey",
                    "specific_needs": "Preferably from a reputable source like McKinsey, Gartner, etc."
                }
            },
            {
                "statement": "The transformer architecture, introduced in 2017, has been fundamental to these advances.",
                "type": "conceptual",
                "context": "Introduction section discussing technical background",
                "requirements": {
                    "recency": "Original paper or recent review",
                    "authority": "Academic paper",
                    "specific_needs": "Should reference the original 'Attention is All You Need' paper"
                }
            }
        ]
        
        # Test potential sources
        self.potential_sources = [
            {
                "title": "The state of AI in 2023: Generative AI's breakout year",
                "authors": "McKinsey & Company",
                "publication": "McKinsey Digital",
                "year": 2023,
                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                "description": "This report provides statistics on AI adoption rates across industries, including the finding that 47% of organizations are using generative AI in at least one business function."
            }
        ]
        
        # Test source evaluation
        self.source_evaluation = {
            "currency": {
                "score": 5,
                "justification": "The source is from 2023, which is very recent and appropriate for current AI adoption statistics."
            },
            "relevance": {
                "score": 5,
                "justification": "The source directly addresses AI adoption rates in businesses, which is exactly what the statement claims."
            },
            "authority": {
                "score": 4,
                "justification": "McKinsey & Company is a highly respected global management consulting firm known for its research and industry insights."
            },
            "accuracy": {
                "score": 4,
                "justification": "The information is based on a global survey with a large sample size, though the exact methodology is not fully detailed."
            },
            "purpose": {
                "score": 4,
                "justification": "While McKinsey has a commercial interest in AI consulting, this report appears to be objective research rather than a marketing piece."
            },
            "overall_score": 4.4,
            "recommendation": "This is an excellent source for the statement. It is recent, highly relevant, from an authoritative source, and appears to be accurate and objective."
        }
        
        # Create Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    def test_content_creation_with_source_collection(self, mock_uuid, mock_publish, mock_store):
        """Test content creation with source collection workflow."""
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
        
        # Step 2: Identify source needs
        
        # Arrange
        mock_firestore = MagicMock()
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Vertex AI response
        mock_model = MagicMock()
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.source_needs)
        mock_model_instance.predict.return_value = mock_response
        
        # Create a mock Flask request for identify_source_needs
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'content_text': self.content_text
        }):
            # Act - Identify source needs
            with patch('cloud_run.research_service.app.TextGenerationModel', mock_model):
                with patch('cloud_run.research_service.app.firestore.Client', return_value=mock_db):
                    response = identify_source_needs()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['source_needs']), 2)
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Analyze the following content and identify statements that require citations", prompt)
        
        # Step 3: Research sources
        
        # Arrange
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': self.source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Reset the mock
        mock_model_instance.predict.reset_mock()
        
        # Mock the Vertex AI response for research_sources
        mock_response.text = json.dumps(self.potential_sources)
        
        # Create a mock Flask request for research_sources
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'source_need_index': 0
        }):
            # Act - Research sources
            with patch('cloud_run.research_service.app.TextGenerationModel', mock_model):
                with patch('cloud_run.research_service.app.firestore.Client', return_value=mock_db):
                    response = research_sources()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['potential_sources']), 1)
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Research potential sources for the following statement", prompt)
        
        # Step 4: Evaluate source
        
        # Arrange
        # Update the mock content data with potential sources
        self.source_needs[0]['potential_sources'] = self.potential_sources
        mock_content_data = {
            'sources': {
                'needs': self.source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Reset the mock
        mock_model_instance.predict.reset_mock()
        
        # Mock the Vertex AI response for evaluate_source
        mock_response.text = json.dumps(self.source_evaluation)
        
        # Create a mock Flask request for evaluate_source
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'source_need_index': 0,
            'source_index': 0
        }):
            # Act - Evaluate source
            with patch('cloud_run.research_service.app.TextGenerationModel', mock_model):
                with patch('cloud_run.research_service.app.firestore.Client', return_value=mock_db):
                    response = evaluate_source()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['evaluation']['overall_score'], 4.4)
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Evaluate the following source using the CRAAP test criteria", prompt)
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_source_need_identification_error_handling(self, mock_firestore, mock_model):
        """Test error handling in source need identification."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Vertex AI error
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_model_instance.predict.side_effect = Exception("Vertex AI API error")
        
        # Create a mock Flask request
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'content_text': self.content_text
        }):
            # Act - Identify source needs with an error
            response = identify_source_needs()
        
        # Assert
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('Error identifying source needs', response_data['message'])
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_research_sources_missing_content(self, mock_firestore, mock_model):
        """Test research_sources with missing content."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response with no content
        mock_content_ref.get.return_value.to_dict.return_value = None
        
        # Create a mock Flask request
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'source_need_index': 0
        }):
            # Act - Research sources with missing content
            response = research_sources()
        
        # Assert
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('Content not found', response_data['message'])
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_evaluate_source_invalid_index(self, mock_firestore, mock_model):
        """Test evaluate_source with invalid source index."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': self.source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Create a mock Flask request with invalid source index
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'source_need_index': 0,
            'source_index': 999  # Invalid index
        }):
            # Act - Evaluate source with invalid index
            response = evaluate_source()
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('Invalid source index', response_data['message'])

if __name__ == '__main__':
    unittest.main()
