"""
API response time tests for the Agentic AI Content Creation System.
"""

import json
import time
import uuid
import requests
from test.performance.framework import APIResponseTimeTest

class ContentCreationAPIResponseTest(APIResponseTimeTest):
    """API response time test for the Content Creation API endpoints."""
    
    def __init__(self, name="content_creation_api_response_test", description="API response time test for the Content Creation API endpoints", 
                 endpoints=None, iterations=10):
        """
        Initialize the API response time test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoints (dict): Dictionary of API endpoints to test.
            iterations (int): Number of iterations for each endpoint.
        """
        # Define default endpoints if not provided
        if endpoints is None:
            endpoints = {
                "Initialize Content Creation": "http://localhost:8080/initialize-content-creation",
                "Select Template": "http://localhost:8080/select-template",
                "Generate Content Plan": "http://localhost:8080/generate-content-plan",
                "Populate Sections": "http://localhost:8080/populate-sections",
                "Get Content": "http://localhost:8080/content/{content_id}"
            }
        
        super().__init__(name, description, endpoints, iterations)
        self.content_id = None
    
    def setup(self):
        """Set up the API response time test."""
        super().setup()
        
        # Create a content item to use for testing
        try:
            title = f"API Test Content {uuid.uuid4().hex[:8]}"
            payload = {
                "content_type": "LearningModule",
                "audience_level": "Beginner",
                "title": title,
                "mission_pillars": ["ResponsibleAI", "Inclusion"]
            }
            
            response = requests.post(self.endpoints["Initialize Content Creation"], json=payload)
            
            if response.status_code == 200:
                self.content_id = response.json().get('content_id')
                self.logger.info(f"Created content item with ID: {self.content_id}")
                
                # Update the Get Content endpoint with the content ID
                if self.content_id:
                    self.endpoints["Get Content"] = self.endpoints["Get Content"].format(content_id=self.content_id)
            else:
                self.logger.error(f"Failed to create content item: {response.text}")
        except Exception as e:
            self.logger.error(f"Error creating content item: {str(e)}")
    
    def run(self):
        """Run the API response time test."""
        self.logger.info(f"Running API response time test: {self.name}")
        
        for endpoint_name, endpoint_url in self.endpoints.items():
            self.logger.info(f"Testing endpoint: {endpoint_name} ({endpoint_url})")
            
            response_times = []
            
            for i in range(self.iterations):
                try:
                    start_time = time.time()
                    
                    # Make the appropriate request based on the endpoint
                    if endpoint_name == "Initialize Content Creation":
                        title = f"API Test Content {uuid.uuid4().hex[:8]}"
                        payload = {
                            "content_type": "LearningModule",
                            "audience_level": "Beginner",
                            "title": title,
                            "mission_pillars": ["ResponsibleAI", "Inclusion"]
                        }
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Select Template":
                        payload = {"content_id": self.content_id}
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Generate Content Plan":
                        payload = {"content_id": self.content_id}
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Populate Sections":
                        payload = {"content_id": self.content_id}
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Get Content":
                        response = requests.get(endpoint_url)
                    else:
                        response = requests.get(endpoint_url)
                    
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    self.logger.info(f"Iteration {i+1}/{self.iterations}: Response time {response_time:.3f} seconds")
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Error testing endpoint {endpoint_name}, iteration {i+1}: {str(e)}")
            
            # Calculate metrics for this endpoint
            if response_times:
                self.results['metrics']['endpoints'][endpoint_name]['response_times'] = response_times
                self.results['metrics']['endpoints'][endpoint_name]['avg_response_time'] = sum(response_times) / len(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['min_response_time'] = min(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['max_response_time'] = max(response_times)
                
                # Calculate 95th percentile
                sorted_times = sorted(response_times)
                index = int(len(sorted_times) * 0.95)
                self.results['metrics']['endpoints'][endpoint_name]['p95_response_time'] = sorted_times[index]
    
    def cleanup(self):
        """Clean up after the API response time test."""
        super().cleanup()
        
        # Clean up the content item
        if self.content_id:
            try:
                requests.delete(f"http://localhost:8080/content/{self.content_id}")
                self.logger.info(f"Deleted content item with ID: {self.content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {self.content_id}: {str(e)}")

class SourceCollectionAPIResponseTest(APIResponseTimeTest):
    """API response time test for the Source Collection API endpoints."""
    
    def __init__(self, name="source_collection_api_response_test", description="API response time test for the Source Collection API endpoints", 
                 endpoints=None, iterations=10):
        """
        Initialize the API response time test.
        
        Args:
            name (str): Name of the test.
            description (str): Description of the test.
            endpoints (dict): Dictionary of API endpoints to test.
            iterations (int): Number of iterations for each endpoint.
        """
        # Define default endpoints if not provided
        if endpoints is None:
            endpoints = {
                "Identify Source Needs": "http://localhost:8080/identify-source-needs",
                "Research Sources": "http://localhost:8080/research-sources",
                "Evaluate Source": "http://localhost:8080/evaluate-source",
                "Generate Citation": "http://localhost:8080/generate-citation",
                "Integrate Source": "http://localhost:8080/integrate-source"
            }
        
        super().__init__(name, description, endpoints, iterations)
        self.content_id = None
        self.source_need_index = 0
        self.source_index = 0
    
    def setup(self):
        """Set up the API response time test."""
        super().setup()
        
        # Create a content item to use for testing
        try:
            title = f"API Test Content {uuid.uuid4().hex[:8]}"
            payload = {
                "content_type": "LearningModule",
                "audience_level": "Beginner",
                "title": title,
                "mission_pillars": ["ResponsibleAI", "Inclusion"]
            }
            
            response = requests.post("http://localhost:8080/initialize-content-creation", json=payload)
            
            if response.status_code == 200:
                self.content_id = response.json().get('content_id')
                self.logger.info(f"Created content item with ID: {self.content_id}")
                
                # Identify source needs
                content_text = """
                # Introduction to Generative AI
                
                Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances.
                """
                
                source_needs_payload = {
                    "content_id": self.content_id,
                    "content_text": content_text
                }
                
                source_needs_response = requests.post(self.endpoints["Identify Source Needs"], json=source_needs_payload)
                
                if source_needs_response.status_code == 200:
                    self.logger.info("Successfully identified source needs")
                else:
                    self.logger.error(f"Failed to identify source needs: {source_needs_response.text}")
            else:
                self.logger.error(f"Failed to create content item: {response.text}")
        except Exception as e:
            self.logger.error(f"Error setting up test: {str(e)}")
    
    def run(self):
        """Run the API response time test."""
        self.logger.info(f"Running API response time test: {self.name}")
        
        for endpoint_name, endpoint_url in self.endpoints.items():
            self.logger.info(f"Testing endpoint: {endpoint_name} ({endpoint_url})")
            
            response_times = []
            
            for i in range(self.iterations):
                try:
                    start_time = time.time()
                    
                    # Make the appropriate request based on the endpoint
                    if endpoint_name == "Identify Source Needs":
                        content_text = """
                        # Introduction to Generative AI
                        
                        Generative AI has seen rapid adoption in businesses, with nearly half of organizations implementing it in at least one function. The transformer architecture, introduced in 2017, has been fundamental to these advances.
                        """
                        
                        payload = {
                            "content_id": self.content_id,
                            "content_text": content_text
                        }
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Research Sources":
                        payload = {
                            "content_id": self.content_id,
                            "source_need_index": self.source_need_index
                        }
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Evaluate Source":
                        payload = {
                            "content_id": self.content_id,
                            "source_need_index": self.source_need_index,
                            "source_index": self.source_index
                        }
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Generate Citation":
                        payload = {
                            "content_id": self.content_id,
                            "source_need_index": self.source_need_index,
                            "source_index": self.source_index,
                            "citation_style": "APA"
                        }
                        response = requests.post(endpoint_url, json=payload)
                    elif endpoint_name == "Integrate Source":
                        payload = {
                            "content_id": self.content_id,
                            "source_need_index": self.source_need_index,
                            "source_index": self.source_index,
                            "integration_type": "paraphrase"
                        }
                        response = requests.post(endpoint_url, json=payload)
                    else:
                        response = requests.get(endpoint_url)
                    
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    self.logger.info(f"Iteration {i+1}/{self.iterations}: Response time {response_time:.3f} seconds")
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Error testing endpoint {endpoint_name}, iteration {i+1}: {str(e)}")
            
            # Calculate metrics for this endpoint
            if response_times:
                self.results['metrics']['endpoints'][endpoint_name]['response_times'] = response_times
                self.results['metrics']['endpoints'][endpoint_name]['avg_response_time'] = sum(response_times) / len(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['min_response_time'] = min(response_times)
                self.results['metrics']['endpoints'][endpoint_name]['max_response_time'] = max(response_times)
                
                # Calculate 95th percentile
                sorted_times = sorted(response_times)
                index = int(len(sorted_times) * 0.95)
                self.results['metrics']['endpoints'][endpoint_name]['p95_response_time'] = sorted_times[index]
    
    def cleanup(self):
        """Clean up after the API response time test."""
        super().cleanup()
        
        # Clean up the content item
        if self.content_id:
            try:
                requests.delete(f"http://localhost:8080/content/{self.content_id}")
                self.logger.info(f"Deleted content item with ID: {self.content_id}")
            except Exception as e:
                self.logger.error(f"Error deleting content item {self.content_id}: {str(e)}")
