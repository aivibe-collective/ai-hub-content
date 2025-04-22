# Test Environment for Agentic AI Content Creation System

This directory contains the test environment for the Agentic AI Content Creation System. It includes test cases, test data, and scripts for setting up and running tests.

## Directory Structure

```text
test/
├── config.py                  # Test configuration
├── data/                      # Test data
│   ├── content_plans/         # Sample content plans
│   ├── sources/               # Sample source data
│   ├── templates/             # Content templates
│   └── feedback/              # Mock user feedback
├── integration/               # Integration tests
│   ├── README.md              # Integration tests documentation
│   ├── run_integration_tests.py # Integration test runner
│   ├── test_content_creation_workflow.py # Content creation workflow tests
│   ├── test_source_collection_workflow.py # Source collection workflow tests
│   └── test_mission_pillar_integration_workflow.py # Mission pillar integration tests
├── performance/               # Performance tests
│   ├── README.md              # Performance tests documentation
│   ├── framework.py           # Performance testing framework
│   ├── run_performance_tests.py # Performance test runner
│   ├── setup_perf_env.py      # Performance environment setup script
│   ├── load/                  # Load tests
│   │   └── test_content_creation_api.py # Content creation API load tests
│   ├── stress/                # Stress tests
│   │   └── test_content_creation_api.py # Content creation API stress tests
│   ├── endurance/             # Endurance tests
│   │   └── test_content_creation_endurance.py # Content creation endurance tests
│   └── api_response/          # API response time tests
│       └── test_api_response_times.py # API response time tests
├── run_tests.py               # Test runner script
├── setup_local_env.py         # Local environment setup script
├── setup_cloud_env.py         # Cloud environment setup script
├── cleanup_test_env.py        # Environment cleanup script
├── TEST_PLAN.md               # Comprehensive test plan
├── TEST_SUMMARY.md            # Test implementation summary
├── test_simple.py             # Simple tests for verification
├── test_template_selection_simple.py # Simplified template selection tests
├── test_source_collection_simple.py # Simplified source collection tests
├── test_content_generation_simple.py # Simplified content generation tests
├── test_cloud_functions_simple.py # Simplified cloud functions tests
├── test_blog_post_generation.py # Blog post generation tests
├── test_source_evaluation.py # Source evaluation tests
├── test_mission_pillar_integration.py # Mission pillar integration tests
└── requirements-test.txt      # Test dependencies
```

## Setup

1. Install test dependencies:

   ```bash
   pip install -r test/requirements-test.txt
   ```

2. Set up the test environment:

   ```bash
   python test/setup_test_env.py
   ```

3. For cloud-based testing, deploy the test environment:

   ```bash
   chmod +x deployment/deploy_test_env.sh
   ./deployment/deploy_test_env.sh
   ```

## Running Tests

### Running Unit Tests

```bash
# Run all unit tests
python test/run_tests.py

# Run specific test modules
python test/run_tests.py --modules test_template_selection_simple test_source_collection_simple

# Run tests in verbose mode
python test/run_tests.py --verbose

# Set up local test environment and run tests
python test/run_tests.py --setup

# Set up cloud test environment (requires local setup first)
python test/run_tests.py --cloud-setup

# List available test modules
python test/run_tests.py --list
```

### Running Integration Tests

```bash
# Run all integration tests
python test/integration/run_integration_tests.py

# Run specific integration test modules
python test/integration/run_integration_tests.py --modules test_content_creation_workflow

# Run integration tests in verbose mode
python test/integration/run_integration_tests.py --verbose

# List available integration test modules
python test/integration/run_integration_tests.py --list
```

### Running Performance Tests

```bash
# Set up the performance test environment
python test/performance/setup_perf_env.py

# Run all performance tests
python test/performance/run_performance_tests.py

# Run specific performance test categories
python test/performance/run_performance_tests.py --category load
python test/performance/run_performance_tests.py --category stress
python test/performance/run_performance_tests.py --category endurance
python test/performance/run_performance_tests.py --category api_response

# Run performance tests with specific parameters
python test/performance/run_performance_tests.py --category load --users 100
python test/performance/run_performance_tests.py --category endurance --duration 3600
python test/performance/run_performance_tests.py --category api_response --iterations 10

# List available performance tests
python test/performance/run_performance_tests.py --list
```

### Setting Up and Cleaning Up Test Environment

```bash
# Set up local test environment
python test/setup_local_env.py

# Set up cloud test environment (requires local setup first)
python test/setup_cloud_env.py

# Clean up local test environment
python test/cleanup_test_env.py

# Clean up local and cloud test environment
python test/cleanup_test_env.py --cloud
```

## Test Documentation

- **Test Plan**: For a comprehensive test plan, see [TEST_PLAN.md](TEST_PLAN.md).
- **Test Summary**: For a summary of the test implementation, see [TEST_SUMMARY.md](TEST_SUMMARY.md).
- **Integration Tests**: For information about integration tests, see [integration/README.md](integration/README.md).
- **Performance Tests**: For information about performance tests, see [performance/README.md](performance/README.md).
- **Code Coverage**: For information about code coverage, see [COVERAGE.md](COVERAGE.md).
- **Mock Tests**: For information about mock tests, see [MOCK_TEST_COVERAGE.md](MOCK_TEST_COVERAGE.md).

## Test Data

The test environment includes sample data for testing different components:

- **Content Plans**: Sample content plans for different content types and audience levels
- **Templates**: Content templates from the production environment
- **Source Data**: Sample source documents and metadata
- **User Feedback**: Mock feedback from reviewers

## Adding New Tests

To add new tests:

1. Create a new test file following the naming convention `test_*.py`
2. Import the necessary modules and test fixtures
3. Create test cases using the `unittest` framework
4. Run the tests using the test runner

Example:

```python
import unittest
from unittest.mock import patch, MagicMock

class TestNewComponent(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        pass

    def test_new_functionality(self):
        # Test implementation
        self.assertEqual(expected_result, actual_result)

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting

### Common Issues

- **Authentication Errors**: Ensure you're authenticated with the correct Google Cloud project
- **Missing Dependencies**: Run `pip install -r test/requirements-test.txt` to install all dependencies
- **API Errors**: Check that all required APIs are enabled in the test project
- **Timeout Errors**: Increase the timeout values in the test configuration

### Getting Help

If you encounter issues with the test environment, please contact the development team.
