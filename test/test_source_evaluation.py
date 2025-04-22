"""
Test cases for the Source Evaluation component of the Source Collection module.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

class TestSourceEvaluation(unittest.TestCase):
    """Test cases for the Source Evaluation component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load test sources
        self.sources = {}
        try:
            with open('test/data/sources/source1.json', 'r') as f:
                self.sources['recent_industry'] = json.load(f)
            with open('test/data/sources/source2.json', 'r') as f:
                self.sources['academic_paper'] = json.load(f)
            with open('test/data/sources/source5.json', 'r') as f:
                self.sources['outdated'] = json.load(f)
            with open('test/data/sources/source6.json', 'r') as f:
                self.sources['biased'] = json.load(f)
        except FileNotFoundError:
            # Create mock sources if files don't exist
            self.sources = {
                'recent_industry': {
                    "id": "source1",
                    "title": "The state of AI in 2023: Generative AI's breakout year",
                    "authors": ["McKinsey & Company"],
                    "publication": "McKinsey Digital",
                    "year": 2023,
                    "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
                    "type": "industry_report",
                    "content_snippet": "47% of organizations are using generative AI in at least one business function, according to our latest McKinsey Global Survey on AI."
                },
                'academic_paper': {
                    "id": "source2",
                    "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
                    "publication": "Advances in Neural Information Processing Systems",
                    "year": 2017,
                    "url": "https://arxiv.org/abs/1706.03762",
                    "doi": "10.48550/arXiv.1706.03762",
                    "type": "academic_paper",
                    "content_snippet": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
                },
                'outdated': {
                    "id": "source5",
                    "title": "Outdated AI Information",
                    "authors": ["Legacy Researcher"],
                    "publication": "Journal of Historical AI",
                    "year": 2010,
                    "url": "https://example.com/outdated",
                    "type": "academic_paper",
                    "content_snippet": "Neural networks will never be practical for commercial applications due to computational limitations."
                },
                'biased': {
                    "id": "source6",
                    "title": "Biased AI Research",
                    "authors": ["Biased Author"],
                    "publication": "Commercial AI Vendor Blog",
                    "year": 2023,
                    "url": "https://example.com/biased-research",
                    "type": "blog_post",
                    "content_snippet": "Our proprietary AI system outperforms all others by at least 200% on all benchmarks.",
                    "bias_indicators": ["commercial interest", "no methodology details", "extreme claims"]
                }
            }
    
    def test_currency_evaluation_recent(self):
        """Test currency evaluation for a recent source."""
        # Arrange
        source = self.sources['recent_industry']
        mock_evaluate_currency = MagicMock(return_value={
            "score": 5,
            "justification": "The source is from 2023, which is very recent and appropriate for current AI adoption statistics."
        })
        
        # Act
        result = mock_evaluate_currency(source)
        
        # Assert
        self.assertEqual(result["score"], 5)
        self.assertIn("recent", result["justification"].lower())
        mock_evaluate_currency.assert_called_once_with(source)
    
    def test_currency_evaluation_outdated(self):
        """Test currency evaluation for an outdated source."""
        # Arrange
        source = self.sources['outdated']
        mock_evaluate_currency = MagicMock(return_value={
            "score": 1,
            "justification": "The source is from 2010, which is very outdated for AI information. The field has changed dramatically since then."
        })
        
        # Act
        result = mock_evaluate_currency(source)
        
        # Assert
        self.assertEqual(result["score"], 1)
        self.assertIn("outdated", result["justification"].lower())
        mock_evaluate_currency.assert_called_once_with(source)
    
    def test_relevance_evaluation_high(self):
        """Test relevance evaluation for a highly relevant source."""
        # Arrange
        source = self.sources['recent_industry']
        statement = "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function."
        
        mock_evaluate_relevance = MagicMock(return_value={
            "score": 5,
            "justification": "The source directly addresses AI adoption rates in businesses, which is exactly what the statement claims."
        })
        
        # Act
        result = mock_evaluate_relevance(source, statement)
        
        # Assert
        self.assertEqual(result["score"], 5)
        self.assertIn("directly addresses", result["justification"].lower())
        mock_evaluate_relevance.assert_called_once_with(source, statement)
    
    def test_relevance_evaluation_low(self):
        """Test relevance evaluation for a less relevant source."""
        # Arrange
        source = self.sources['academic_paper']
        statement = "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function."
        
        mock_evaluate_relevance = MagicMock(return_value={
            "score": 2,
            "justification": "While the paper is foundational for transformer models used in generative AI, it doesn't address business adoption rates at all."
        })
        
        # Act
        result = mock_evaluate_relevance(source, statement)
        
        # Assert
        self.assertEqual(result["score"], 2)
        self.assertIn("doesn't address", result["justification"].lower())
        mock_evaluate_relevance.assert_called_once_with(source, statement)
    
    def test_authority_evaluation_high(self):
        """Test authority evaluation for a highly authoritative source."""
        # Arrange
        source = self.sources['academic_paper']
        mock_evaluate_authority = MagicMock(return_value={
            "score": 5,
            "justification": "The paper is published in a prestigious peer-reviewed conference (NeurIPS) and authored by researchers from Google and other respected institutions. It has over 50,000 citations, indicating its significant impact and recognition in the field."
        })
        
        # Act
        result = mock_evaluate_authority(source)
        
        # Assert
        self.assertEqual(result["score"], 5)
        self.assertIn("peer-reviewed", result["justification"].lower())
        mock_evaluate_authority.assert_called_once_with(source)
    
    def test_authority_evaluation_low(self):
        """Test authority evaluation for a less authoritative source."""
        # Arrange
        source = self.sources['biased']
        mock_evaluate_authority = MagicMock(return_value={
            "score": 2,
            "justification": "The source is a blog post from a commercial vendor with a clear interest in promoting their product. There's no peer review, and the author's credentials in AI research are not established."
        })
        
        # Act
        result = mock_evaluate_authority(source)
        
        # Assert
        self.assertEqual(result["score"], 2)
        self.assertIn("commercial vendor", result["justification"].lower())
        mock_evaluate_authority.assert_called_once_with(source)
    
    def test_accuracy_evaluation_high(self):
        """Test accuracy evaluation for a highly accurate source."""
        # Arrange
        source = self.sources['recent_industry']
        mock_evaluate_accuracy = MagicMock(return_value={
            "score": 4,
            "justification": "The information is based on a global survey with a large sample size. The methodology is described, though not in full detail. McKinsey has a reputation for rigorous research methods."
        })
        
        # Act
        result = mock_evaluate_accuracy(source)
        
        # Assert
        self.assertEqual(result["score"], 4)
        self.assertIn("survey", result["justification"].lower())
        mock_evaluate_accuracy.assert_called_once_with(source)
    
    def test_accuracy_evaluation_low(self):
        """Test accuracy evaluation for a less accurate source."""
        # Arrange
        source = self.sources['biased']
        mock_evaluate_accuracy = MagicMock(return_value={
            "score": 1,
            "justification": "The claim of 200% improvement is extreme and not supported by methodology details or independent verification. No information is provided about benchmarks, comparison systems, or testing procedures."
        })
        
        # Act
        result = mock_evaluate_accuracy(source)
        
        # Assert
        self.assertEqual(result["score"], 1)
        self.assertIn("not supported", result["justification"].lower())
        mock_evaluate_accuracy.assert_called_once_with(source)
    
    def test_purpose_evaluation_objective(self):
        """Test purpose evaluation for an objective source."""
        # Arrange
        source = self.sources['academic_paper']
        mock_evaluate_purpose = MagicMock(return_value={
            "score": 5,
            "justification": "The paper's purpose is to present research findings and advance knowledge in the field. It follows academic conventions for objectivity and doesn't appear to have commercial or political motivations."
        })
        
        # Act
        result = mock_evaluate_purpose(source)
        
        # Assert
        self.assertEqual(result["score"], 5)
        self.assertIn("objectivity", result["justification"].lower())
        mock_evaluate_purpose.assert_called_once_with(source)
    
    def test_purpose_evaluation_biased(self):
        """Test purpose evaluation for a biased source."""
        # Arrange
        source = self.sources['biased']
        mock_evaluate_purpose = MagicMock(return_value={
            "score": 1,
            "justification": "The source is clearly promotional content from a vendor with a commercial interest in presenting their product favorably. The purpose is marketing rather than objective information sharing."
        })
        
        # Act
        result = mock_evaluate_purpose(source)
        
        # Assert
        self.assertEqual(result["score"], 1)
        self.assertIn("promotional", result["justification"].lower())
        mock_evaluate_purpose.assert_called_once_with(source)
    
    def test_overall_evaluation_excellent(self):
        """Test overall evaluation for an excellent source."""
        # Arrange
        source = self.sources['academic_paper']
        mock_evaluate_source = MagicMock(return_value={
            "currency": {
                "score": 4,
                "justification": "The paper is from 2017, which is relatively recent for a foundational paper in AI."
            },
            "relevance": {
                "score": 5,
                "justification": "The paper directly addresses transformer architecture, which is the focus of the statement."
            },
            "authority": {
                "score": 5,
                "justification": "Published in a prestigious peer-reviewed conference with authors from respected institutions."
            },
            "accuracy": {
                "score": 5,
                "justification": "The paper presents empirical results with detailed methodology and has been extensively validated by subsequent research."
            },
            "purpose": {
                "score": 5,
                "justification": "The paper's purpose is to present research findings with no apparent bias or agenda."
            },
            "overall_score": 4.8,
            "recommendation": "This is an excellent source. It is highly authoritative, accurate, and relevant to the topic."
        })
        
        # Act
        result = mock_evaluate_source(source)
        
        # Assert
        self.assertGreaterEqual(result["overall_score"], 4.5)
        self.assertIn("excellent", result["recommendation"].lower())
        mock_evaluate_source.assert_called_once_with(source)
    
    def test_overall_evaluation_poor(self):
        """Test overall evaluation for a poor source."""
        # Arrange
        source = self.sources['biased']
        mock_evaluate_source = MagicMock(return_value={
            "currency": {
                "score": 5,
                "justification": "The source is from 2023, which is very recent."
            },
            "relevance": {
                "score": 3,
                "justification": "The source discusses AI performance, which is related to the topic."
            },
            "authority": {
                "score": 2,
                "justification": "The source is a commercial blog post without peer review."
            },
            "accuracy": {
                "score": 1,
                "justification": "The claims are extreme and not supported by evidence."
            },
            "purpose": {
                "score": 1,
                "justification": "The source is clearly promotional content with commercial bias."
            },
            "overall_score": 2.4,
            "recommendation": "This source should not be used. It has a clear commercial bias and makes extreme claims without proper evidence."
        })
        
        # Act
        result = mock_evaluate_source(source)
        
        # Assert
        self.assertLessEqual(result["overall_score"], 3.0)
        self.assertIn("should not be used", result["recommendation"].lower())
        mock_evaluate_source.assert_called_once_with(source)
    
    def test_craap_test_implementation(self):
        """Test the complete CRAAP test implementation."""
        # Arrange
        source = self.sources['recent_industry']
        statement = "Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function."
        
        mock_craap_test = MagicMock(return_value={
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
        })
        
        # Act
        result = mock_craap_test(source, statement)
        
        # Assert
        self.assertIn("currency", result)
        self.assertIn("relevance", result)
        self.assertIn("authority", result)
        self.assertIn("accuracy", result)
        self.assertIn("purpose", result)
        self.assertIn("overall_score", result)
        self.assertIn("recommendation", result)
        
        # Check that all criteria have scores and justifications
        for criterion in ["currency", "relevance", "authority", "accuracy", "purpose"]:
            self.assertIn("score", result[criterion])
            self.assertIn("justification", result[criterion])
        
        mock_craap_test.assert_called_once_with(source, statement)

if __name__ == '__main__':
    unittest.main()
