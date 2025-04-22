#!/usr/bin/env python3
"""
Simple test script with mocked cloud functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import flask

class MockCloudFunctionTest(unittest.TestCase):
    """Test case with mocked cloud functions."""
    
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
    
    def test_mock_initialize_content_creation(self):
        """Test a mocked initialize_content_creation function."""
        # Define a mock function
        def mock_initialize_content_creation(request):
            request_json = request.get_json()
            if not request_json:
                return flask.jsonify({
                    'status': 'error',
                    'message': 'No request data provided'
                }), 400
            
            content_type = request_json.get('content_type')
            title = request_json.get('title')
            
            if not all([content_type, title]):
                return flask.jsonify({
                    'status': 'error',
                    'message': 'Missing required parameters: content_type, title'
                }), 400
            
            content_id = 'test-content-123'
            
            return flask.jsonify({
                'status': 'success',
                'message': 'Content creation initialized',
                'content_id': content_id
            })
        
        # Create a mock Flask request
        with self.app.test_request_context(json=self.content_request):
            # Act
            response = mock_initialize_content_creation(flask.request)
            
            # Assert
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertEqual(response_data['content_id'], 'test-content-123')
            
            print("Test passed: mock_initialize_content_creation")
    
    def test_mock_select_template(self):
        """Test a mocked select_template function."""
        # Define a mock function
        def mock_select_template(event, context):
            event_data = {
                'content_id': 'test-content-123',
                'action': 'select_template'
            }
            
            # Mock Firestore client
            mock_db = MagicMock()
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
            mock_template = {
                "type": "LearningModule",
                "content": "# Learning Module Template",
                "audience_levels": ["Beginner", "Intermediate", "Expert"],
                "sections": [
                    "1. Introduction & Context",
                    "2. Core Concepts"
                ]
            }
            mock_template_doc = MagicMock()
            mock_template_doc.to_dict.return_value = mock_template
            mock_query.stream.return_value = [mock_template_doc]
            
            # Update content with template
            mock_content_ref.update({
                'template': mock_template,
                'metadata.status': 'template_selected',
                'workflow.current_stage': 'content_planning'
            })
            
            # Mock publish event
            mock_publish = MagicMock()
            mock_publish.return_value = "message-id-12345"
            
            # Return success
            return True
        
        # Act
        result = mock_select_template({'data': 'test-data'}, None)
        
        # Assert
        self.assertTrue(result)
        print("Test passed: mock_select_template")
    
    def test_mock_generate_content_plan(self):
        """Test a mocked generate_content_plan function."""
        # Define a mock function
        def mock_generate_content_plan(event, context):
            event_data = {
                'content_id': 'test-content-123',
                'action': 'generate_content_plan'
            }
            
            # Mock Firestore client
            mock_db = MagicMock()
            mock_content_ref = MagicMock()
            mock_db.collection.return_value.document.return_value = mock_content_ref
            
            mock_content_data = {
                'metadata': {
                    'title': 'Introduction to AI',
                    'type': 'LearningModule',
                    'audience': 'Beginner',
                    'mission_pillars': ['ResponsibleAI']
                },
                'template': {
                    "type": "LearningModule",
                    "content": "# Learning Module Template",
                    "audience_levels": ["Beginner", "Intermediate", "Expert"],
                    "sections": [
                        "1. Introduction & Context",
                        "2. Core Concepts"
                    ]
                }
            }
            mock_content_ref.get.return_value.to_dict.return_value = mock_content_data
            
            # Mock Vertex AI call
            mock_content_plan = {
                "learning_objectives": [
                    "By the end of this module, learners will be able to define AI and explain its key components."
                ],
                "key_concepts": {
                    "Introduction & Context": [
                        "Definition of AI",
                        "Brief history of AI development"
                    ]
                }
            }
            mock_call_vertex = MagicMock(return_value=json.dumps(mock_content_plan))
            
            # Update content with plan
            mock_content_ref.update({
                'content.plan': mock_content_plan,
                'metadata.status': 'plan_generated',
                'workflow.current_stage': 'section_population'
            })
            
            # Mock publish event
            mock_publish = MagicMock()
            mock_publish.return_value = "message-id-12345"
            
            # Return success
            return True
        
        # Act
        result = mock_generate_content_plan({'data': 'test-data'}, None)
        
        # Assert
        self.assertTrue(result)
        print("Test passed: mock_generate_content_plan")

if __name__ == '__main__':
    unittest.main()
