"""
Integration tests for the mission pillar integration workflow.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestMissionPillarIntegrationWorkflow(unittest.TestCase):
    """Integration tests for the mission pillar integration workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Test content ID
        self.content_id = "test-content-12345678"
        
        # Test content section
        self.content_section = """
        # Introduction to Generative AI
        
        Generative AI refers to artificial intelligence systems that can create new content, including text, images, code, and more. These systems learn patterns from existing data and generate new outputs that reflect those patterns.
        
        Key generative AI technologies include:
        
        - Large Language Models (LLMs) like GPT-4 and PaLM
        - Text-to-image models like DALL-E and Stable Diffusion
        - Code generation tools like GitHub Copilot
        - Music and audio generation systems
        
        These technologies are transforming industries by automating creative tasks, enhancing productivity, and enabling new forms of expression.
        """
        
        # Define mission pillars
        self.mission_pillars = {
            "ResponsibleAI": {
                "description": "Ensuring AI systems are developed and deployed ethically, with consideration for fairness, transparency, accountability, and privacy.",
                "key_themes": ["Ethics", "Fairness", "Transparency", "Accountability", "Privacy", "Safety"],
                "integration_points": ["Ethical considerations", "Bias mitigation", "Transparency mechanisms", "Governance frameworks", "Privacy protections"]
            },
            "Sustainability": {
                "description": "Promoting environmentally sustainable AI practices and using AI to address sustainability challenges.",
                "key_themes": ["Environmental impact", "Energy efficiency", "Climate action", "Resource optimization", "Sustainable development"],
                "integration_points": ["Energy-efficient models", "Environmental applications", "Resource optimization", "Sustainable infrastructure", "Climate impact assessment"]
            },
            "Inclusion": {
                "description": "Ensuring AI benefits diverse populations and is accessible to all, with consideration for different backgrounds, abilities, and perspectives.",
                "key_themes": ["Accessibility", "Diversity", "Equity", "Cultural sensitivity", "Global perspectives", "Underrepresented groups"],
                "integration_points": ["Inclusive design", "Accessibility features", "Diverse representation", "Cultural considerations", "Global perspectives"]
            }
        }
        
        # Test integration points
        self.integration_points = [
            {
                "section": "Introduction to Generative AI",
                "integration_points": [
                    {
                        "pillar": "ResponsibleAI",
                        "theme": "Ethics",
                        "suggestion": "Add a paragraph discussing ethical considerations in generative AI, such as potential for misuse, copyright concerns, and authenticity issues."
                    },
                    {
                        "pillar": "Sustainability",
                        "theme": "Environmental impact",
                        "suggestion": "Add information about the environmental impact of training and running large generative AI models, including energy consumption and carbon footprint."
                    },
                    {
                        "pillar": "Inclusion",
                        "theme": "Accessibility",
                        "suggestion": "Highlight how generative AI can improve accessibility through text-to-speech, image description generation, and other assistive technologies."
                    }
                ]
            }
        ]
        
        # Test integrated content
        self.integrated_content = """
        # Introduction to Generative AI
        
        Generative AI refers to artificial intelligence systems that can create new content, including text, images, code, and more. These systems learn patterns from existing data and generate new outputs that reflect those patterns.
        
        Key generative AI technologies include:
        
        - Large Language Models (LLMs) like GPT-4 and PaLM
        - Text-to-image models like DALL-E and Stable Diffusion
        - Code generation tools like GitHub Copilot
        - Music and audio generation systems
        
        These technologies are transforming industries by automating creative tasks, enhancing productivity, and enabling new forms of expression.
        
        ## Ethical Considerations in Generative AI
        
        As generative AI becomes more powerful and widespread, several ethical considerations emerge:
        
        - **Misinformation and Deepfakes**: These technologies can create convincing but false content, raising concerns about misinformation and manipulation.
        - **Copyright and Ownership**: Questions about intellectual property rights arise when AI generates content based on existing works.
        - **Consent and Attribution**: Using artists' or writers' work to train generative models raises questions about consent and proper attribution.
        - **Bias and Representation**: Generative models can perpetuate or amplify biases present in their training data, affecting representation and fairness.
        
        Responsible development and deployment of generative AI requires addressing these ethical challenges through thoughtful policies, technical safeguards, and ongoing dialogue with stakeholders.
        
        ## Environmental Impact of Generative AI
        
        Training and running large generative AI models comes with significant environmental costs:
        
        - **Energy Consumption**: Training a single large language model can consume as much electricity as several hundred U.S. homes use in a year.
        - **Carbon Footprint**: Depending on the energy source, this electricity consumption translates to substantial carbon emissions.
        - **Computing Resources**: The demand for specialized hardware like GPUs and TPUs drives resource extraction and manufacturing impacts.
        
        The AI community is responding to these challenges through research into more efficient model architectures, carbon footprint reporting, and renewable energy commitments for data centers.
        
        ## Accessibility and Inclusion in Generative AI
        
        Generative AI has the potential to improve accessibility and inclusion in several ways:
        
        - **Text-to-Speech and Speech-to-Text**: Enabling better communication for people with hearing or speech impairments.
        - **Image Description Generation**: Automatically creating alt text for images to assist people with visual impairments.
        - **Language Translation**: Breaking down language barriers for global communication.
        - **Content Adaptation**: Tailoring content to different reading levels or learning styles.
        
        However, ensuring these benefits reach diverse populations requires intentional design, diverse training data, and ongoing testing with users from different backgrounds and abilities.
        """
        
        # Test pillar balance assessment
        self.pillar_balance = {
            "pillars_present": ["ResponsibleAI", "Sustainability", "Inclusion"],
            "pillar_coverage": {
                "ResponsibleAI": {
                    "present": True,
                    "sections": ["Ethical Considerations in Generative AI"],
                    "themes_covered": ["Ethics", "Fairness"],
                    "coverage_score": 0.33  # 2 of 6 themes covered
                },
                "Sustainability": {
                    "present": True,
                    "sections": ["Environmental Impact of Generative AI"],
                    "themes_covered": ["Environmental impact", "Energy efficiency"],
                    "coverage_score": 0.4  # 2 of 5 themes covered
                },
                "Inclusion": {
                    "present": True,
                    "sections": ["Accessibility and Inclusion in Generative AI"],
                    "themes_covered": ["Accessibility", "Diversity"],
                    "coverage_score": 0.33  # 2 of 6 themes covered
                }
            },
            "overall_balance": {
                "all_pillars_present": True,
                "average_coverage": 0.35,
                "recommendations": [
                    "Expand ResponsibleAI coverage to include Transparency, Accountability, Privacy, and Safety themes",
                    "Expand Sustainability coverage to include Climate action, Resource optimization, and Sustainable development themes",
                    "Expand Inclusion coverage to include Equity, Cultural sensitivity, Global perspectives, and Underrepresented groups themes"
                ]
            }
        }
        
        # Test impact metrics
        self.impact_metrics = {
            "ResponsibleAI": [
                {
                    "metric": "Fairness Assessment Score",
                    "description": "Measure of model performance across different demographic groups",
                    "measurement_method": "Statistical analysis of model outputs across protected attributes"
                },
                {
                    "metric": "Transparency Index",
                    "description": "Rating of how well the system explains its decisions and processes",
                    "measurement_method": "Expert evaluation using standardized rubric"
                }
            ],
            "Sustainability": [
                {
                    "metric": "Carbon Emissions per Training Run",
                    "description": "CO2 equivalent emissions from model training",
                    "measurement_method": "Energy consumption tracking with emissions conversion factors"
                },
                {
                    "metric": "Inference Energy Efficiency",
                    "description": "Energy used per inference request",
                    "measurement_method": "Direct measurement of power consumption during operation"
                }
            ],
            "Inclusion": [
                {
                    "metric": "Accessibility Compliance Score",
                    "description": "Degree of compliance with accessibility standards",
                    "measurement_method": "Automated and manual testing against WCAG guidelines"
                },
                {
                    "metric": "Language Support Coverage",
                    "description": "Percentage of target languages/dialects supported",
                    "measurement_method": "Inventory of supported languages compared to target demographics"
                }
            ]
        }
    
    @patch('cloud_function.mission_pillar.identify_integration_points')
    @patch('cloud_function.mission_pillar.firestore.Client')
    def test_identify_integration_points(self, mock_firestore, mock_identify):
        """Test the identification of mission pillar integration points."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'content': {
                'sections': {
                    'introduction': self.content_section
                }
            },
            'metadata': {
                'mission_pillars': ['ResponsibleAI', 'Sustainability', 'Inclusion']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the identify_integration_points function
        mock_identify.return_value = self.integration_points
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.get_json.return_value = {
            'content_id': self.content_id,
            'section_id': 'introduction'
        }
        
        # Act
        from cloud_function.mission_pillar import identify_section_integration_points
        response = identify_section_integration_points(mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['integration_points']), 1)
        self.assertEqual(len(response_data['integration_points'][0]['integration_points']), 3)
        
        # Verify Firestore queries
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with(self.content_id)
        
        # Verify identify_integration_points was called with correct parameters
        mock_identify.assert_called_once_with(
            content=self.content_section,
            mission_pillars=['ResponsibleAI', 'Sustainability', 'Inclusion']
        )
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('mission_pillar_integration.sections.introduction', update_args)
        
        return response_data['integration_points']
    
    @patch('cloud_function.mission_pillar.generate_integrated_content')
    @patch('cloud_function.mission_pillar.firestore.Client')
    def test_generate_integrated_content(self, mock_firestore, mock_generate):
        """Test the generation of content with integrated mission pillars."""
        # Arrange
        integration_points = self.test_identify_integration_points()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'content': {
                'sections': {
                    'introduction': self.content_section
                }
            },
            'mission_pillar_integration': {
                'sections': {
                    'introduction': integration_points
                }
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the generate_integrated_content function
        mock_generate.return_value = self.integrated_content
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.get_json.return_value = {
            'content_id': self.content_id,
            'section_id': 'introduction'
        }
        
        # Act
        from cloud_function.mission_pillar import generate_section_with_pillars
        response = generate_section_with_pillars(mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('integrated_content', response_data)
        
        # Verify Firestore queries
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with(self.content_id)
        
        # Verify generate_integrated_content was called with correct parameters
        mock_generate.assert_called_once_with(
            content=self.content_section,
            integration_points=integration_points[0]['integration_points']
        )
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('content.sections.introduction', update_args)
        
        return response_data['integrated_content']
    
    @patch('cloud_function.mission_pillar.check_pillar_balance')
    @patch('cloud_function.mission_pillar.firestore.Client')
    def test_check_pillar_balance(self, mock_firestore, mock_check_balance):
        """Test checking the balance of mission pillars in content."""
        # Arrange
        integrated_content = self.test_generate_integrated_content()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'content': {
                'sections': {
                    'introduction': integrated_content
                }
            },
            'metadata': {
                'mission_pillars': ['ResponsibleAI', 'Sustainability', 'Inclusion']
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the check_pillar_balance function
        mock_check_balance.return_value = self.pillar_balance
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.get_json.return_value = {
            'content_id': self.content_id
        }
        
        # Act
        from cloud_function.mission_pillar import check_content_pillar_balance
        response = check_content_pillar_balance(mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('pillar_balance', response_data)
        self.assertTrue(response_data['pillar_balance']['overall_balance']['all_pillars_present'])
        
        # Verify Firestore queries
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with(self.content_id)
        
        # Verify check_pillar_balance was called with correct parameters
        all_content = "\n".join([integrated_content])
        mock_check_balance.assert_called_once_with(
            content=all_content,
            mission_pillars=['ResponsibleAI', 'Sustainability', 'Inclusion']
        )
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('mission_pillar_integration.balance', update_args)
        
        return response_data['pillar_balance']
    
    @patch('cloud_function.mission_pillar.suggest_impact_metrics')
    @patch('cloud_function.mission_pillar.firestore.Client')
    def test_suggest_impact_metrics(self, mock_firestore, mock_suggest_metrics):
        """Test suggesting metrics for mission-related outcomes."""
        # Arrange
        pillar_balance = self.test_check_pillar_balance()
        
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock the Firestore get response
        mock_content_data = {
            'metadata': {
                'type': 'LearningModule',
                'mission_pillars': ['ResponsibleAI', 'Sustainability', 'Inclusion']
            },
            'mission_pillar_integration': {
                'balance': pillar_balance
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock the suggest_impact_metrics function
        mock_suggest_metrics.return_value = self.impact_metrics
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.get_json.return_value = {
            'content_id': self.content_id
        }
        
        # Act
        from cloud_function.mission_pillar import suggest_mission_impact_metrics
        response = suggest_mission_impact_metrics(mock_request)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('impact_metrics', response_data)
        self.assertIn('ResponsibleAI', response_data['impact_metrics'])
        self.assertIn('Sustainability', response_data['impact_metrics'])
        self.assertIn('Inclusion', response_data['impact_metrics'])
        
        # Verify Firestore queries
        mock_db.collection.assert_called_with('content-items')
        mock_db.collection().document.assert_called_with(self.content_id)
        
        # Verify suggest_impact_metrics was called with correct parameters
        mock_suggest_metrics.assert_called_once_with(
            content_type='LearningModule',
            mission_pillars=['ResponsibleAI', 'Sustainability', 'Inclusion']
        )
        
        # Verify Firestore update
        mock_content_ref.update.assert_called_once()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertIn('mission_pillar_integration.impact_metrics', update_args)
    
    def test_end_to_end_mission_pillar_integration_workflow(self):
        """Test the end-to-end mission pillar integration workflow."""
        # This test calls the other test methods in sequence to simulate the workflow
        self.test_suggest_impact_metrics()

if __name__ == '__main__':
    unittest.main()
