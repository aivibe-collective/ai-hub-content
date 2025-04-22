"""
Unit tests for cloud_function/utils.py
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules under test
from cloud_function.utils import (
    store_content_metadata,
    publish_event,
    call_vertex_ai,
    upload_content_to_storage,
    download_content_from_storage,
    get_template_by_id,
    get_content_by_id
)

class TestCloudFunctionUtils(unittest.TestCase):
    """Unit tests for the cloud function utility functions."""

    @patch('cloud_function.utils.firestore.Client')
    def test_store_content_metadata_success(self, mock_firestore):
        """Test store_content_metadata function with successful storage."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        content_id = "test-content-123"
        metadata = {
            "metadata": {
                "title": "Test Content",
                "type": "LearningModule"
            }
        }

        # Act
        result = store_content_metadata(content_id, metadata)

        # Assert
        mock_db.collection.assert_called_once_with('content-items')
        mock_db.collection().document.assert_called_once_with(content_id)
        mock_doc_ref.set.assert_called_once_with(metadata, merge=True)
        self.assertEqual(result, f"Stored metadata for content {content_id}")

    @patch('cloud_function.utils.firestore.Client')
    def test_store_content_metadata_error(self, mock_firestore):
        """Test store_content_metadata function with a Firestore error."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_doc_ref.set.side_effect = Exception("Firestore connection error")

        content_id = "test-content-123"
        metadata = {
            "metadata": {
                "title": "Test Content",
                "type": "LearningModule"
            }
        }

        # Act and Assert
        with self.assertRaises(Exception) as context:
            store_content_metadata(content_id, metadata)

        self.assertIn("Firestore connection error", str(context.exception))

    @patch('cloud_function.utils.pubsub_v1.PublisherClient')
    def test_publish_event_success(self, mock_publisher):
        """Test publish_event function with successful publishing."""
        # Arrange
        mock_client = MagicMock()
        mock_publisher.return_value = mock_client
        mock_client.publish.return_value.result.return_value = "message-id-12345"

        topic_name = "test-topic"
        event_data = {
            "content_id": "test-content-123",
            "action": "test_action"
        }

        # Act
        result = publish_event(topic_name, event_data)

        # Assert
        mock_client.topic_path.assert_called_once()
        mock_client.publish.assert_called_once()
        publish_args = mock_client.publish.call_args[0]
        self.assertEqual(publish_args[1], json.dumps(event_data).encode('utf-8'))
        self.assertEqual(result, "message-id-12345")

    @patch('cloud_function.utils.pubsub_v1.PublisherClient')
    def test_publish_event_error(self, mock_publisher):
        """Test publish_event function with a publishing error."""
        # Arrange
        mock_client = MagicMock()
        mock_publisher.return_value = mock_client
        mock_client.publish.return_value.result.side_effect = Exception("Pub/Sub connection error")

        topic_name = "test-topic"
        event_data = {
            "content_id": "test-content-123",
            "action": "test_action"
        }

        # Act and Assert
        with self.assertRaises(Exception) as context:
            publish_event(topic_name, event_data)

        self.assertIn("Pub/Sub connection error", str(context.exception))

    @patch('cloud_function.utils.vertexai.init')
    @patch('cloud_function.utils.TextGenerationModel.from_pretrained')
    def test_call_vertex_ai_success(self, mock_model_from_pretrained, mock_vertexai_init):
        """Test call_vertex_ai function with successful API call."""
        # Arrange
        mock_model = MagicMock()
        mock_model_from_pretrained.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = '{"key": "value"}'
        mock_model.predict.return_value = mock_response

        prompt = "Generate a content plan for Introduction to AI"

        # Act
        result = call_vertex_ai(prompt)

        # Assert
        mock_vertexai_init.assert_called_once()
        mock_model_from_pretrained.assert_called_once()
        mock_model.predict.assert_called_once_with(prompt=prompt, temperature=0.2, max_output_tokens=1024, top_k=40, top_p=0.8)
        self.assertEqual(result, '{"key": "value"}')

    @patch('cloud_function.utils.vertexai.init')
    @patch('cloud_function.utils.TextGenerationModel.from_pretrained')
    def test_call_vertex_ai_error(self, mock_model_from_pretrained, mock_vertexai_init):
        """Test call_vertex_ai function with an API error."""
        # Arrange
        mock_model = MagicMock()
        mock_model_from_pretrained.return_value = mock_model
        mock_model.predict.side_effect = Exception("Vertex AI API error")

        prompt = "Generate a content plan for Introduction to AI"

        # Act and Assert
        with self.assertRaises(Exception) as context:
            call_vertex_ai(prompt)

        self.assertIn("Vertex AI API error", str(context.exception))

    @patch('cloud_function.utils.vertexai.init')
    @patch('cloud_function.utils.TextGenerationModel.from_pretrained')
    def test_call_vertex_ai_non_json_response(self, mock_model_from_pretrained, mock_vertexai_init):
        """Test call_vertex_ai function with a non-JSON response."""
        # Arrange
        mock_model = MagicMock()
        mock_model_from_pretrained.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_model.predict.return_value = mock_response

        prompt = "Generate a content plan for Introduction to AI"

        # Act
        result = call_vertex_ai(prompt)

        # Assert
        self.assertEqual(result, "This is not valid JSON")

    @patch('cloud_function.utils.storage.Client')
    def test_upload_content_to_storage_success(self, mock_storage):
        """Test upload_content_to_storage with valid input."""
        # Arrange
        mock_client = MagicMock()
        mock_storage.return_value = mock_client

        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        content_id = "test-content-123"
        content_text = "Test content text"
        bucket_name = "content-bucket"

        # Act
        result = upload_content_to_storage(content_id, content_text, bucket_name)

        # Assert
        mock_client.bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(f"content/{content_id}.md")
        mock_blob.upload_from_string.assert_called_once_with(content_text)
        self.assertEqual(result, f"gs://{bucket_name}/content/{content_id}.md")

    @patch('cloud_function.utils.storage.Client')
    def test_upload_content_to_storage_error(self, mock_storage):
        """Test upload_content_to_storage with a storage error."""
        # Arrange
        mock_client = MagicMock()
        mock_storage.return_value = mock_client

        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Mock storage error
        mock_blob.upload_from_string.side_effect = Exception("Storage error")

        content_id = "test-content-123"
        content_text = "Test content text"
        bucket_name = "content-bucket"

        # Act and Assert
        with self.assertRaises(Exception) as context:
            upload_content_to_storage(content_id, content_text, bucket_name)

        self.assertIn("Storage error", str(context.exception))

    @patch('cloud_function.utils.storage.Client')
    def test_download_content_from_storage_success(self, mock_storage):
        """Test download_content_from_storage with valid input."""
        # Arrange
        mock_client = MagicMock()
        mock_storage.return_value = mock_client

        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Mock download response
        mock_blob.download_as_text.return_value = "Downloaded content text"

        content_id = "test-content-123"
        bucket_name = "content-bucket"

        # Act
        result = download_content_from_storage(content_id, bucket_name)

        # Assert
        mock_client.bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(f"content/{content_id}.md")
        mock_blob.download_as_text.assert_called_once()
        self.assertEqual(result, "Downloaded content text")

    @patch('cloud_function.utils.storage.Client')
    def test_download_content_from_storage_error(self, mock_storage):
        """Test download_content_from_storage with a storage error."""
        # Arrange
        mock_client = MagicMock()
        mock_storage.return_value = mock_client

        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        # Mock storage error
        mock_blob.download_as_text.side_effect = Exception("Storage error")

        content_id = "test-content-123"
        bucket_name = "content-bucket"

        # Act and Assert
        with self.assertRaises(Exception) as context:
            download_content_from_storage(content_id, bucket_name)

        self.assertIn("Storage error", str(context.exception))

    @patch('cloud_function.utils.firestore.Client')
    def test_get_template_by_id_success(self, mock_firestore):
        """Test get_template_by_id with valid input."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        # Mock document snapshot
        mock_snapshot = MagicMock()
        mock_doc_ref.get.return_value = mock_snapshot

        # Mock template data
        template_data = {
            "type": "LearningModule",
            "content": "# Learning Module Template",
            "audience_levels": ["Beginner", "Intermediate", "Expert"],
            "sections": [
                "1. Introduction & Context",
                "2. Core Concepts"
            ]
        }
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = template_data

        template_id = "template-123"

        # Act
        result = get_template_by_id(template_id)

        # Assert
        mock_db.collection.assert_called_once_with('templates')
        mock_db.collection.return_value.document.assert_called_once_with(template_id)
        mock_doc_ref.get.assert_called_once()
        self.assertEqual(result, template_data)

    @patch('cloud_function.utils.firestore.Client')
    def test_get_template_by_id_not_found(self, mock_firestore):
        """Test get_template_by_id with a non-existent template."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        # Mock document snapshot
        mock_snapshot = MagicMock()
        mock_doc_ref.get.return_value = mock_snapshot

        # Mock non-existent template
        mock_snapshot.exists = False

        template_id = "nonexistent-template"

        # Act and Assert
        with self.assertRaises(ValueError) as context:
            get_template_by_id(template_id)

        self.assertIn(f"Template {template_id} not found", str(context.exception))

    @patch('cloud_function.utils.firestore.Client')
    def test_get_content_by_id_success(self, mock_firestore):
        """Test get_content_by_id with valid input."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        # Mock document snapshot
        mock_snapshot = MagicMock()
        mock_doc_ref.get.return_value = mock_snapshot

        # Mock content data
        content_data = {
            "metadata": {
                "title": "Test Content",
                "type": "LearningModule",
                "audience": "Beginner",
                "mission_pillars": ["ResponsibleAI"]
            },
            "template": {
                "type": "LearningModule",
                "content": "# Learning Module Template",
                "audience_levels": ["Beginner", "Intermediate", "Expert"],
                "sections": [
                    "1. Introduction & Context",
                    "2. Core Concepts"
                ]
            }
        }
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = content_data

        content_id = "test-content-123"

        # Act
        result = get_content_by_id(content_id)

        # Assert
        mock_db.collection.assert_called_once_with('content-items')
        mock_db.collection.return_value.document.assert_called_once_with(content_id)
        mock_doc_ref.get.assert_called_once()
        self.assertEqual(result, content_data)

    @patch('cloud_function.utils.firestore.Client')
    def test_get_content_by_id_not_found(self, mock_firestore):
        """Test get_content_by_id with non-existent content."""
        # Arrange
        mock_db = MagicMock()
        mock_firestore.return_value = mock_db

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        # Mock document snapshot
        mock_snapshot = MagicMock()
        mock_doc_ref.get.return_value = mock_snapshot

        # Mock non-existent content
        mock_snapshot.exists = False

        content_id = "nonexistent-content"

        # Act and Assert
        with self.assertRaises(ValueError) as context:
            get_content_by_id(content_id)

        self.assertIn(f"Content {content_id} not found", str(context.exception))

if __name__ == '__main__':
    unittest.main()
