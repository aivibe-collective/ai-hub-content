#!/usr/bin/env python3
"""
Script to run all mock tests for the Agentic AI Content Creation System.
"""

import os
import sys
import unittest
import argparse

def run_all_mock_tests(verbose=False):
    """
    Run all mock tests.

    Args:
        verbose (bool): Whether to run tests in verbose mode.

    Returns:
        bool: True if all tests passed, False otherwise.
    """
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test files directly
    test_files = [
        'test/run_simple_test.py',
        'test/run_mock_test.py',
        'test/run_mock_integration_test.py',
        'test/run_mock_source_collection_test.py'
    ]

    for test_file in test_files:
        try:
            # Add tests from the file
            file_suite = loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file))
            suite.addTest(file_suite)

            print(f"Loaded tests from {test_file}")
        except Exception as e:
            print(f"Error loading tests from {test_file}: {str(e)}")
            return False

    # Run the tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run all mock tests for the Agentic AI Content Creation System.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")

    args = parser.parse_args()

    # Run the tests
    success = run_all_mock_tests(args.verbose)

    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
