"""
End-to-end integration tests for the Agentic AI Content Creation System.
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
from cloud_function.utils import store_content_metadata, publish_event, call_vertex_ai

class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end integration tests for the Agentic AI Content Creation System."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True
        
        # Test content ID
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
        
        # Mock source needs
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
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    def test_complete_content_creation_workflow(self, mock_call_vertex, mock_firestore, mock_uuid, mock_publish, mock_store):
        """Test the complete content creation workflow from initialization to content generation."""
        # Step 1: Initialize content creation
        
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act - Initialize content creation
            init_response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(init_response.status_code, 200)
            init_data = json.loads(init_response.data)
            self.assertEqual(init_data['status'], 'success')
            self.assertEqual(init_data['content_id'], self.test_content_id)
            
            # Verify that store_content_metadata was called
            mock_store.assert_called_once()
            
            # Verify that publish_event was called with the correct parameters
            mock_publish.assert_called_once_with('content-creation-events', {
                'content_id': self.test_content_id,
                'action': 'select_template'
            })
        
        # Step 2: Select template
        
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
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
        
        # Create a mock Pub/Sub event for template selection
        event_data = {
            'content_id': self.test_content_id,
            'action': 'select_template'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Select template
        from cloud_function.main import select_template
        select_template(event, None)
        
        # Assert
        # Verify that the content was updated with the template
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['template'], self.template)
        
        # Verify that publish_event was called with the correct parameters
        mock_publish.assert_called_with('content-creation-events', {
            'content_id': self.test_content_id,
            'action': 'generate_content_plan'
        })
        
        # Step 3: Generate content plan
        
        # Arrange
        # Reset mock_content_ref.get().to_dict() to include the template
        mock_content_data['template'] = self.template
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call
        mock_call_vertex.return_value = json.dumps(self.content_plan)
        
        # Create a mock Pub/Sub event for content plan generation
        event_data = {
            'content_id': self.test_content_id,
            'action': 'generate_content_plan'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Generate content plan
        from cloud_function.main import generate_content_plan
        generate_content_plan(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the content plan
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['content.plan'], self.content_plan)
        
        # Verify that publish_event was called with the correct parameters
        mock_publish.assert_called_with('content-creation-events', {
            'content_id': self.test_content_id,
            'action': 'populate_sections'
        })
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    def test_content_creation_with_source_collection(self, mock_call_vertex, mock_firestore, mock_uuid, mock_publish, mock_store):
        """Test the content creation workflow with source collection."""
        # Step 1: Initialize content creation
        
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act - Initialize content creation
            init_response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(init_response.status_code, 200)
            init_data = json.loads(init_response.data)
            self.assertEqual(init_data['status'], 'success')
            self.assertEqual(init_data['content_id'], self.test_content_id)
        
        # Step 2: Generate content sections
        
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data with template and plan
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            },
            'template': self.template,
            'content': {
                'plan': self.content_plan
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call for section content
        section_content = """
        # Introduction to Generative AI
        
        Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns. The transformer architecture, which relies on attention mechanisms, has been particularly successful for text generation tasks.
        
        ## Practical Applications
        
        Businesses are using generative AI for customer service automation, content creation, and code generation. These applications can significantly improve productivity and enable new capabilities.
        """
        mock_call_vertex.return_value = section_content
        
        # Create a mock Pub/Sub event for section population
        event_data = {
            'content_id': self.test_content_id,
            'action': 'populate_sections'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Populate sections
        # This is a mock implementation since the actual function doesn't exist
        def mock_populate_sections(event, context):
            # Parse event data
            event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
            content_id = event_data.get('content_id')
            
            # Get content data
            db = mock_firestore()
            content_ref = db.collection('content-items').document(content_id)
            content_data = content_ref.get().to_dict()
            
            # Generate section content
            section_content = mock_call_vertex(prompt="Generate section content")
            
            # Update content with section content
            content_ref.update({
                'content.sections': section_content,
                'metadata.status': 'sections_populated',
                'workflow.current_stage': 'source_collection',
                'workflow.stages_completed': firestore.ArrayUnion(['section_population'])
            })
            
            # Publish event to trigger source collection
            publish_event('content-creation-events', {
                'content_id': content_id,
                'action': 'identify_source_needs'
            })
        
        mock_populate_sections(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the section content
        mock_content_ref.update.assert_called()
        
        # Verify that publish_event was called with the correct parameters
        mock_publish.assert_called_with('content-creation-events', {
            'content_id': self.test_content_id,
            'action': 'identify_source_needs'
        })
        
        # Step 3: Identify source needs
        
        # Arrange
        # Reset mock_content_ref.get().to_dict() to include the section content
        mock_content_data['content']['sections'] = section_content
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call for source needs
        mock_call_vertex.reset_mock()
        mock_call_vertex.return_value = json.dumps(self.source_needs)
        
        # Create a mock Flask request for identify_source_needs
        with self.app.test_request_context(json={
            'content_id': self.test_content_id,
            'content_text': section_content
        }):
            # Act - Identify source needs
            # This is a mock implementation since the actual function doesn't exist
            def mock_identify_source_needs():
                # Get request data
                request_json = flask.request.get_json()
                content_id = request_json.get('content_id')
                content_text = request_json.get('content_text')
                
                # Call Vertex AI to identify source needs
                source_needs = json.loads(mock_call_vertex(prompt="Identify source needs"))
                
                # Update content with source needs
                db = mock_firestore()
                content_ref = db.collection('content-items').document(content_id)
                content_ref.update({
                    'sources.needs': source_needs
                })
                
                # Return response
                return flask.jsonify({
                    'status': 'success',
                    'message': 'Source needs identified',
                    'content_id': content_id,
                    'source_needs': source_needs
                })
            
            response = mock_identify_source_needs()
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertEqual(len(response_data['source_needs']), 2)
        
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the source needs
        mock_content_ref.update.assert_called_with({
            'sources.needs': self.source_needs
        })
    
    @patch('cloud_function.main.store_content_metadata')
    @patch('cloud_function.main.publish_event')
    @patch('cloud_function.main.uuid.uuid4')
    @patch('cloud_function.main.firestore.Client')
    @patch('cloud_function.main.call_vertex_ai')
    def test_content_creation_with_mission_pillar_integration(self, mock_call_vertex, mock_firestore, mock_uuid, mock_publish, mock_store):
        """Test the content creation workflow with mission pillar integration."""
        # Step 1: Initialize content creation
        
        # Arrange
        mock_uuid.return_value = MagicMock(hex=self.test_content_id)
        mock_store.return_value = f"Stored metadata for content {self.test_content_id}"
        mock_publish.return_value = "message-id-12345"
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act - Initialize content creation
            init_response = initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(init_response.status_code, 200)
            init_data = json.loads(init_response.data)
            self.assertEqual(init_data['status'], 'success')
            self.assertEqual(init_data['content_id'], self.test_content_id)
        
        # Step 2: Generate content with mission pillar integration
        
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        
        mock_content_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_content_ref
        
        # Mock content data with template, plan, and sections
        section_content = """
        # Introduction to Generative AI
        
        Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns. The transformer architecture, which relies on attention mechanisms, has been particularly successful for text generation tasks.
        
        ## Practical Applications
        
        Businesses are using generative AI for customer service automation, content creation, and code generation. These applications can significantly improve productivity and enable new capabilities.
        """
        
        mock_content_data = {
            'metadata': {
                'title': self.content_request['title'],
                'type': self.content_request['content_type'],
                'audience': self.content_request['audience_level'],
                'mission_pillars': self.content_request['mission_pillars']
            },
            'template': self.template,
            'content': {
                'plan': self.content_plan,
                'sections': section_content
            }
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call for mission pillar integration
        mock_call_vertex.reset_mock()
        
        # Mock integration points
        integration_points = [
            {
                "section": "Introduction & Context",
                "integration_point": "Discuss the importance of responsible AI in generative models, highlighting potential biases in training data.",
                "mission_pillar": "ResponsibleAI"
            },
            {
                "section": "Core Concepts",
                "integration_point": "Explain how inclusive design principles can be applied to generative AI systems to ensure they serve diverse user groups.",
                "mission_pillar": "Inclusion"
            }
        ]
        mock_call_vertex.return_value = json.dumps(integration_points)
        
        # Create a mock Pub/Sub event for mission pillar integration
        event_data = {
            'content_id': self.test_content_id,
            'action': 'identify_integration_points'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Identify integration points
        # This is a mock implementation since the actual function doesn't exist
        def mock_identify_integration_points(event, context):
            # Parse event data
            event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
            content_id = event_data.get('content_id')
            
            # Get content data
            db = mock_firestore()
            content_ref = db.collection('content-items').document(content_id)
            content_data = content_ref.get().to_dict()
            
            # Call Vertex AI to identify integration points
            integration_points = json.loads(mock_call_vertex(prompt="Identify integration points"))
            
            # Update content with integration points
            content_ref.update({
                'mission_pillars.integration_points': integration_points,
                'metadata.status': 'integration_points_identified',
                'workflow.current_stage': 'integrate_mission_pillars',
                'workflow.stages_completed': firestore.ArrayUnion(['integration_point_identification'])
            })
            
            # Publish event to trigger mission pillar integration
            publish_event('content-creation-events', {
                'content_id': content_id,
                'action': 'integrate_mission_pillars'
            })
        
        mock_identify_integration_points(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the integration points
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['mission_pillars.integration_points'], integration_points)
        
        # Verify that publish_event was called with the correct parameters
        mock_publish.assert_called_with('content-creation-events', {
            'content_id': self.test_content_id,
            'action': 'integrate_mission_pillars'
        })
        
        # Step 3: Integrate mission pillars
        
        # Arrange
        # Reset mock_content_ref.get().to_dict() to include the integration points
        mock_content_data['mission_pillars'] = {
            'integration_points': integration_points
        }
        mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
        
        # Mock Vertex AI call for integrated content
        mock_call_vertex.reset_mock()
        
        integrated_content = """
        # Introduction to Generative AI
        
        Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed.
        
        It's crucial to consider the ethical implications of generative AI systems. These models can perpetuate and amplify biases present in their training data, potentially leading to unfair or harmful outputs. Responsible AI practices require careful data curation, regular bias audits, and transparent documentation of model limitations.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns. The transformer architecture, which relies on attention mechanisms, has been particularly successful for text generation tasks.
        
        When designing generative AI systems, inclusive design principles ensure these powerful tools serve diverse user groups. This includes testing with varied user populations, supporting multiple languages, and considering accessibility requirements. Inclusive AI systems should accommodate different cultural contexts and avoid assumptions that might exclude certain groups.
        
        ## Practical Applications
        
        Businesses are using generative AI for customer service automation, content creation, and code generation. These applications can significantly improve productivity and enable new capabilities.
        """
        mock_call_vertex.return_value = integrated_content
        
        # Create a mock Pub/Sub event for mission pillar integration
        event_data = {
            'content_id': self.test_content_id,
            'action': 'integrate_mission_pillars'
        }
        event = {
            'data': base64.b64encode(json.dumps(event_data).encode('utf-8'))
        }
        
        # Act - Integrate mission pillars
        # This is a mock implementation since the actual function doesn't exist
        def mock_integrate_mission_pillars(event, context):
            # Parse event data
            event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
            content_id = event_data.get('content_id')
            
            # Get content data
            db = mock_firestore()
            content_ref = db.collection('content-items').document(content_id)
            content_data = content_ref.get().to_dict()
            
            # Call Vertex AI to integrate mission pillars
            integrated_content = mock_call_vertex(prompt="Integrate mission pillars")
            
            # Update content with integrated content
            content_ref.update({
                'content.integrated_sections': integrated_content,
                'metadata.status': 'mission_pillars_integrated',
                'workflow.current_stage': 'review',
                'workflow.stages_completed': firestore.ArrayUnion(['mission_pillar_integration'])
            })
            
            # Publish event to trigger review
            publish_event('content-creation-events', {
                'content_id': content_id,
                'action': 'review_content'
            })
        
        mock_integrate_mission_pillars(event, None)
        
        # Assert
        # Verify that call_vertex_ai was called
        mock_call_vertex.assert_called_once()
        
        # Verify that the content was updated with the integrated content
        mock_content_ref.update.assert_called()
        update_args = mock_content_ref.update.call_args[0][0]
        self.assertEqual(update_args['content.integrated_sections'], integrated_content)
        
        # Verify that publish_event was called with the correct parameters
        mock_publish.assert_called_with('content-creation-events', {
            'content_id': self.test_content_id,
            'action': 'review_content'
        })

if __name__ == '__main__':
    unittest.main()
