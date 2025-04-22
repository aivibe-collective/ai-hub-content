"""
Performance tests for the Agentic AI Content Creation System.
"""

import unittest
import json
import os
import uuid
import time
import statistics
import requests
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from google.cloud import firestore, storage, pubsub_v1
import google.api_core.exceptions

class PerformanceTest(unittest.TestCase):
    """Base class for performance tests."""
    
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
        
        # Create results directory
        os.makedirs("test/performance/results", exist_ok=True)
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize results
        self.results = []
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def run_test(self, iterations=10, concurrency=1):
        """Run the performance test."""
        print(f"Running {self.__class__.__name__} performance test...")
        print(f"Iterations: {iterations}")
        print(f"Concurrency: {concurrency}")
        
        # Run the test
        start_time = time.time()
        
        if concurrency > 1:
            # Run iterations concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(self.run_iteration) for _ in range(iterations)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        print(f"Error in iteration: {str(e)}")
        else:
            # Run iterations sequentially
            for i in range(iterations):
                try:
                    result = self.run_iteration()
                    self.results.append(result)
                except Exception as e:
                    print(f"Error in iteration {i+1}: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        response_times = [result['response_time'] for result in self.results]
        
        stats = {
            'name': self.__class__.__name__,
            'iterations': iterations,
            'concurrency': concurrency,
            'total_time': total_time,
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'p90_response_time': np.percentile(response_times, 90),
            'p95_response_time': np.percentile(response_times, 95),
            'p99_response_time': np.percentile(response_times, 99),
            'throughput': iterations / total_time
        }
        
        # Print statistics
        print(f"\nResults for {self.__class__.__name__}:")
        print(f"Total time: {stats['total_time']:.2f} seconds")
        print(f"Min response time: {stats['min_response_time']:.2f} seconds")
        print(f"Max response time: {stats['max_response_time']:.2f} seconds")
        print(f"Average response time: {stats['avg_response_time']:.2f} seconds")
        print(f"Median response time: {stats['median_response_time']:.2f} seconds")
        print(f"90th percentile response time: {stats['p90_response_time']:.2f} seconds")
        print(f"95th percentile response time: {stats['p95_response_time']:.2f} seconds")
        print(f"99th percentile response time: {stats['p99_response_time']:.2f} seconds")
        print(f"Throughput: {stats['throughput']:.2f} requests/second")
        
        # Generate charts
        self.generate_charts(stats)
        
        return stats
    
    def run_iteration(self):
        """Run a single iteration of the test."""
        raise NotImplementedError("Subclasses must implement run_iteration")
    
    def generate_charts(self, stats):
        """Generate charts for the performance test results."""
        # Generate response time histogram
        plt.figure(figsize=(10, 6))
        plt.hist([result['response_time'] for result in self.results], bins=20, alpha=0.7)
        plt.axvline(stats['avg_response_time'], color='r', linestyle='dashed', linewidth=1, label=f"Mean: {stats['avg_response_time']:.2f}s")
        plt.axvline(stats['median_response_time'], color='g', linestyle='dashed', linewidth=1, label=f"Median: {stats['median_response_time']:.2f}s")
        plt.axvline(stats['p95_response_time'], color='b', linestyle='dashed', linewidth=1, label=f"95th percentile: {stats['p95_response_time']:.2f}s")
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Frequency')
        plt.title(f'{self.__class__.__name__} - Response Time Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"test/performance/results/{self.__class__.__name__.lower()}_histogram.png")
        plt.close()
        
        # Generate response time over iterations
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(self.results) + 1), [result['response_time'] for result in self.results], marker='o', linestyle='-', alpha=0.7)
        plt.axhline(stats['avg_response_time'], color='r', linestyle='dashed', linewidth=1, label=f"Mean: {stats['avg_response_time']:.2f}s")
        plt.xlabel('Iteration')
        plt.ylabel('Response Time (seconds)')
        plt.title(f'{self.__class__.__name__} - Response Time per Iteration')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"test/performance/results/{self.__class__.__name__.lower()}_iterations.png")
        plt.close()
        
        # Save results to JSON
        with open(f"test/performance/results/{self.__class__.__name__.lower()}_results.json", 'w') as f:
            json.dump({
                'stats': stats,
                'results': self.results
            }, f, indent=2)

