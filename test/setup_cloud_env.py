"""
Setup script for the cloud test environment.
This script initializes the cloud test environment by:
1. Setting up Cloud Storage buckets
2. Initializing Firestore with test templates
3. Setting up test users
4. Creating Pub/Sub topics
"""

import os
import json
from google.cloud import storage
from google.cloud import firestore
from google.cloud import pubsub_v1
import config

def setup_test_bucket():
    """Create and initialize the test bucket in Cloud Storage."""
    try:
        # Initialize storage client
        storage_client = storage.Client(project=config.TEST_PROJECT_ID)
        
        # Create the test bucket if it doesn't exist
        try:
            bucket = storage_client.get_bucket(config.TEST_CONTENT_BUCKET)
            print(f"Bucket {config.TEST_CONTENT_BUCKET} already exists")
        except Exception:
            bucket = storage_client.create_bucket(
                config.TEST_CONTENT_BUCKET, 
                location=config.TEST_REGION
            )
            print(f"Created bucket: {config.TEST_CONTENT_BUCKET}")
        
        # Create basic directory structure in the bucket
        directories = [
            "content/",
            "sources/",
            "assets/",
            "templates/"
        ]
        
        for directory in directories:
            blob = bucket.blob(f"{directory}.keep")
            blob.upload_from_string('')
            print(f"Created directory in bucket: {directory}")
            
        return True
    except Exception as e:
        print(f"Error setting up test bucket: {str(e)}")
        return False

def setup_firestore_templates():
    """Initialize Firestore with test templates."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=config.TEST_PROJECT_ID)
        
        # Load templates from local test data
        template_dir = config.TEMPLATES_DIR
        
        if not os.path.exists(template_dir):
            print(f"Error: Template directory {template_dir} not found. Run setup_local_env.py first.")
            return False
        
        # Add templates to Firestore
        for filename in os.listdir(template_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(template_dir, filename), 'r') as f:
                        template_data = json.load(f)
                    
                    # Save to Firestore
                    template_type = template_data['type']
                    db.collection(config.TEMPLATES_COLLECTION).document(template_type).set(template_data)
                    print(f"Added template to Firestore: {template_type}")
                    
                except Exception as e:
                    print(f"Error processing template {filename}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error setting up Firestore templates: {str(e)}")
        return False

def setup_test_users():
    """Initialize Firestore with test users."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=config.TEST_PROJECT_ID)
        
        # Define test users
        test_users = [
            {
                'id': 'creator1',
                'name': 'Content Creator 1',
                'email': 'creator1@example.com',
                'role': config.UserRoles.CONTENT_CREATOR
            },
            {
                'id': 'tech_reviewer1',
                'name': 'Technical Reviewer 1',
                'email': 'tech_reviewer1@example.com',
                'role': config.UserRoles.TECHNICAL_REVIEWER
            },
            {
                'id': 'mission_reviewer1',
                'name': 'Mission Pillar Reviewer 1',
                'email': 'mission_reviewer1@example.com',
                'role': config.UserRoles.MISSION_PILLAR_REVIEWER
            },
            {
                'id': 'audience_reviewer1',
                'name': 'Audience Reviewer 1',
                'email': 'audience_reviewer1@example.com',
                'role': config.UserRoles.AUDIENCE_REVIEWER
            },
            {
                'id': 'source_reviewer1',
                'name': 'Source Reviewer 1',
                'email': 'source_reviewer1@example.com',
                'role': config.UserRoles.SOURCE_REVIEWER
            },
            {
                'id': 'editor1',
                'name': 'Editor 1',
                'email': 'editor1@example.com',
                'role': config.UserRoles.EDITOR
            },
            {
                'id': 'admin1',
                'name': 'Admin 1',
                'email': 'admin1@example.com',
                'role': config.UserRoles.ADMIN
            }
        ]
        
        # Add users to Firestore
        for user in test_users:
            db.collection(config.USERS_COLLECTION).document(user['id']).set(user)
            print(f"Added test user to Firestore: {user['name']}")
        
        return True
    except Exception as e:
        print(f"Error setting up test users: {str(e)}")
        return False

def setup_pubsub_topics():
    """Create Pub/Sub topics for testing."""
    try:
        # Initialize Pub/Sub client
        publisher = pubsub_v1.PublisherClient()
        
        # Create topics
        topics = [
            config.CONTENT_CREATION_TOPIC,
            config.SOURCE_COLLECTION_TOPIC,
            config.REVIEW_TOPIC
        ]
        
        for topic in topics:
            topic_path = publisher.topic_path(config.TEST_PROJECT_ID, topic)
            try:
                publisher.create_topic(request={"name": topic_path})
                print(f"Created Pub/Sub topic: {topic}")
            except Exception as e:
                print(f"Topic {topic} already exists or error: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error setting up Pub/Sub topics: {str(e)}")
        return False

def upload_test_data_to_firestore():
    """Upload test data to Firestore."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=config.TEST_PROJECT_ID)
        
        # Upload content plans
        content_plans_dir = config.CONTENT_PLANS_DIR
        if os.path.exists(content_plans_dir):
            for filename in os.listdir(content_plans_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(content_plans_dir, filename), 'r') as f:
                            plan_data = json.load(f)
                        
                        # Save to Firestore
                        plan_id = plan_data['id']
                        db.collection('content-plans-test').document(plan_id).set(plan_data)
                        print(f"Added content plan to Firestore: {plan_id}")
                        
                    except Exception as e:
                        print(f"Error processing content plan {filename}: {str(e)}")
        
        # Upload source data
        sources_dir = config.SOURCE_DATA_DIR
        if os.path.exists(sources_dir):
            for filename in os.listdir(sources_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(sources_dir, filename), 'r') as f:
                            source_data = json.load(f)
                        
                        # Save to Firestore
                        source_id = source_data['id']
                        db.collection('sources-test').document(source_id).set(source_data)
                        print(f"Added source to Firestore: {source_id}")
                        
                    except Exception as e:
                        print(f"Error processing source {filename}: {str(e)}")
        
        # Upload feedback data
        feedback_dir = config.USER_FEEDBACK_DIR
        if os.path.exists(feedback_dir):
            for filename in os.listdir(feedback_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(feedback_dir, filename), 'r') as f:
                            feedback_data = json.load(f)
                        
                        # Save to Firestore
                        feedback_id = feedback_data['id']
                        db.collection('feedback-test').document(feedback_id).set(feedback_data)
                        print(f"Added feedback to Firestore: {feedback_id}")
                        
                    except Exception as e:
                        print(f"Error processing feedback {filename}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error uploading test data to Firestore: {str(e)}")
        return False

def main():
    """Main function to set up the cloud test environment."""
    print("Setting up cloud test environment...")
    
    # Check if local test data exists
    if not os.path.exists(config.TEST_DATA_DIR):
        print("Error: Local test data not found. Run setup_local_env.py first.")
        return
    
    # Set up cloud resources
    setup_test_bucket()
    setup_firestore_templates()
    setup_test_users()
    setup_pubsub_topics()
    upload_test_data_to_firestore()
    
    print("Cloud test environment setup complete!")

if __name__ == "__main__":
    main()
