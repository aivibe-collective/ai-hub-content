#!/usr/bin/env python3
"""
Setup script for the performance test environment.
"""

import os
import sys
import logging
import argparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test/performance/logs/setup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('setup')

def create_directories():
    """Create necessary directories for performance testing."""
    directories = [
        'test/performance/logs',
        'test/performance/reports',
        'test/performance/reports/load',
        'test/performance/reports/stress',
        'test/performance/reports/endurance',
        'test/performance/reports/scalability',
        'test/performance/reports/api_response',
        'test/performance/load',
        'test/performance/stress',
        'test/performance/endurance',
        'test/performance/scalability',
        'test/performance/api_response'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def create_config_file(api_base_url):
    """
    Create a configuration file for performance tests.
    
    Args:
        api_base_url (str): Base URL for the API.
    """
    config = {
        'api_base_url': api_base_url,
        'endpoints': {
            'initialize_content_creation': '/initialize-content-creation',
            'select_template': '/select-template',
            'generate_content_plan': '/generate-content-plan',
            'identify_source_needs': '/identify-source-needs',
            'research_sources': '/research-sources',
            'evaluate_source': '/evaluate-source',
            'generate_citation': '/generate-citation',
            'integrate_source': '/integrate-source',
            'identify_integration_points': '/identify-integration-points',
            'generate_integrated_content': '/generate-integrated-content',
            'check_pillar_balance': '/check-pillar-balance',
            'suggest_impact_metrics': '/suggest-impact-metrics'
        },
        'performance_requirements': {
            'response_time': {
                'api_endpoints': 1.0,  # seconds
                'content_generation': 30.0  # seconds
            },
            'throughput': {
                'min_requests_per_minute': 100
            },
            'error_rate': {
                'normal_load': 1.0,  # percent
                'peak_load': 5.0  # percent
            },
            'concurrency': {
                'min_concurrent_users': 50
            },
            'resource_utilization': {
                'max_cpu_percent': 80.0,
                'max_memory_percent': 80.0
            }
        }
    }
    
    config_file = 'test/performance/config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created configuration file: {config_file}")

def create_init_files():
    """Create __init__.py files in all directories."""
    directories = [
        'test/performance',
        'test/performance/load',
        'test/performance/stress',
        'test/performance/endurance',
        'test/performance/scalability',
        'test/performance/api_response'
    ]
    
    for directory in directories:
        init_file = f"{directory}/__init__.py"
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Performance tests for the Agentic AI Content Creation System."""\n')
            logger.info(f"Created __init__.py file: {init_file}")

def main():
    """Main function to set up the performance test environment."""
    parser = argparse.ArgumentParser(description="Set up the performance test environment.")
    parser.add_argument("--api-base-url", default="http://localhost:8080",
                        help="Base URL for the API (default: http://localhost:8080)")
    
    args = parser.parse_args()
    
    # Create necessary directories
    create_directories()
    
    # Create configuration file
    create_config_file(args.api_base_url)
    
    # Create __init__.py files
    create_init_files()
    
    logger.info("Performance test environment setup complete")

if __name__ == "__main__":
    main()
