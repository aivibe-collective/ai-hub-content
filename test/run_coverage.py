#!/usr/bin/env python3
"""
Script to run tests and generate a coverage report for the cloud functions.
"""

import os
import sys
import subprocess
import argparse
import webbrowser

def run_tests_with_coverage(module_pattern, html_report=True, open_browser=True):
    """
    Run tests and generate a coverage report.
    
    Args:
        module_pattern (str): Pattern for test modules to run.
        html_report (bool): Whether to generate an HTML report.
        open_browser (bool): Whether to open the report in a browser.
    
    Returns:
        int: Exit code from pytest.
    """
    # Create the command
    cmd = [
        "pytest",
        module_pattern,
        "--cov=cloud_function",
        "--cov-report=term"
    ]
    
    if html_report:
        cmd.append("--cov-report=html")
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Open the HTML report in a browser if requested
    if html_report and open_browser and result.returncode == 0:
        report_path = os.path.abspath("htmlcov/index.html")
        if os.path.exists(report_path):
            print(f"Opening coverage report: {report_path}")
            webbrowser.open(f"file://{report_path}")
        else:
            print(f"Coverage report not found: {report_path}")
    
    return result.returncode

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests and generate a coverage report for the cloud functions.")
    parser.add_argument("--module", "-m", default="test/test_cloud_function_*.py",
                        help="Pattern for test modules to run (default: test/test_cloud_function_*.py)")
    parser.add_argument("--no-html", action="store_true",
                        help="Don't generate an HTML report")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open the report in a browser")
    
    args = parser.parse_args()
    
    # Run the tests
    exit_code = run_tests_with_coverage(
        args.module,
        html_report=not args.no_html,
        open_browser=not args.no_browser
    )
    
    # Exit with the same code as pytest
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
