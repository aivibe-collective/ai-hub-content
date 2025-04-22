#!/usr/bin/env python3
"""
Script to run tests in a real environment with cloud services for the Agentic AI Content Creation System.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
import dotenv

def load_env_file():
    """Load environment variables from .env.real file."""
    print("Loading environment variables from .env.real file...")
    
    # Check if .env.real file exists
    env_file = Path("test/.env.real")
    if not env_file.exists():
        print("Error: .env.real file not found. Please run setup_real_env.py first.")
        return False
    
    # Load environment variables
    dotenv.load_dotenv(env_file)
    
    # Verify required environment variables
    required_vars = [
        "TEST_PROJECT_ID",
        "TEST_PREFIX",
        "TEST_CONTENT_COLLECTION",
        "TEST_TEMPLATES_COLLECTION",
        "TEST_CONTENT_CREATION_TOPIC",
        "TEST_CONTENT_BUCKET"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("Environment variables loaded successfully.")
    return True

def run_unit_tests(coverage=False):
    """Run unit tests for cloud functions."""
    print("Running unit tests for cloud functions...")
    
    # Set up command
    cmd = ["python3", "-m", "pytest", "test/test_cloud_function_*.py", "-v"]
    
    if coverage:
        cmd = ["python3", "-m", "pytest", "test/test_cloud_function_*.py", "-v", "--cov=cloud_function", "--cov-report=term", "--cov-report=html:test/coverage/real_env/unit"]
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Return success status
    return result.returncode == 0

def run_integration_tests(coverage=False):
    """Run integration tests for workflows."""
    print("Running integration tests for workflows...")
    
    # Set up command
    cmd = ["python3", "test/integration/run_integration_tests.py", "--cloud-functions"]
    
    if coverage:
        cmd = ["python3", "test/integration/run_integration_tests.py", "--cloud-functions", "--coverage"]
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Return success status
    return result.returncode == 0

def run_real_env_integration_tests(coverage=False):
    """Run integration tests in a real environment."""
    print("Running integration tests in a real environment...")
    
    # Set up command
    cmd = ["python3", "-m", "pytest", "test/integration/test_real_env_integration.py", "-v"]
    
    if coverage:
        cmd = ["python3", "-m", "pytest", "test/integration/test_real_env_integration.py", "-v", "--cov=cloud_function", "--cov=cloud_run", "--cov-report=term", "--cov-report=html:test/coverage/real_env/integration"]
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Return success status
    return result.returncode == 0

def run_performance_tests():
    """Run performance tests in a real environment."""
    print("Running performance tests in a real environment...")
    
    # Set up command
    cmd = ["python3", "test/performance/run_performance_tests.py", "--api-url", os.environ.get("TEST_API_URL", "http://localhost:8080")]
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Return success status
    return result.returncode == 0

def generate_coverage_report():
    """Generate a combined coverage report."""
    print("Generating combined coverage report...")
    
    # Set up command
    cmd = ["python3", "-m", "coverage", "combine", "test/coverage/real_env/.coverage.*"]
    
    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Generate report
    cmd = ["python3", "-m", "coverage", "report"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Generate HTML report
    cmd = ["python3", "-m", "coverage", "html", "-d", "test/coverage/real_env/html"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    print("Coverage report generated successfully.")
    print("HTML report available at: test/coverage/real_env/html/index.html")
    
    return True

def cleanup_test_data():
    """Clean up test data after running tests."""
    print("Cleaning up test data...")
    
    # Get project ID and test prefix
    project_id = os.environ.get("TEST_PROJECT_ID")
    test_prefix = os.environ.get("TEST_PREFIX")
    
    if not project_id or not test_prefix:
        print("Error: TEST_PROJECT_ID or TEST_PREFIX environment variable not set.")
        return False
    
    # Clean up Firestore
    print("Cleaning up Firestore collections...")
    try:
        from google.cloud import firestore
        
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        # Delete test documents
        collections = [
            f"{test_prefix}_content-items",
            f"{test_prefix}_templates",
            f"{test_prefix}_sources",
            f"{test_prefix}_users"
        ]
        
        for collection_name in collections:
            # Delete all documents in the collection
            docs = db.collection(collection_name).stream()
            for doc in docs:
                if doc.id != "learning-module-template" and doc.id != "blog-post-template" and doc.id != "test-user-1":
                    doc.reference.delete()
                    print(f"  Deleted document: {doc.id} from {collection_name}")
    except Exception as e:
        print(f"Error cleaning up Firestore: {e}")
    
    # Clean up Cloud Storage
    print("Cleaning up Cloud Storage buckets...")
    try:
        from google.cloud import storage
        
        # Initialize Storage client
        storage_client = storage.Client(project=project_id)
        
        # Delete test objects
        buckets = [
            f"{test_prefix}-content-bucket",
            f"{test_prefix}-templates-bucket",
            f"{test_prefix}-sources-bucket"
        ]
        
        for bucket_name in buckets:
            try:
                bucket = storage_client.get_bucket(bucket_name)
                
                # Delete all objects except .keep files
                blobs = bucket.list_blobs()
                for blob in blobs:
                    if not blob.name.endswith("/.keep"):
                        blob.delete()
                        print(f"  Deleted object: {blob.name} from {bucket_name}")
            except Exception as e:
                print(f"  Error cleaning up bucket {bucket_name}: {e}")
    except Exception as e:
        print(f"Error cleaning up Cloud Storage: {e}")
    
    print("Test data cleaned up successfully.")
    return True

def main():
    """Main function to run tests in a real environment."""
    parser = argparse.ArgumentParser(description="Run tests in a real environment with cloud services for the Agentic AI Content Creation System.")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--real-env", action="store_true", help="Run real environment integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test data after running tests")
    
    args = parser.parse_args()
    
    # Load environment variables
    if not load_env_file():
        print("Error loading environment variables. Exiting.")
        sys.exit(1)
    
    # Create coverage directory
    os.makedirs("test/coverage/real_env", exist_ok=True)
    
    try:
        # Determine which tests to run
        run_all = args.all or not any([args.unit, args.integration, args.real_env, args.performance])
        
        # Run tests
        success = True
        
        if args.unit or run_all:
            success = run_unit_tests(args.coverage) and success
        
        if args.integration or run_all:
            success = run_integration_tests(args.coverage) and success
        
        if args.real_env or run_all:
            success = run_real_env_integration_tests(args.coverage) and success
        
        if args.performance or run_all:
            success = run_performance_tests() and success
        
        # Generate combined coverage report if requested
        if args.coverage:
            generate_coverage_report()
        
        # Clean up test data if requested
        if args.cleanup:
            cleanup_test_data()
        
        # Return success status
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