class FirestorePerformanceTest(PerformanceTest):
    """Performance test for Firestore operations."""
    
    def run_iteration(self):
        """Run a single iteration of the Firestore performance test."""
        # Create a unique ID for test content
        test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Create content request
        content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": f"Test Content {test_content_id}",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Measure time to create document
        start_time = time.time()
        
        # Create document
        doc_ref = self.db.collection(self.content_collection).document(test_content_id)
        doc_ref.set({
            "metadata": {
                "title": content_request["title"],
                "type": content_request["content_type"],
                "audience": content_request["audience_level"],
                "mission_pillars": content_request["mission_pillars"],
                "status": "initialized",
                "created_at": firestore.SERVER_TIMESTAMP
            },
            "workflow": {
                "current_stage": "template_selection",
                "stages_completed": ["initialization"],
                "last_updated": firestore.SERVER_TIMESTAMP
            }
        })
        
        # Get the document
        doc = doc_ref.get()
        
        # Update the document
        doc_ref.update({
            "metadata.status": "template_selected",
            "workflow.current_stage": "content_planning",
            "workflow.stages_completed": firestore.ArrayUnion(["template_selection"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        # Get the updated document
        doc = doc_ref.get()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Delete the document
        doc_ref.delete()
        
        return {
            'content_id': test_content_id,
            'response_time': response_time
        }

class StoragePerformanceTest(PerformanceTest):
    """Performance test for Cloud Storage operations."""
    
    def run_iteration(self):
        """Run a single iteration of the Cloud Storage performance test."""
        # Create a unique ID for test content
        test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Create content
        content_text = f"""
        # Test Content {test_content_id}
        
        This is a test content for performance testing.
        
        ## Introduction
        
        This is the introduction section.
        
        ## Core Concepts
        
        These are the core concepts.
        
        ## Practical Applications
        
        These are the practical applications.
        """
        
        # Get the bucket
        bucket = self.storage_client.bucket(self.content_bucket)
        
        # Create a test blob
        blob_name = f"content/{test_content_id}.md"
        blob = bucket.blob(blob_name)
        
        # Measure time to upload and download
        start_time = time.time()
        
        # Upload content
        blob.upload_from_string(content_text)
        
        # Download content
        downloaded_content = blob.download_as_text()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Delete the blob
        blob.delete()
        
        return {
            'content_id': test_content_id,
            'content_size': len(content_text),
            'response_time': response_time
        }

class PubSubPerformanceTest(PerformanceTest):
    """Performance test for Pub/Sub operations."""
    
    def run_iteration(self):
        """Run a single iteration of the Pub/Sub performance test."""
        # Create a unique ID for test content
        test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Create a topic path
        topic_path = self.publisher.topic_path(self.project_id, self.content_creation_topic)
        
        # Create a message
        message_data = {
            "content_id": test_content_id,
            "action": "select_template"
        }
        
        # Measure time to publish
        start_time = time.time()
        
        # Publish the message
        data = json.dumps(message_data).encode("utf-8")
        future = self.publisher.publish(topic_path, data)
        message_id = future.result()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            'content_id': test_content_id,
            'message_id': message_id,
            'response_time': response_time
        }

class APIPerformanceTest(PerformanceTest):
    """Performance test for API operations."""
    
    def run_iteration(self):
        """Run a single iteration of the API performance test."""
        # Create a unique ID for test content
        test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Create content request
        content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": f"Test Content {test_content_id}",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Measure time to make API request
        start_time = time.time()
        
        # Send request to create content
        response = requests.post(
            f"{self.api_url}/api/content/initialize",
            json=content_request,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Error initializing content: {response.text}")
        
        # Parse response
        response_data = response.json()
        
        return {
            'content_id': response_data.get('content_id'),
            'status_code': response.status_code,
            'response_time': response_time
        }

class EndToEndPerformanceTest(PerformanceTest):
    """Performance test for end-to-end workflow."""
    
    def run_iteration(self):
        """Run a single iteration of the end-to-end performance test."""
        # Create a unique ID for test content
        test_content_id = f"test-content-{str(uuid.uuid4())[:8]}"
        
        # Create content request
        content_request = {
            "content_type": "LearningModule",
            "audience_level": "Beginner",
            "title": f"Test Content {test_content_id}",
            "mission_pillars": ["ResponsibleAI", "Inclusion"]
        }
        
        # Measure time for end-to-end workflow
        start_time = time.time()
        
        # Step 1: Create content
        doc_ref = self.db.collection(self.content_collection).document(test_content_id)
        doc_ref.set({
            "metadata": {
                "title": content_request["title"],
                "type": content_request["content_type"],
                "audience": content_request["audience_level"],
                "mission_pillars": content_request["mission_pillars"],
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
        # {content_request["title"]}
        
        This is a test content for {test_content_id}.
        
        ## Introduction & Context
        
        Generative AI refers to artificial intelligence systems that can generate new content.
        
        ## Core Concepts
        
        Generative AI models learn patterns from data and generate new content that reflects those patterns.
        """
        
        # Upload content to storage
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.blob(f"content/{test_content_id}.md")
        blob.upload_from_string(section_content)
        
        # Update content with section content
        doc_ref.update({
            "content.sections": section_content,
            "content.storage_path": f"gs://{self.content_bucket}/content/{test_content_id}.md",
            "metadata.status": "sections_populated",
            "workflow.current_stage": "source_collection",
            "workflow.stages_completed": firestore.ArrayUnion(["section_population"]),
            "workflow.last_updated": firestore.SERVER_TIMESTAMP
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Clean up
        doc_ref.delete()
        blob.delete()
        
        return {
            'content_id': test_content_id,
            'response_time': response_time
        }

def run_performance_tests(iterations=10, concurrency=1):
    """Run all performance tests."""
    # Create results directory
    os.makedirs("test/performance/results", exist_ok=True)
    
    # Run Firestore performance test
    firestore_test = FirestorePerformanceTest()
    firestore_stats = firestore_test.run_test(iterations, concurrency)
    
    # Run Storage performance test
    storage_test = StoragePerformanceTest()
    storage_stats = storage_test.run_test(iterations, concurrency)
    
    # Run Pub/Sub performance test
    pubsub_test = PubSubPerformanceTest()
    pubsub_stats = pubsub_test.run_test(iterations, concurrency)
    
    # Run end-to-end performance test
    end_to_end_test = EndToEndPerformanceTest()
    end_to_end_stats = end_to_end_test.run_test(iterations, concurrency)
    
    # Run API performance test if API URL is provided
    api_stats = None
    if os.environ.get("TEST_API_URL"):
        api_test = APIPerformanceTest()
        api_stats = api_test.run_test(iterations, concurrency)
    
    # Generate summary report
    generate_summary_report([
        firestore_stats,
        storage_stats,
        pubsub_stats,
        end_to_end_stats,
        api_stats
    ])

def generate_summary_report(results):
    """Generate a summary report of all performance tests."""
    # Filter out None results
    results = [result for result in results if result]
    
    if not results:
        print("No performance test results to report")
        return
    
    print("\n=== Performance Test Summary ===")
    
    # Create a table of results
    print("\nResponse Time (seconds):")
    print(f"{'Test':<25} {'Avg':<10} {'Median':<10} {'P95':<10} {'P99':<10} {'Min':<10} {'Max':<10} {'Throughput':<15}")
    print("-" * 100)
    
    for result in results:
        print(f"{result['name']:<25} {result['avg_response_time']:<10.2f} {result['median_response_time']:<10.2f} {result['p95_response_time']:<10.2f} {result['p99_response_time']:<10.2f} {result['min_response_time']:<10.2f} {result['max_response_time']:<10.2f} {result['throughput']:<15.2f}")
    
    # Generate comparison chart
    plt.figure(figsize=(12, 8))
    
    # Bar chart for average response times
    plt.subplot(2, 1, 1)
    names = [result['name'] for result in results]
    avg_times = [result['avg_response_time'] for result in results]
    p95_times = [result['p95_response_time'] for result in results]
    
    x = np.arange(len(names))
    width = 0.35
    
    plt.bar(x - width/2, avg_times, width, label='Average', alpha=0.7)
    plt.bar(x + width/2, p95_times, width, label='95th Percentile', alpha=0.7)
    
    plt.xlabel('Test')
    plt.ylabel('Response Time (seconds)')
    plt.title('Average and 95th Percentile Response Times')
    plt.xticks(x, names)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Bar chart for throughput
    plt.subplot(2, 1, 2)
    throughputs = [result['throughput'] for result in results]
    
    plt.bar(x, throughputs, alpha=0.7)
    plt.xlabel('Test')
    plt.ylabel('Throughput (requests/second)')
    plt.title('Throughput')
    plt.xticks(x, names)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("test/performance/results/summary.png")
    plt.close()
    
    # Save summary to JSON
    with open("test/performance/results/summary.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nPerformance test summary saved to test/performance/results/summary.json")
    print("Performance test charts saved to test/performance/results/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run performance tests for the Agentic AI Content Creation System.")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations to run")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    
    args = parser.parse_args()
    
    run_performance_tests(args.iterations, args.concurrency)
