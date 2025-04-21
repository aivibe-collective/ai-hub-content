"""
Cleanup script for the test environment.
This script cleans up the test environment by:
1. Removing local test data
2. Optionally removing cloud resources
"""

import os
import shutil
import argparse
from google.cloud import storage
from google.cloud import firestore
from google.cloud import pubsub_v1
import config

def cleanup_local_data():
    """Remove local test data."""
    try:
        # Remove test data directory
        if os.path.exists(config.TEST_DATA_DIR):
            shutil.rmtree(config.TEST_DATA_DIR)
            print(f"Removed local test data directory: {config.TEST_DATA_DIR}")
        else:
            print(f"Local test data directory not found: {config.TEST_DATA_DIR}")
        
        return True
    except Exception as e:
        print(f"Error cleaning up local test data: {str(e)}")
        return False

def cleanup_cloud_storage():
    """Remove test bucket from Cloud Storage."""
    try:
        # Initialize storage client
        storage_client = storage.Client(project=config.TEST_PROJECT_ID)
        
        # Delete the test bucket if it exists
        try:
            bucket = storage_client.get_bucket(config.TEST_CONTENT_BUCKET)
            
            # Delete all objects in the bucket
            blobs = bucket.list_blobs()
            for blob in blobs:
                blob.delete()
                print(f"Deleted blob: {blob.name}")
            
            # Delete the bucket
            bucket.delete()
            print(f"Deleted bucket: {config.TEST_CONTENT_BUCKET}")
        except Exception as e:
            print(f"Bucket {config.TEST_CONTENT_BUCKET} not found or error: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error cleaning up Cloud Storage: {str(e)}")
        return False

def cleanup_firestore():
    """Remove test collections from Firestore."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=config.TEST_PROJECT_ID)
        
        # Delete test collections
        collections = [
            config.CONTENT_ITEMS_COLLECTION,
            config.TEMPLATES_COLLECTION,
            config.SOURCES_COLLECTION,
            config.USERS_COLLECTION,
            'content-plans-test',
            'sources-test',
            'feedback-test'
        ]
        
        for collection_name in collections:
            # Delete all documents in the collection
            docs = db.collection(collection_name).limit(100).stream()
            deleted = 0
            
            for doc in docs:
                doc.reference.delete()
                deleted += 1
            
            print(f"Deleted {deleted} documents from collection: {collection_name}")
        
        return True
    except Exception as e:
        print(f"Error cleaning up Firestore: {str(e)}")
        return False

def cleanup_pubsub():
    """Remove test topics from Pub/Sub."""
    try:
        # Initialize Pub/Sub client
        publisher = pubsub_v1.PublisherClient()
        
        # Delete test topics
        topics = [
            config.CONTENT_CREATION_TOPIC,
            config.SOURCE_COLLECTION_TOPIC,
            config.REVIEW_TOPIC
        ]
        
        for topic in topics:
            topic_path = publisher.topic_path(config.TEST_PROJECT_ID, topic)
            try:
                publisher.delete_topic(request={"topic": topic_path})
                print(f"Deleted Pub/Sub topic: {topic}")
            except Exception as e:
                print(f"Topic {topic} not found or error: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error cleaning up Pub/Sub: {str(e)}")
        return False

def main():
    """Main function to clean up the test environment."""
    parser = argparse.ArgumentParser(description="Clean up the test environment.")
    parser.add_argument("--cloud", "-c", action="store_true", help="Clean up cloud resources")
    parser.add_argument("--force", "-f", action="store_true", help="Force cleanup without confirmation")
    
    args = parser.parse_args()
    
    # Confirm cleanup
    if not args.force:
        confirm = input("This will delete all test data. Are you sure? (y/n): ")
        if confirm.lower() != 'y':
            print("Cleanup aborted.")
            return
    
    print("Cleaning up local test environment...")
    cleanup_local_data()
    
    # Clean up cloud resources if requested
    if args.cloud:
        print("Cleaning up cloud resources...")
        cleanup_cloud_storage()
        cleanup_firestore()
        cleanup_pubsub()
    
    print("Test environment cleanup complete!")

if __name__ == "__main__":
    main()
