"""
Load tests for the Content Creation API.
"""

import json
import time
import uuid
import requests
from test.performance.framework import LoadTest

class ContentCreationAPILoadTest(LoadTest):
    """Load test for the Content Creation API."""
    
    def __init__(self, name="content_creation_api_load_test", description="Load test for the Content Creation API", 
                 endpoint="http://localhost:8080/initialize-content-creation", num_users=10, requests_per_user=5, ramp_up_time=5):
        """
        Initialize the load test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            requests_per_user (int): Number of requests per user.
            ramp_up_time (int): Time in seconds to ramp up to full load.
        """
        super().__init__(name, description, endpoint, num_users, requests_per_user, ramp_up_time)
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        # Generate a unique title for each request
        title = f"Test Content {uuid.uuid4().hex[:8]}"
        
        # Create request payload
        payload = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": title,
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)

class TemplateSelectionAPILoadTest(LoadTest):
    """Load test for the Template Selection API."""
    
    def __init__(self, name="template_selection_api_load_test", description="Load test for the Template Selection API", 
                 endpoint="http://localhost:8080/select-template", num_users=10, requests_per_user=5, ramp_up_time=5):
        """
        Initialize the load test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            requests_per_user (int): Number of requests per user.
            ramp_up_time (int): Time in seconds to ramp up to full load.
        """
        super().__init__(name, description, endpoint, num_users, requests_per_user, ramp_up_time)
        self.content_ids = []
    
    def setup(self):
        """Set up the load test."""
        super().setup()
        
        # Create content items to use in the test
        for i in range(self.num_users * self.requests_per_user):
            try:
                # Initialize content creation
                title = f"Test Content {uuid.uuid4().hex[:8]}"
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
        
        # Create request payload
        payload = {
            "content_id": content_id
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)
    
    def cleanup(self):
        """Clean up after the load test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")

class ContentPlanGenerationAPILoadTest(LoadTest):
    """Load test for the Content Plan Generation API."""
    
    def __init__(self, name="content_plan_generation_api_load_test", description="Load test for the Content Plan Generation API", 
                 endpoint="http://localhost:8080/generate-content-plan", num_users=5, requests_per_user=3, ramp_up_time=5):
        """
        Initialize the load test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            num_users (int): Number of concurrent users.
            requests_per_user (int): Number of requests per user.
            ramp_up_time (int): Time in seconds to ramp up to full load.
        """
        super().__init__(name, description, endpoint, num_users, requests_per_user, ramp_up_time)
        self.content_ids = []
    
    def setup(self):
        """Set up the load test."""
        super().setup()
        
        # Create content items and select templates
        for i in range(self.num_users * self.requests_per_user):
            try:
                # Initialize content creation
                title = f"Test Content {uuid.uuid4().hex[:8]}"
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
                        # Select template
                        template_response = requests.post("http://localhost:8080/select-template", json={"content_id": content_id})
                        if template_response.status_code == 200:
                            self.content_ids.append(content_id)
            except Exception as e:
                self.logger.error(f"Error setting up content item: {str(e)}")
        
        self.logger.info(f"Created {len(self.content_ids)} content items with templates for testing")
    
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
        
        # Create request payload
        payload = {
            "content_id": content_id
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)
    
    def cleanup(self):
        """Clean up after the load test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")
