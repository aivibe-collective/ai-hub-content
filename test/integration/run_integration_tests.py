#!/usr/bin/env python3
"""
Test runner for integration tests of the Agentic AI Content Creation System.
"""

import os
import sys
import unittest
import argparse

def run_integration_tests(test_modules=None, verbose=False):
    """
    Run the specified integration test modules or all integration tests if none specified.
    
    Args:
        test_modules (list): List of integration test module names to run.
        verbose (bool): Whether to run tests in verbose mode.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    # Check if integration test data exists
    if not os.path.exists(os.path.dirname(os.path.abspath(__file__))):
        print("Error: Integration test directory not found.")
        return False
        
    # Discover and load test modules
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = unittest.TestSuite()
    
    if test_modules:
        # Run specific test modules
        for module_name in test_modules:
            try:
                # Use discover to find the module
                module_pattern = f"{module_name}.py"
                module_suite = loader.discover(start_dir, pattern=module_pattern)
                
                if not list(module_suite):
                    print(f"Error: No tests found in module {module_name}")
                    return False
                    
                suite.addTests(module_suite)
                print(f"Loaded tests from {module_name}")
            except Exception as e:
                print(f"Error loading test module {module_name}: {str(e)}")
                return False
    else:
        # Run all tests in the integration test directory
        suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run the tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run integration tests for the Agentic AI Content Creation System.")
    parser.add_argument("--modules", "-m", nargs="+", help="Specific test modules to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--list", "-l", action="store_true", help="List available test modules")
    
    args = parser.parse_args()
    
    # List available test modules if requested
    if args.list:
        print("Available integration test modules:")
        start_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(start_dir):
            if file.startswith("test_") and file.endswith(".py"):
                module_name = file[:-3]  # Remove .py extension
                print(f"  {module_name}")
        return
    
    # Run the tests
    success = run_integration_tests(args.modules, args.verbose)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
