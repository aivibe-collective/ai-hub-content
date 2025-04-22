#!/usr/bin/env python3
"""
Test runner for performance tests of the Agentic AI Content Creation System.
"""

import os
import sys
import argparse
import logging
import importlib
import json
import datetime
from test.performance.framework import PerformanceTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test/performance/logs/runner.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('performance_runner')

def discover_tests(category=None):
    """
    Discover performance tests.
    
    Args:
        category (str, optional): Category of tests to discover. If None, discover all tests.
    
    Returns:
        list: List of test classes.
    """
    test_classes = []
    
    # Define test directories based on category
    if category:
        test_dirs = [f"test/performance/{category}"]
    else:
        test_dirs = [
            "test/performance/load",
            "test/performance/stress",
            "test/performance/endurance",
            "test/performance/scalability",
            "test/performance/api_response"
        ]
    
    # Discover tests in each directory
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            logger.warning(f"Test directory {test_dir} does not exist")
            continue
        
        for file in os.listdir(test_dir):
            if file.endswith(".py") and file.startswith("test_"):
                module_name = f"test.performance.{os.path.basename(test_dir)}.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find test classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, PerformanceTest) and attr != PerformanceTest:
                            test_classes.append(attr)
                            logger.info(f"Discovered test: {attr.__name__}")
                except Exception as e:
                    logger.error(f"Error importing module {module_name}: {str(e)}")
    
    return test_classes

def run_tests(test_classes, args):
    """
    Run the specified performance tests.
    
    Args:
        test_classes (list): List of test classes to run.
        args (argparse.Namespace): Command-line arguments.
    
    Returns:
        dict: Test results.
    """
    results = {
        'tests': [],
        'summary': {
            'total': len(test_classes),
            'success': 0,
            'error': 0,
            'start_time': datetime.datetime.now().isoformat(),
            'end_time': None,
            'duration': None
        }
    }
    
    start_time = datetime.datetime.now()
    
    for test_class in test_classes:
        # Create test instance with command-line parameters
        test_params = {}
        
        if hasattr(args, 'users') and args.users is not None:
            test_params['num_users'] = args.users
        
        if hasattr(args, 'duration') and args.duration is not None:
            test_params['duration'] = args.duration
        
        if hasattr(args, 'iterations') and args.iterations is not None:
            test_params['iterations'] = args.iterations
        
        try:
            test = test_class(**test_params)
            test_result = test.execute()
            
            results['tests'].append(test_result)
            
            if test_result['status'] == 'success':
                results['summary']['success'] += 1
            else:
                results['summary']['error'] += 1
        except Exception as e:
            logger.error(f"Error running test {test_class.__name__}: {str(e)}")
            results['summary']['error'] += 1
    
    end_time = datetime.datetime.now()
    results['summary']['end_time'] = end_time.isoformat()
    results['summary']['duration'] = (end_time - start_time).total_seconds()
    
    return results

def generate_report(results):
    """
    Generate a report from the test results.
    
    Args:
        results (dict): Test results.
    """
    # Create reports directory
    reports_dir = "test/performance/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Save results to JSON file
    report_file = f"{reports_dir}/performance_test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    logger.info("Performance Test Summary:")
    logger.info(f"Total tests: {results['summary']['total']}")
    logger.info(f"Successful tests: {results['summary']['success']}")
    logger.info(f"Failed tests: {results['summary']['error']}")
    logger.info(f"Duration: {results['summary']['duration']:.2f} seconds")
    logger.info(f"Report saved to: {report_file}")

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run performance tests for the Agentic AI Content Creation System.")
    parser.add_argument("--category", choices=["load", "stress", "endurance", "scalability", "api_response"],
                        help="Category of tests to run")
    parser.add_argument("--users", type=int, help="Number of concurrent users for load and stress tests")
    parser.add_argument("--duration", type=int, help="Duration in seconds for endurance tests")
    parser.add_argument("--iterations", type=int, help="Number of iterations for API response time tests")
    parser.add_argument("--list", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("test/performance/logs", exist_ok=True)
    
    # Discover tests
    test_classes = discover_tests(args.category)
    
    if not test_classes:
        logger.error("No tests discovered")
        return
    
    # List tests if requested
    if args.list:
        logger.info("Available tests:")
        for test_class in test_classes:
            logger.info(f"  {test_class.__name__}")
        return
    
    # Run tests
    results = run_tests(test_classes, args)
    
    # Generate report
    generate_report(results)
    
    # Exit with appropriate status code
    sys.exit(0 if results['summary']['error'] == 0 else 1)

if __name__ == "__main__":
    main()
