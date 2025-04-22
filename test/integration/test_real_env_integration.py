"""
Integration tests for the Agentic AI Content Creation System in a real environment.
"""

import unittest
import json
import os
import uuid
import time
import requests
from google.cloud import firestore, storage, pubsub_v1
import google.api_core.exceptions

class TestRealEnvIntegration(unittest.TestCase):
    """Integration tests for the Agentic AI Content Creation System in a real environment."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the class."""
        # Get project ID and test prefix
        cls.project_id = os.environ.get("TEST_PROJECT_ID")
        cls.test_prefix = os.environ.get("TEST_PREFIX")
        
        if not cls.project_id or not cls.test_prefix:
            raise ValueError("TEST_PROJECT_ID or TEST_PREFIX environment variable not set.")
        
        # Initialize clients
        cls.db = firestore.Client(project=cls.project_id)
        cls.storage_client = storage.Client(project=cls.project_id)
        cls.publisher = pubsub_v1.PublisherClient()
        
        # Get collection and topic names
        cls.content_collection = os.environ.get("TEST_CONTENT_COLLECTION", f"{cls.test_prefix}_content-items")
        cls.templates_collection = os.environ.get("TEST_TEMPLATES_COLLECTION", f"{cls.test_prefix}_templates")
        cls.content_creation_topic = os.environ.get("TEST_CONTENT_CREATION_TOPIC", f"{cls.test_prefix}-content-creation-events")
        cls.content_bucket = os.environ.get("TEST_CONTENT_BUCKET", f"{cls.test_prefix}-content-bucket")
        
        # Get API URL
        cls.api_url = os.environ.get("TEST_API_URL", "http://localhost:8080")
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a unique ID for test content
        self.test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Mock content request
        self.content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": f"Test Content {self.test_content_id}",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
    
    def tearDown(self):
        """Clean up after each test."""
        # Delete test content
        try:
            self.db.collection(self.content_collection).document(self.test_content_id).delete()
        except Exception:
            pass
        
        # Delete test content from storage
        try:
            bucket = self.storage_client.bucket(self.content_bucket)
            blob = bucket.blob(f"content/{self.test_content_id}.md")
            blob.delete()
        except Exception:
            pass
    
    def test_firestore_operations(self):
        """Test Firestore operations in a real environment."""
        # Create a test document
        doc_ref = self.db.collection(self.content_collection).document(self.test_content_id)
        doc_ref.set({
            "metadata": {
                "title": self.content_request["title"],
                "type": self.content_request["content_type"],
                "audience": self.content_request["audience_level"],
                "mission_pillars": self.content_request["mission_pillars"],
                "status": "initialized",
                "created_at": firestore.SERVER_TIMESTAMP
            }
        })
        
        # Get the document
        doc = doc_ref.get()
        
        # Assert
        self.assertTrue(doc.exists)
        doc_data = doc.to_dict()
        self.assertEqual(doc_data["metadata"]["title"], self.content_request["title"])
        self.assertEqual(doc_data["metadata"]["type"], self.content_request["content_type"])
        
        # Update the document
        doc_ref.update({
            "metadata.status": "template_selected",
            "template": {
                "type": "LearningModule",
                "sections": ["Introduction", "Core Concepts"]
            }
        })
        
        # Get the updated document
        doc = doc_ref.get()
        doc_data = doc.to_dict()
        
        # Assert
        self.assertEqual(doc_data["metadata"]["status"], "template_selected")
        self.assertEqual(doc_data["template"]["type"], "LearningModule")
    
    def test_storage_operations(self):
        """Test Cloud Storage operations in a real environment."""
        # Get the bucket
        bucket = self.storage_client.bucket(self.content_bucket)
        
        # Create a test blob
        blob_name = f"content/{self.test_content_id}.md"
        blob = bucket.blob(blob_name)
        
        # Upload content
        content_text = f"# Test Content {self.test_content_id}\n\nThis is a test content."
        blob.upload_from_string(content_text)
        
        # Check if blob exists
        self.assertTrue(blob.exists())
        
        # Download content
        downloaded_content = blob.download_as_text()
        
        # Assert
        self.assertEqual(downloaded_content, content_text)
    
    def test_pubsub_operations(self):
        """Test Pub/Sub operations in a real environment."""
        # Create a topic path
        topic_path = self.publisher.topic_path(self.project_id, self.content_creation_topic)
        
        # Create a message
        message_data = {
            "content_id": self.test_content_id,
            "action": "select_template"
        }
        
        # Publish the message
        data = json.dumps(message_data).encode("utf-8")
        future = self.publisher.publish(topic_path, data)
        message_id = future.result()
        
        # Assert
        self.assertIsNotNone(message_id)
    
    def test_template_retrieval(self):
        """Test template retrieval from Firestore."""
        # Get the template
        template_ref = self.db.collection(self.templates_collection).document("learning-module-template")
        template_doc = template_ref.get()
        
        # Assert
        self.assertTrue(template_doc.exists)
        template_data = template_doc.to_dict()
        self.assertEqual(template_data["type"], "LearningModule")
        self.assertIn("Beginner", template_data["audience_levels"])
    
    @unittest.skip("Requires running API server")
    def test_api_content_creation(self):
        """Test content creation through the API."""
        # Send request to create content
        response = requests.post(
            f"{self.api_url}/api/content/initialize",
            json=self.content_request,
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "success")
        self.assertIn("content_id", response_data)
        
        # Get the content ID
        content_id = response_data["content_id"]
        
        # Wait for content to be created
        time.sleep(2)
        
        # Get the content from Firestore
        doc_ref = self.db.collection(self.content_collection).document(content_id)
        doc = doc_ref.get()
        
        # Assert
        self.assertTrue(doc.exists)
        doc_data = doc.to_dict()
        self.assertEqual(doc_data["metadata"]["title"], self.content_request["title"])
        self.assertEqual(doc_data["metadata"]["type"], self.content_request["content_type"])
    
    def test_end_to_end_workflow_simulation(self):
        """Simulate an end-to-end workflow in a real environment."""
        # Step 1: Create content
        doc_ref = self.db.collection(self.content_collection).document(self.test_content_id)
        doc_ref.set({
            "metadata": {
                "title": self.content_request["title"],
                "type": self.content_request["content_type"],
                "audience": self.content_request["audience_level"],
                "mission_pillars": self.content_request["mission_pillars"],
                "status": "initialized",
                "created_at": firestore.SERVER_TIMESTAMP
            },
            "workflow": {
                "current_stage": "template_selection",
                "stages_completed": ["initialization"],
                "last_updated": firestore.SERVER_TIMESTAMP
            }
        })
        
        # Step 2: Select template
        template_ref = self.db.collection(self.templates_collection).document("learning-module-template")
        template_doc = template_ref.get()
        template_data = template_doc.to_dict()
        
        doc_ref.update({
            "template": template_data,
            "metadata.status": "template_selected",
            "workflow.current_stage": "content_planning",
            "workflow.stages_completed": firestore.ArrayUnion(["template_selection"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        # Step 3: Generate content plan
        content_plan = {
            "learning_objectives": [
                "By the end of this module, learners will be able to define generative AI and explain its key components."
            ],
            "key_concepts": {
                "Introduction & Context": [
                    "Definition of generative AI",
                    "Distinction from traditional AI"
                ]
            }
        }
        
        doc_ref.update({
            "content.plan": content_plan,
            "metadata.status": "plan_generated",
            "workflow.current_stage": "section_population",
            "workflow.stages_completed": firestore.ArrayUnion(["content_planning"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        # Step 4: Generate section content
        section_content = f"""
        # {self.content_request["title"]}
        
        This is a test content for {self.test_content_id}.
        
        ## Introduction & Context
        
        Generative AI refers to artificial intelligence systems that can generate new content.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns.
        """
        
        # Upload content to storage
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob(f"content/{self.test_content_id}.md")
        blob.upload_from_string(section_content)
        
        # Update content with section content
        doc_ref.update({
            "content.sections": section_content,
            "content.storage_path": f"gs://{self.content_bucket}/content/{self.test_content_id}.md",
            "metadata.status": "sections_populated",
            "workflow.current_stage": "source_collection",
            "workflow.stages_completed": firestore.ArrayUnion(["section_population"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        # Step 5: Identify source needs
        source_needs = [
            {
                "statement": "Generative AI refers to artificial intelligence systems that can generate new content.",
                "type": "conceptual",
                "context": "Introduction section",
                "requirements": {
                    "recency": "Last 2 years",
                    "authority": "Academic or industry source",
                    "specific_needs": "Clear definition of generative AI"
                }
            }
        ]
        
        doc_ref.update({
            "sources.needs": source_needs,
            "metadata.status": "source_needs_identified",
            "workflow.current_stage": "source_research",
            "workflow.stages_completed": firestore.ArrayUnion(["source_need_identification"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        # Step 6: Get the final document
        doc = doc_ref.get()
        doc_data = doc.to_dict()
        
        # Assert
        self.assertEqual(doc_data["metadata"]["status"], "source_needs_identified")
        self.assertEqual(doc_data["workflow"]["current_stage"], "source_research")
        self.assertIn("source_need_identification", doc_data["workflow"]["stages_completed"])
        self.assertEqual(len(doc_data["sources"]["needs"]), 1)
        
        # Download content from storage
        downloaded_content = blob.download_as_text()
        
        # Assert
        self.assertEqual(downloaded_content, section_content)

if __name__ == "__main__":
    unittest.main()
