#!/usr/bin/env python3
"""
Test runner for the Agentic AI Content Creation System.
"""

import os
import sys
import unittest
import argparse

def run_tests(test_modules=None, verbose=False):
    """
    Run the specified test modules or all tests if none specified.
    
    Args:
        test_modules (list): List of test module names to run.
        verbose (bool): Whether to run tests in verbose mode.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    # Discover and load all test modules
    loader = unittest.TestLoader()
    
    if test_modules:
        # Run specific test modules
        suite = unittest.TestSuite()
        for module_name in test_modules:
            try:
                # Import the module
                module = __import__(module_name)
                # Add tests from the module to the suite
                module_tests = loader.loadTestsFromModule(module)
                suite.addTests(module_tests)
                print(f"Loaded tests from {module_name}")
            except ImportError:
                print(f"Error: Could not import test module {module_name}")
                return False
    else:
        # Run all tests in the test directory
        start_dir = os.path.dirname(os.path.abspath(__file__))
        suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run the tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for the Agentic AI Content Creation System.")
    parser.add_argument("--modules", "-m", nargs="+", help="Specific test modules to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--setup", "-s", action="store_true", help="Set up the test environment before running tests")
    
    args = parser.parse_args()
    
    # Set up the test environment if requested
    if args.setup:
        print("Setting up test environment...")
        from setup_test_env import main as setup_main
        setup_main()
    
    # Run the tests
    success = run_tests(args.modules, args.verbose)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
