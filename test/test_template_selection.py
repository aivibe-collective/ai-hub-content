"""
Test cases for the Template Selection component.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module under test
from cloud_function.utils import get_template

# Import test configuration
from test.config import ContentTypes, AudienceLevels, TEST_DATA_DIR, CONTENT_PLANS_DIR, TEMPLATES_DIR

class TestTemplateSelection(unittest.TestCase):
    """Test cases for the Template Selection component."""

    def setUp(self):
        """Set up test fixtures."""
        # Load test content plans
        self.content_plans = {}
        for filename in os.listdir(CONTENT_PLANS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(CONTENT_PLANS_DIR, filename), 'r') as f:
                    plan = json.load(f)
                    self.content_plans[plan['id']] = plan

        # Load test templates
        self.templates = {}
        for filename in os.listdir(TEMPLATES_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(TEMPLATES_DIR, filename), 'r') as f:
                    template = json.load(f)
                    self.templates[template['type']] = template

    @patch('cloud_function.utils.firestore.Client')
    def test_valid_template_selection(self, mock_firestore):
        """TC1.1 - Valid Template: Given a content plan, the system recommends a valid template."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Set up the mock to return a template for LearningModule
        mock_template = MagicMock()
        mock_template.to_dict.return_value = self.templates.get(ContentTypes.LEARNING_MODULE)
        mock_query.stream.return_value = [mock_template]

        # Act
        plan = self.content_plans.get('plan_learning_beginner')
        result = get_template(plan['content_type'], plan['audience_level'])

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], ContentTypes.LEARNING_MODULE)
        mock_db.collection.assert_called_once()
        mock_db.collection().where.assert_called_once_with('type', '==', ContentTypes.LEARNING_MODULE)
        mock_query.where.assert_called_once_with('audience_levels', 'array_contains', AudienceLevels.BEGINNER)

    @patch('cloud_function.utils.firestore.Client')
    def test_invalid_template_selection(self, mock_firestore):
        """TC1.2 - Invalid Template: Given a content plan, the system does not recommend an incorrect template."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Set up the mock to return a template for BlogPost
        mock_template = MagicMock()
        mock_template.to_dict.return_value = self.templates.get(ContentTypes.BLOG_POST)
        mock_query.stream.return_value = [mock_template]

        # Act
        plan = self.content_plans.get('plan_case_study')
        result = get_template(plan['content_type'], plan['audience_level'])

        # Assert
        self.assertIsNotNone(result)
        self.assertNotEqual(result['type'], ContentTypes.CASE_STUDY)
        mock_db.collection.assert_called_once()
        mock_db.collection().where.assert_called_once_with('type', '==', ContentTypes.CASE_STUDY)

    @patch('cloud_function.utils.firestore.Client')
    def test_no_template_found(self, mock_firestore):
        """TC1.3 - No Template: Given a content plan, the system fails if no template is found."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Set up the mock to return no templates
        mock_query.stream.return_value = []

        # Act
        plan = self.content_plans.get('plan_invalid')
        result = get_template(plan['content_type'], plan['audience_level'])

        # Assert
        self.assertIsNone(result)
        mock_db.collection.assert_called_once()
        mock_db.collection().where.assert_called_once_with('type', '==', 'InvalidType')

    @patch('cloud_function.utils.firestore.Client')
    def test_firestore_error(self, mock_firestore):
        """Test handling of Firestore errors."""
        # Arrange
        mock_firestore.side_effect = Exception("Firestore connection error")

        # Act & Assert
        plan = self.content_plans.get('plan_learning_beginner')
        with self.assertRaises(Exception):
            get_template(plan['content_type'], plan['audience_level'])

    @patch('cloud_function.utils.firestore.Client')
    def test_empty_content_plan(self, mock_firestore):
        """Test handling of empty content plan."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Set up the mock to return no templates
        mock_query.stream.return_value = []

        # Act
        plan = self.content_plans.get('plan_empty')
        result = get_template(plan['content_type'], plan['audience_level'])

        # Assert
        self.assertIsNone(result)
        mock_db.collection.assert_called_once()

    @patch('cloud_function.utils.firestore.Client')
    def test_audience_level_filtering(self, mock_firestore):
        """Test that templates are filtered by audience level."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Set up the mock to return a template for LearningModule
        mock_template = MagicMock()
        mock_template.to_dict.return_value = self.templates.get(ContentTypes.LEARNING_MODULE)
        mock_query.stream.return_value = [mock_template]

        # Act
        result = get_template(ContentTypes.LEARNING_MODULE, AudienceLevels.EXPERT)

        # Assert
        self.assertIsNotNone(result)
        mock_db.collection.assert_called_once()
        mock_db.collection().where.assert_called_once_with('type', '==', ContentTypes.LEARNING_MODULE)
        mock_query.where.assert_called_once_with('audience_levels', 'array_contains', AudienceLevels.EXPERT)

    @patch('cloud_function.utils.firestore.Client')
    def test_no_audience_level(self, mock_firestore):
        """Test that templates can be retrieved without an audience level."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_query = MagicMock()
        mock_db.collection.return_value.where.return_value = mock_query

        # Set up the mock to return a template for BlogPost
        mock_template = MagicMock()
        mock_template.to_dict.return_value = self.templates.get(ContentTypes.BLOG_POST)
        mock_query.stream.return_value = [mock_template]

        # Act
        result = get_template(ContentTypes.BLOG_POST, None)

        # Assert
        self.assertIsNotNone(result)
        mock_db.collection.assert_called_once()
        mock_db.collection().where.assert_called_once_with('type', '==', ContentTypes.BLOG_POST)
        # Should not call where again for audience level
        mock_query.where.assert_not_called()

if __name__ == '__main__':
    unittest.main()
