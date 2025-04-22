#!/usr/bin/env python3
"""
Script to run actual tests for the Agentic AI Content Creation System.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path

def start_emulators():
    """Start local emulators for testing."""
    print("Starting local emulators...")

    # Start Firestore emulator
    firestore_process = subprocess.Popen(
        ["gcloud", "beta", "emulators", "firestore", "start", "--host-port=localhost:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Start Pub/Sub emulator
    pubsub_process = subprocess.Popen(
        ["gcloud", "beta", "emulators", "pubsub", "start", "--host-port=localhost:8085"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for emulators to start
    print("Waiting for emulators to start...")
    time.sleep(5)

    # Set environment variables
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
    os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"

    print("Emulators started successfully.")
    return firestore_process, pubsub_process

def stop_emulators(firestore_process, pubsub_process):
    """Stop local emulators."""
    print("Stopping emulators...")

    # Stop Firestore emulator
    firestore_process.terminate()

    # Stop Pub/Sub emulator
    pubsub_process.terminate()

    print("Emulators stopped successfully.")

def run_unit_tests(coverage=False):
    """Run unit tests for cloud functions."""
    print("Running unit tests for cloud functions...")

    # Set up command
    cmd = ["python3", "-m", "pytest", "test/test_cloud_function_*.py", "-v"]

    if coverage:
        cmd = ["python3", "-m", "pytest", "test/test_cloud_function_*.py", "-v", "--cov=cloud_function", "--cov-report=term", "--cov-report=html:test/coverage/unit"]

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
    cmd = ["python", "test/integration/run_integration_tests.py", "--cloud-functions"]

    if coverage:
        cmd = ["python", "test/integration/run_integration_tests.py", "--cloud-functions", "--coverage"]

    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

    # Return success status
    return result.returncode == 0

def run_source_collection_tests(coverage=False):
    """Run source collection integration tests."""
    print("Running source collection integration tests...")

    # Set up command
    cmd = ["python3", "-m", "pytest", "test/integration/test_source_collection_integration.py", "-v"]

    if coverage:
        cmd = ["python3", "-m", "pytest", "test/integration/test_source_collection_integration.py", "-v", "--cov=cloud_function", "--cov=cloud_run.research_service", "--cov-report=term", "--cov-report=html:test/coverage/source_collection"]

    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

    # Return success status
    return result.returncode == 0

def run_edge_case_tests(coverage=False):
    """Run edge case tests."""
    print("Running edge case tests...")

    # Set up command
    cmd = ["python3", "-m", "pytest", "test/test_edge_cases.py", "-v"]

    if coverage:
        cmd = ["python3", "-m", "pytest", "test/test_edge_cases.py", "-v", "--cov=cloud_function", "--cov=cloud_run", "--cov-report=term", "--cov-report=html:test/coverage/edge_cases"]

    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

    # Return success status
    return result.returncode == 0

def run_performance_tests():
    """Run performance tests."""
    print("Running performance tests...")

    # Set up command
    cmd = ["python", "test/performance/run_performance_tests.py"]

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
    cmd = ["python3", "-m", "coverage", "combine", "test/coverage/.coverage.*"]

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
    cmd = ["python3", "-m", "coverage", "html", "-d", "test/coverage/html"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print output
    if result.stderr:
        print(f"Errors: {result.stderr}")

    print("Coverage report generated successfully.")
    print("HTML report available at: test/coverage/html/index.html")

    return True

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Run actual tests for the Agentic AI Content Creation System.")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--source-collection", action="store_true", help="Run source collection tests")
    parser.add_argument("--edge-cases", action="store_true", help="Run edge case tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--skip-emulators", action="store_true", help="Skip starting emulators")

    args = parser.parse_args()

    # Create coverage directory
    os.makedirs("test/coverage", exist_ok=True)

    # Start emulators if needed
    firestore_process = None
    pubsub_process = None

    if not args.skip_emulators:
        firestore_process, pubsub_process = start_emulators()

    try:
        # Determine which tests to run
        run_all = args.all or not any([args.unit, args.integration, args.source_collection, args.edge_cases, args.performance])

        # Run tests
        success = True

        if args.unit or run_all:
            success = run_unit_tests(args.coverage) and success

        if args.integration or run_all:
            success = run_integration_tests(args.coverage) and success

        if args.source_collection or run_all:
            success = run_source_collection_tests(args.coverage) and success

        if args.edge_cases or run_all:
            success = run_edge_case_tests(args.coverage) and success

        if args.performance or run_all:
            success = run_performance_tests() and success

        # Generate combined coverage report if requested
        if args.coverage:
            generate_coverage_report()

        # Return success status
        return 0 if success else 1

    finally:
        # Stop emulators if they were started
        if firestore_process and pubsub_process:
            stop_emulators(firestore_process, pubsub_process)

if __name__ == "__main__":
    sys.exit(main())
