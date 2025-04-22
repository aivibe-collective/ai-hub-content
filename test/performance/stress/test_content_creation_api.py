"""
Stress tests for the Content Creation API.
"""

import json
import time
import uuid
import requests
from test.performance.framework import StressTest

class ContentCreationAPIStressTest(StressTest):
    """Stress test for the Content Creation API."""
    
    def __init__(self, name="content_creation_api_stress_test", description="Stress test for the Content Creation API", 
                 endpoint="http://localhost:8080/initialize-content-creation", start_users=5, max_users=50, step_size=5, step_duration=30):
        """
        Initialize the stress test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            start_users (int): Initial number of concurrent users.
            max_users (int): Maximum number of concurrent users.
            step_size (int): Number of users to add in each step.
            step_duration (int): Duration of each step in seconds.
        """
        super().__init__(name, description, endpoint, start_users, max_users, step_size, step_duration)
    
    def make_request(self):
        """
        Make a request to the API endpoint.
        
        Returns:
            requests.Response: Response from the API.
        """
        # Generate a unique title for each request
        title = f"Stress Test Content {uuid.uuid4().hex[:8]}"
        
        # Create request payload
        payload = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": title,
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)

class SourceCollectionAPIStressTest(StressTest):
    """Stress test for the Source Collection API."""
    
    def __init__(self, name="source_collection_api_stress_test", description="Stress test for the Source Collection API", 
                 endpoint="http://localhost:8080/identify-source-needs", start_users=5, max_users=30, step_size=5, step_duration=30):
        """
        Initialize the stress test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            start_users (int): Initial number of concurrent users.
            max_users (int): Maximum number of concurrent users.
            step_size (int): Number of users to add in each step.
            step_duration (int): Duration of each step in seconds.
        """
        super().__init__(name, description, endpoint, start_users, max_users, step_size, step_duration)
        self.content_ids = []
    
    def setup(self):
        """Set up the stress test."""
        super().setup()
        
        # Create content items to use in the test
        for i in range(self.max_users * 2):  # Create enough content items for all users
            try:
                # Initialize content creation
                title = f"Stress Test Content {uuid.uuid4().hex[:8]}"
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
        """Clean up after the stress test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")

class MissionPillarIntegrationAPIStressTest(StressTest):
    """Stress test for the Mission Pillar Integration API."""
    
    def __init__(self, name="mission_pillar_api_stress_test", description="Stress test for the Mission Pillar Integration API", 
                 endpoint="http://localhost:8080/identify-integration-points", start_users=3, max_users=20, step_size=3, step_duration=30):
        """
        Initialize the stress test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoint (str): API endpoint to test.
            start_users (int): Initial number of concurrent users.
            max_users (int): Maximum number of concurrent users.
            step_size (int): Number of users to add in each step.
            step_duration (int): Duration of each step in seconds.
        """
        super().__init__(name, description, endpoint, start_users, max_users, step_size, step_duration)
        self.content_ids = []
    
    def setup(self):
        """Set up the stress test."""
        super().setup()
        
        # Create content items to use in the test
        for i in range(self.max_users * 2):  # Create enough content items for all users
            try:
                # Initialize content creation
                title = f"Stress Test Content {uuid.uuid4().hex[:8]}"
                payload = {
                    "content_type": "LearningModule",
                    "audience_level": "Beginner",
                    "title": title,
                    "mission_pillars": ["ResponsibleAI", "Sustainability", "Inclusion"]
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
            "content_id": content_id,
            "section_id": "introduction",
            "section_content": """
            # Introduction to Generative AI
            
            Generative AI refers to artificial intelligence systems that can create new content, including text, images, code, and more. These systems learn patterns from existing data and generate new outputs that reflect those patterns.
            
            Key generative AI technologies include:
            
            - Large Language Models (LLMs) like GPT-4 and PaLM
            - Text-to-image models like DALL-E and Stable Diffusion
            - Code generation tools like GitHub Copilot
            - Music and audio generation systems
            
            These technologies are transforming industries by automating creative tasks, enhancing productivity, and enabling new forms of expression.
            """
        }
        
        # Make POST request to the API
        return requests.post(self.endpoint, json=payload)
    
    def cleanup(self):
        """Clean up after the stress test."""
        super().cleanup()
        
        # Clean up any remaining content items
        for content_id in self.content_ids:
            try:
                requests.delete(f"http://localhost:8080/content/{content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {content_id}: {str(e)}")
