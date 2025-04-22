#!/usr/bin/env python3
"""
Script to set up a real test environment with cloud services for the Agentic AI Content Creation System.
"""

import os
import sys
import subprocess
import argparse
import json
import time
import uuid
from pathlib import Path
from google.cloud import firestore, storage, pubsub_v1
import google.api_core.exceptions

def setup_firestore(project_id, test_prefix):
    """Set up Firestore collections for testing."""
    print("Setting up Firestore collections...")
    
    # Initialize Firestore client
    db = firestore.Client(project=project_id)
    
    # Create test collections
    collections = {
        f"{test_prefix}_content-items": [
            # No initial documents
        ],
        f"{test_prefix}_templates": [
            {
                "id": "learning-module-template",
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
            },
            {
                "id": "blog-post-template",
                "type": "BlogPost",
                "content": "# Blog Post Template\n\n**1. Introduction:**\nEngage the reader with a compelling hook and introduce the topic.\n\n**2. Main Points:**\nDevelop 3-5 key points with supporting evidence and examples.\n\n**3. Practical Implications:**\nExplain how the reader can apply this information.\n\n**4. Responsible AI & Sustainability Considerations:**\nAddress ethical and sustainability aspects related to the topic.\n\n**5. Conclusion:**\nSummarize key takeaways and include a call to action.",
                "audience_levels": ["Beginner", "Intermediate", "Expert"],
                "sections": [
                    "1. Introduction",
                    "2. Main Points",
                    "3. Practical Implications",
                    "4. Responsible AI & Sustainability Considerations",
                    "5. Conclusion"
                ]
            }
        ],
        f"{test_prefix}_sources": [
            # No initial documents
        ],
        f"{test_prefix}_users": [
            {
                "id": "test-user-1",
                "name": "Test User",
                "email": "test.user@example.com",
                "roles": ["ContentCreator", "TechnicalReviewer"]
            }
        ]
    }
    
    # Create collections and documents
    for collection_name, documents in collections.items():
        print(f"Setting up collection: {collection_name}")
        
        for doc in documents:
            doc_id = doc.pop("id", str(uuid.uuid4()))
            doc_ref = db.collection(collection_name).document(doc_id)
            
            try:
                doc_ref.set(doc)
                print(f"  Created document: {doc_id}")
            except Exception as e:
                print(f"  Error creating document {doc_id}: {e}")
    
    print("Firestore collections set up successfully.")
    return True

def setup_storage(project_id, test_prefix):
    """Set up Cloud Storage buckets for testing."""
    print("Setting up Cloud Storage buckets...")
    
    # Initialize Storage client
    storage_client = storage.Client(project=project_id)
    
    # Create test buckets
    buckets = [
        f"{test_prefix}-content-bucket",
        f"{test_prefix}-templates-bucket",
        f"{test_prefix}-sources-bucket"
    ]
    
    for bucket_name in buckets:
        try:
            # Check if bucket exists
            try:
                bucket = storage_client.get_bucket(bucket_name)
                print(f"  Bucket already exists: {bucket_name}")
            except google.api_core.exceptions.NotFound:
                # Create bucket
                bucket = storage_client.create_bucket(bucket_name)
                print(f"  Created bucket: {bucket_name}")
            
            # Create test directories
            directories = [
                "content",
                "templates",
                "sources"
            ]
            
            for directory in directories:
                blob = bucket.blob(f"{directory}/.keep")
                blob.upload_from_string("")
                print(f"  Created directory: {directory}")
        except Exception as e:
            print(f"  Error setting up bucket {bucket_name}: {e}")
    
    print("Cloud Storage buckets set up successfully.")
    return True

