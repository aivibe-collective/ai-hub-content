"""
Endurance tests for the Content Creation API.
"""

import json
import time
import uuid
import requests
from test.performance.framework import EnduranceTest

class ContentCreationAPIEnduranceTest(EnduranceTest):
    """Endurance test for the Content Creation API."""
    
    def __init__(self, name="content_creation_api_endurance_test", description="Endurance test for the Content Creation API", 
                 endpoint="http://localhost:8080/initialize-content-creation", num_users=5, duration=1800, sampling_interval=60):
        """
        Initialize the endurance test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            duration (int): Test duration in seconds.
            sampling_interval (int): Interval in seconds between metric samples.
        """
        super().__init__(name, description, endpoint, num_users, duration, sampling_interval)
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        # Generate a unique title for each request
        title = f"Endurance Test Content {uuid.uuid4().hex[:8]}"
        
        # Create request payload
        payload = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": title,
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)

class SourceCollectionAPIEnduranceTest(EnduranceTest):
    """Endurance test for the Source Collection API."""
    
    def __init__(self, name="source_collection_api_endurance_test", description="Endurance test for the Source Collection API", 
                 endpoint="http://localhost:8080/identify-source-needs", num_users=3, duration=1200, sampling_interval=60):
        """
        Initialize the endurance test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            duration (int): Test duration in seconds.
            sampling_interval (int): Interval in seconds between metric samples.
        """
        super().__init__(name, description, endpoint, num_users, duration, sampling_interval)
        self.content_ids = []
    
    def setup(self):
        """Set up the endurance test."""
        super().setup()
        
        # Calculate how many content items we need
        num_samples = self.duration // self.sampling_interval
        total_requests = num_samples * self.num_users * 5  # 5 requests per user per sample
        
        # Create content items to use in the test
        for i in range(total_requests):
            try:
                # Initialize content creation
                title = f"Endurance Test Content {uuid.uuid4().hex[:8]}"
                payload = {
                    "content_type": "LearningModule",
                    "audience_level": "Beginner",
                    "title": title,
                    "mission_pillars": ["ResponsibleAI", "Inclusion"]
                }
                
                response = requests.post("http://localhost:8080/initialize-content-creation", json=payload)
                
                if response.status_code == 200:
                    content_id = response.json().get('content_id')
                    if content_id:
                        self.content_ids.append(content_id)
            except Exception as e:
                self.logger.error(f"Error creating content item: {str(e)}")
        
        self.logger.info(f"Created {len(self.content_ids)} content items for testing")
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        # Get a content ID from the list
        if not self.content_ids:
            raise Exception("No content IDs available for testing")
        
        content_id = self.content_ids.pop(0)
        
        # Create request payload with sample content text
        payload = {
            "content_id": content_id,
            "content_text": """
            # Introduction to Generative AI
            
            Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances. Recent regulations like the EU AI Act are shaping how these technologies can be deployed.
            
            ## Core Concepts
            
            Generative AI models learn patterns from data and generate new content that reflects those patterns. The transformer architecture, which relies on attention mechanisms, has been particularly successful for text generation tasks.
            
            ## Practical Applications
            
            Businesses are using generative AI for customer service automation, content creation, and code generation. These applications can significantly improve productivity and enable new capabilities.
            """
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)
    
    def cleanup(self):
        """Clean up after the endurance test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")

class CompleteWorkflowEnduranceTest(EnduranceTest):
    """Endurance test for the complete content creation workflow."""
    
    def __init__(self, name="complete_workflow_endurance_test", description="Endurance test for the complete content creation workflow", 
                 endpoint="http://localhost:8080/initialize-content-creation", num_users=2, duration=3600, sampling_interval=120):
        """
        Initialize the endurance test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            duration (int): Test duration in seconds.
            sampling_interval (int): Interval in seconds between metric samples.
        """
        super().__init__(name, description, endpoint, num_users, duration, sampling_interval)
        self.content_ids = []
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        # Generate a unique title for each request
        title = f"Workflow Endurance Test Content {uuid.uuid4().hex[:8]}"
        
        # Create request payload
        payload = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": title,
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Make POST request to initialize content creation
        response = requests.post(self.endpoint, json=payload)
        
        if response.status_code == 200:
            content_id = response.json().get('content_id')
            if content_id:
                self.content_ids.append(content_id)
                
                # Execute the complete workflow
                try:
                    # Select template
                    template_response = requests.post("http://localhost:8080/select-template", json={"content_id": content_id})
                    
                    # Generate content plan
                    plan_response = requests.post("http://localhost:8080/generate-content-plan", json={"content_id": content_id})
                    
                    # Identify source needs
                    content_text = """
                    # Introduction to Generative AI
                    
                    Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances.
                    """
                    
                    source_needs_response = requests.post("http://localhost:8080/identify-source-needs", json={
                        "content_id": content_id,
                        "content_text": content_text
                    })
                    
                    # Identify mission pillar integration points
                    integration_response = requests.post("http://localhost:8080/identify-integration-points", json={
                        "content_id": content_id,
                        "section_id": "introduction",
                        "section_content": content_text
                    })
                except Exception as e:
                    self.logger.error(f"Error executing workflow for content {content_id}: {str(e)}")
        
        return response
    
    def cleanup(self):
        """Clean up after the endurance test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")
