"""
Test cases for the Source Collection and Documentation module.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import requests
import sys

# Add the parent directory to the path to import the cloud_run module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the research service
from cloud_run.research_service.app import app
import test.config as config

class TestSourceCollection(unittest.TestCase):
    """Test cases for the Source Collection and Documentation module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set up Flask test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Load test content
        self.test_content = "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed."
        
        # Load test sources
        self.sources = {}
        for filename in os.listdir(config.SOURCE_DATA_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(config.SOURCE_DATA_DIR, filename), 'r') as f:
                    source = json.load(f)
                    self.sources[source['id']] = source
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_source_need_identification(self, mock_firestore, mock_model):
        """TC5.1 - Source Need Identification: Check if the system correctly identifies when a source is needed."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps([
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
                "context": "Technical background section",
                "requirements": {
                    "recency": "Original paper or recent review",
                    "authority": "Academic paper",
                    "specific_needs": "Should reference the original 'Attention is All You Need' paper"
                }
            }
        ])
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/identify-source-needs', 
                                json={
                                    'content_id': 'test_content_1',
                                    'content_text': self.test_content
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
        self.assertIn(self.test_content, prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_once_with('content-items')
        mock_db.collection().document.assert_called_once_with('test_content_1')
        mock_content_ref.update.assert_called_once()
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_source_research(self, mock_firestore, mock_model):
        """TC5.2 - Source Research: Check if the system researches potential sources."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': [
                    {
                        "statement": "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function.",
                        "type": "statistical",
                        "context": "Introduction section discussing adoption rates",
                        "requirements": {
                            "recency": "Last 2 years",
                            "authority": "Industry report or survey",
                            "specific_needs": "Preferably from a reputable source like McKinsey, Gartner, etc."
                        }
                    }
                ]
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps([
            {
                "title": "The state of AI in 2023: Generative AI's breakout year",
                "authors": "McKinsey & Company",
                "publication": "McKinsey Digital",
                "year": 2023,
                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                "description": "This report provides statistics on AI adoption rates across industries, including the finding that 47% of organizations are using generative AI in at least one business function."
            }
        ])
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/research-sources', 
                                json={
                                    'content_id': 'test_content_1',
                                    'source_need_index': 0
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['potential_sources']), 1)
        self.assertEqual(response_data['potential_sources'][0]['title'], 'The state of AI in 2023: Generative AI's breakout year')
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Research potential sources for the following statement", prompt)
        self.assertIn("Generative AI has seen rapid adoption", prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test_content_1')
        mock_content_ref.update.assert_called_once()
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_source_evaluation(self, mock_firestore, mock_model):
        """TC5.3 - CRAAP Test: Check if the CRAAP test is applied correctly."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': [
                    {
                        "statement": "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function.",
                        "type": "statistical",
                        "context": "Introduction section discussing adoption rates",
                        "requirements": {
                            "recency": "Last 2 years",
                            "authority": "Industry report or survey",
                            "specific_needs": "Preferably from a reputable source like McKinsey, Gartner, etc."
                        },
                        "potential_sources": [
                            {
                                "title": "The state of AI in 2023: Generative AI's breakout year",
                                "authors": "McKinsey & Company",
                                "publication": "McKinsey Digital",
                                "year": 2023,
                                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year"
                            }
                        ]
                    }
                ]
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "currency": {
                "score": 5,
                "justification": "The source is from 2023, which is very recent and appropriate for current AI adoption statistics."
            },
            "relevance": {
                "score": 5,
                "justification": "The source directly addresses AI adoption rates in businesses, which is exactly what the statement claims."
            },
            "authority": {
                "score": 5,
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
            "overall_score": 4.6,
            "recommendation": "This is an excellent source for the statement. It is recent, highly relevant, from an authoritative source, and appears to be accurate and objective."
        })
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/evaluate-source', 
                                json={
                                    'content_id': 'test_content_1',
                                    'source_need_index': 0,
                                    'source_index': 0
                                })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['evaluation']['overall_score'], 4.6)
        self.assertEqual(response_data['evaluation']['currency']['score'], 5)
        
        # Verify the prompt sent to the model
        mock_model_instance.predict.assert_called_once()
        prompt = mock_model_instance.predict.call_args[1]['prompt']
        self.assertIn("Evaluate the following source using the CRAAP test criteria", prompt)
        self.assertIn("McKinsey & Company", prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test_content_1')
        mock_content_ref.update.assert_called_once()
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_citation_generation(self, mock_firestore, mock_model):
        """TC5.4 - Citation Generation: Check if citations are generated correctly."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': [
                    {
                        "statement": "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function.",
                        "type": "statistical",
                        "context": "Introduction section discussing adoption rates",
                        "requirements": {
                            "recency": "Last 2 years",
                            "authority": "Industry report or survey",
                            "specific_needs": "Preferably from a reputable source like McKinsey, Gartner, etc."
                        },
                        "potential_sources": [
                            {
                                "title": "The state of AI in 2023: Generative AI's breakout year",
                                "authors": "McKinsey & Company",
                                "publication": "McKinsey Digital",
                                "year": 2023,
                                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                                "evaluation": {
                                    "overall_score": 4.6,
                                    "recommendation": "Excellent source"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "reference": "McKinsey & Company. (2023). The state of AI in 2023: Generative AI's breakout year. McKinsey Digital. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
            "in_text_citation": "According to McKinsey & Company (2023)",
            "parenthetical_citation": "(McKinsey & Company, 2023)"
        })
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/generate-citation', 
                                json={
                                    'content_id': 'test_content_1',
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
        self.assertIn("McKinsey & Company", prompt)
        
        # Verify Firestore update
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test_content_1')
        mock_content_ref.update.assert_called()
    
    @patch('cloud_run.research_service.app.TextGenerationModel')
    @patch('cloud_run.research_service.app.firestore.Client')
    def test_source_integration(self, mock_firestore, mock_model):
        """TC5.5 - Source Integration: Check if sources are integrated correctly."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'sources': {
                'needs': [
                    {
                        "statement": "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function.",
                        "type": "statistical",
                        "context": "Introduction section discussing adoption rates",
                        "requirements": {
                            "recency": "Last 2 years",
                            "authority": "Industry report or survey",
                            "specific_needs": "Preferably from a reputable source like McKinsey, Gartner, etc."
                        },
                        "potential_sources": [
                            {
                                "title": "The state of AI in 2023: Generative AI's breakout year",
                                "authors": "McKinsey & Company",
                                "publication": "McKinsey Digital",
                                "year": 2023,
                                "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                                "evaluation": {
                                    "overall_score": 4.6,
                                    "recommendation": "Excellent source"
                                },
                                "citation": {
                                    "reference": "McKinsey & Company. (2023). The state of AI in 2023: Generative AI's breakout year. McKinsey Digital. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                                    "in_text_citation": "According to McKinsey & Company (2023)",
                                    "parenthetical_citation": "(McKinsey & Company, 2023)"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the Vertex AI response
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = MagicMock()
        mock_response.text = "According to McKinsey & Company (2023), generative AI has seen rapid adoption in businesses, with 47% of organizations implementing it in at least one function."
        mock_model_instance.predict.return_value = mock_response
        
        # Act
        response = self.app.post('/integrate-source', 
                                json={
                                    'content_id': 'test_content_1',
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
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with('test_content_1')
        mock_content_ref.update.assert_called_once()

if __name__ == '__main__':
    unittest.main()