def setup_pubsub(project_id, test_prefix):
    """Set up Pub/Sub topics and subscriptions for testing."""
    print("Setting up Pub/Sub topics and subscriptions...")
    
    # Initialize Pub/Sub clients
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    
    # Create test topics
    topics = [
        f"{test_prefix}-content-creation-events",
        f"{test_prefix}-source-collection-events",
        f"{test_prefix}-review-events"
    ]
    
    for topic_name in topics:
        topic_path = publisher.topic_path(project_id, topic_name)
        
        try:
            # Check if topic exists
            try:
                publisher.get_topic(request={"topic": topic_path})
                print(f"  Topic already exists: {topic_name}")
            except google.api_core.exceptions.NotFound:
                # Create topic
                publisher.create_topic(request={"name": topic_path})
                print(f"  Created topic: {topic_name}")
            
            # Create subscription
            subscription_name = f"{topic_name}-subscription"
            subscription_path = subscriber.subscription_path(project_id, subscription_name)
            
            try:
                subscriber.get_subscription(request={"subscription": subscription_path})
                print(f"  Subscription already exists: {subscription_name}")
            except google.api_core.exceptions.NotFound:
                # Create subscription
                subscriber.create_subscription(
                    request={"name": subscription_path, "topic": topic_path}
                )
                print(f"  Created subscription: {subscription_name}")
        except Exception as e:
            print(f"  Error setting up topic {topic_name}: {e}")
    
    print("Pub/Sub topics and subscriptions set up successfully.")
    return True

def create_env_file(project_id, test_prefix):
    """Create .env file for testing with real cloud services."""
    print("Creating .env file for testing with real cloud services...")
    
    # Create .env file
    env_content = f"""
# Test environment variables for real cloud services
TEST_PROJECT_ID={project_id}
TEST_PREFIX={test_prefix}

# Firestore configuration
TEST_CONTENT_COLLECTION={test_prefix}_content-items
TEST_TEMPLATES_COLLECTION={test_prefix}_templates
TEST_USERS_COLLECTION={test_prefix}_users
TEST_SOURCE_COLLECTION={test_prefix}_sources

# Pub/Sub configuration
TEST_CONTENT_CREATION_TOPIC={test_prefix}-content-creation-events
TEST_SOURCE_COLLECTION_TOPIC={test_prefix}-source-collection-events
TEST_REVIEW_TOPIC={test_prefix}-review-events

# Storage configuration
TEST_CONTENT_BUCKET={test_prefix}-content-bucket
TEST_TEMPLATES_BUCKET={test_prefix}-templates-bucket
TEST_SOURCES_BUCKET={test_prefix}-sources-bucket

# Vertex AI configuration
TEST_VERTEX_AI_LOCATION=us-central1
TEST_VERTEX_AI_MODEL=text-bison@002
"""
    
    # Write .env file
    with open("test/.env.real", "w") as f:
        f.write(env_content)
    
    print(".env file created successfully at test/.env.real")
    return True

def create_test_config(project_id, test_prefix):
    """Create test configuration file for real cloud services."""
    print("Creating test configuration file for real cloud services...")
    
    # Create test configuration
    config = {
        "test": {
            "project_id": project_id,
            "prefix": test_prefix,
            "firestore": {
                "content_collection": f"{test_prefix}_content-items",
                "template_collection": f"{test_prefix}_templates",
                "users_collection": f"{test_prefix}_users",
                "source_collection": f"{test_prefix}_sources"
            },
            "pubsub": {
                "content_creation_topic": f"{test_prefix}-content-creation-events",
                "source_collection_topic": f"{test_prefix}-source-collection-events",
                "review_topic": f"{test_prefix}-review-events"
            },
            "storage": {
                "content_bucket": f"{test_prefix}-content-bucket",
                "templates_bucket": f"{test_prefix}-templates-bucket",
                "sources_bucket": f"{test_prefix}-sources-bucket"
            },
            "vertex_ai": {
                "location": "us-central1",
                "model": "text-bison@002"
            }
        }
    }
    
    # Create config directory if it doesn't exist
    os.makedirs("test/config", exist_ok=True)
    
    # Write configuration to file
    with open("test/config/real_env_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Test configuration file created successfully at test/config/real_env_config.json")
    return True

