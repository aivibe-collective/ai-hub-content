"""
Integration tests for the source collection workflow.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import requests
import sys

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Flask app from the research service
from cloud_run.research_service.app import app

class TestSourceCollectionWorkflow(unittest.TestCase):
    """Integration tests for the source collection workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set up Flask test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Test content ID
        self.content_id = "test-content-12345678"
        
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
        
        # Test citation
        self.citation = {
            "reference": "McKinsey & Company. (2023). The state of AI in 2023: Generative AI's breakout year. McKinsey Digital. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
            "in_text_citation": "According to McKinsey & Company (2023)",
            "parenthetical_citation": "(McKinsey & Company, 2023)"
        }
        
        # Test integrated text
        self.integrated_text = "According to McKinsey & Company (2023), generative AI has seen rapid adoption in businesses, with 47% of organizations implementing it in at least one function."
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_identify_source_needs(self, mock_firestore, mock_model):
        """Test the identification of source needs."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.source_needs)
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/identify-source-needs', 
                                json={
                                    'content_id': self.content_id,
                                    'content_text': self.content_text
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['source_needs']), 2)
        self.assertEqual(response_data['source_needs'][0]['type'], 'statistical')
        self.assertEqual(response_data['source_needs'][1]['type'], 'conceptual')
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Analyze the following content and identify statements that require citations", prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_once_with('content-items')
        mock_db.collection().document.assert_called_once_with(self.content_id)
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('sources.needs', update_args)
        
        return response_data['source_needs']
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_research_sources(self, mock_firestore, mock_model):
        """Test the research of potential sources."""
        # Arrange
        source_needs = self.test_identify_source_needs()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.potential_sources)
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/research-sources', 
                                json={
                                    'content_id': self.content_id,
                                    'source_need_index': 0
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['potential_sources']), 1)
        self.assertEqual(response_data['potential_sources'][0]['title'], "The state of AI in 2023: Generative AI's breakout year")
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Research potential sources for the following statement", prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('sources.needs', update_args)
        
        # Update source_needs with potential sources for next test
        source_needs[0]['potential_sources'] = self.potential_sources
        return source_needs
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_evaluate_source(self, mock_firestore, mock_model):
        """Test the evaluation of a source."""
        # Arrange
        source_needs = self.test_research_sources()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.source_evaluation)
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/evaluate-source', 
                                json={
                                    'content_id': self.content_id,
                                    'source_need_index': 0,
                                    'source_index': 0
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['evaluation']['overall_score'], 4.4)
        self.assertEqual(response_data['evaluation']['currency']['score'], 5)
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Evaluate the following source using the CRAAP test criteria", prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('sources.needs', update_args)
        
        # Update source_needs with evaluation for next test
        source_needs[0]['potential_sources'][0]['evaluation'] = self.source_evaluation
        return source_needs
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_generate_citation(self, mock_firestore, mock_model):
        """Test the generation of a citation."""
        # Arrange
        source_needs = self.test_evaluate_source()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.citation)
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/generate-citation', 
                                json={
                                    'content_id': self.content_id,
                                    'source_need_index': 0,
                                    'source_index': 0,
                                    'citation_style': 'APA'
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn("McKinsey & Company. (2023)", response_data['citation']['reference'])
        self.assertIn("According to McKinsey & Company (2023)", response_data['citation']['in_text_citation'])
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Generate a citation for the following source in APA format", prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called()
        
        # Update source_needs with citation for next test
        source_needs[0]['potential_sources'][0]['citation'] = self.citation
        return source_needs
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_integrate_source(self, mock_firestore, mock_model):
        """Test the integration of a source into content."""
        # Arrange
        source_needs = self.test_generate_citation()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': source_needs
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = self.integrated_text
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/integrate-source', 
                                json={
                                    'content_id': self.content_id,
                                    'source_need_index': 0,
                                    'source_index': 0,
                                    'integration_type': 'paraphrase'
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['integration_type'], 'paraphrase')
        self.assertIn("According to McKinsey & Company (2023)", response_data['integrated_text'])
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Generate text that integrates the following source into content about AI", prompt)
        self.assertIn("paraphrase", prompt)
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('sources.needs', update_args)
    
    def test_end_to_end_source_collection_workflow(self):
        """Test the end-to-end source collection workflow."""
        # This test calls the other test methods in sequence to simulate the workflow
        self.test_integrate_source()

if __name__ == '__main__':
    unittest.main()
