# Test Environment for Agentic AI Content Creation System

This directory contains the test environment for the Agentic AI Content Creation System. It includes test cases, test data, and scripts for setting up and running tests.

## Directory Structure

```
test/
├── config.py                  # Test configuration
├── data/                      # Test data
│   ├── content_plans/         # Sample content plans
│   ├── sources/               # Sample source data
│   ├── templates/             # Content templates
│   └── feedback/              # Mock user feedback
├── run_tests.py               # Test runner script
├── setup_test_env.py          # Environment setup script
├── TEST_PLAN.md               # Comprehensive test plan
├── test_template_selection.py # Tests for template selection
├── test_source_collection.py  # Tests for source collection
├── test_content_generation.py # Tests for content generation
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

### Running All Tests

```bash
python test/run_tests.py
```

### Running Specific Test Modules

```bash
python test/run_tests.py --modules test_template_selection test_source_collection
```

### Running Tests in Verbose Mode

```bash
python test/run_tests.py --verbose
```

### Setting Up Environment and Running Tests

```bash
python test/run_tests.py --setup
```

## Test Plan

For a comprehensive test plan, see [TEST_PLAN.md](TEST_PLAN.md).

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