def verify_gcloud_setup():
    """Verify that gcloud is set up correctly."""
    print("Verifying gcloud setup...")
    
    # Check if gcloud is installed
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Error: gcloud is not installed. Please install the Google Cloud SDK.")
            return False
    except FileNotFoundError:
        print("Error: gcloud is not installed. Please install the Google Cloud SDK.")
        return False
    
    # Check if gcloud is authenticated
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list"],
            capture_output=True,
            text=True
        )
        
        if "No credentialed accounts." in result.stdout:
            print("Error: gcloud is not authenticated. Please run 'gcloud auth login'.")
            return False
    except Exception as e:
        print(f"Error checking gcloud authentication: {e}")
        return False
    
    # Check if project is set
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("Error: No project is set. Please run 'gcloud config set project PROJECT_ID'.")
            return False
    except Exception as e:
        print(f"Error checking project: {e}")
        return False
    
    print("gcloud is set up correctly.")
    return True

def enable_apis(project_id):
    """Enable required APIs for the project."""
    print(f"Enabling required APIs for project {project_id}...")
    
    # List of required APIs
    apis = [
        "firestore.googleapis.com",
        "pubsub.googleapis.com",
        "storage.googleapis.com",
        "aiplatform.googleapis.com"
    ]
    
    for api in apis:
        try:
            print(f"  Enabling {api}...")
            result = subprocess.run(
                ["gcloud", "services", "enable", api, "--project", project_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"  Error enabling {api}: {result.stderr}")
                return False
        except Exception as e:
            print(f"  Error enabling {api}: {e}")
            return False
    
    print("Required APIs enabled successfully.")
    return True

def main():
    """Main function to set up a real test environment."""
    parser = argparse.ArgumentParser(description="Set up a real test environment with cloud services for the Agentic AI Content Creation System.")
    parser.add_argument("--project-id", required=True, help="Google Cloud project ID")
    parser.add_argument("--test-prefix", default="test", help="Prefix for test resources")
    parser.add_argument("--skip-firestore", action="store_true", help="Skip setting up Firestore")
    parser.add_argument("--skip-storage", action="store_true", help="Skip setting up Cloud Storage")
    parser.add_argument("--skip-pubsub", action="store_true", help="Skip setting up Pub/Sub")
    parser.add_argument("--skip-apis", action="store_true", help="Skip enabling APIs")
    
    args = parser.parse_args()
    
    # Verify gcloud setup
    if not verify_gcloud_setup():
        print("Error: gcloud is not set up correctly. Exiting.")
        sys.exit(1)
    
    # Enable required APIs
    if not args.skip_apis:
        if not enable_apis(args.project_id):
            print("Error enabling required APIs. Exiting.")
            sys.exit(1)
    
    # Set up Firestore
    if not args.skip_firestore:
        if not setup_firestore(args.project_id, args.test_prefix):
            print("Error setting up Firestore. Exiting.")
            sys.exit(1)
    
    # Set up Cloud Storage
    if not args.skip_storage:
        if not setup_storage(args.project_id, args.test_prefix):
            print("Error setting up Cloud Storage. Exiting.")
            sys.exit(1)
    
    # Set up Pub/Sub
    if not args.skip_pubsub:
        if not setup_pubsub(args.project_id, args.test_prefix):
            print("Error setting up Pub/Sub. Exiting.")
            sys.exit(1)
    
    # Create .env file
    if not create_env_file(args.project_id, args.test_prefix):
        print("Error creating .env file. Exiting.")
        sys.exit(1)
    
    # Create test configuration
    if not create_test_config(args.project_id, args.test_prefix):
        print("Error creating test configuration. Exiting.")
        sys.exit(1)
    
    print("\nReal test environment set up successfully.")
    print(f"Project ID: {args.project_id}")
    print(f"Test prefix: {args.test_prefix}")
    print("\nTo use this environment, run:")
    print(f"  export TEST_PROJECT_ID={args.project_id}")
    print(f"  export TEST_PREFIX={args.test_prefix}")
    print("  source test/.env.real")

if __name__ == "__main__":
    main()
