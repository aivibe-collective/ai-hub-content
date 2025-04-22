# Integration Tests for Agentic AI Content Creation System

This directory contains integration tests for the Agentic AI Content Creation System. These tests validate the interaction between different components of the system and ensure that the complete workflows function correctly.

## Test Modules

The integration tests are organized into the following modules:

1. **Content Creation Workflow** (`test_content_creation_workflow.py`):
   - Tests the end-to-end content creation workflow
   - Validates the interaction between initialization, template selection, and content plan generation

2. **Source Collection Workflow** (`test_source_collection_workflow.py`):
   - Tests the end-to-end source collection workflow
   - Validates the interaction between source need identification, research, evaluation, citation, and integration

3. **Mission Pillar Integration Workflow** (`test_mission_pillar_integration_workflow.py`):
   - Tests the end-to-end mission pillar integration workflow
   - Validates the interaction between integration point identification, content generation, balance checking, and impact metric suggestion

4. **Cloud Function Integration** (`test_cloud_function_integration.py`):
   - Tests the integration between different cloud functions
   - Validates the end-to-end content creation workflow with error handling
   - Tests the interaction between initialization, template selection, and content plan generation

5. **Source Collection Integration** (`test_source_collection_integration.py`):
   - Tests the integration between cloud functions and the source collection service
   - Validates the workflow from content creation to source identification and evaluation
   - Tests error handling in the source collection process

6. **End-to-End Workflow** (`test_end_to_end_workflow.py`):
   - Tests the complete end-to-end workflow from content creation to review
   - Validates the interaction between different components of the system
   - Tests the content creation workflow with source collection
   - Tests the content creation workflow with mission pillar integration

7. **Error Handling Integration** (`test_error_handling_integration.py`):
   - Tests error handling in the integration between different components
   - Validates how the system handles errors in different parts of the workflow
   - Tests error handling for Firestore, Pub/Sub, and Vertex AI errors
   - Tests error handling for missing parameters and invalid inputs

## Running the Tests

### Running All Integration Tests

```bash
python test/integration/run_integration_tests.py
```

### Running Specific Test Modules

```bash
python test/integration/run_integration_tests.py --modules test_content_creation_workflow test_source_collection_workflow
```

### Running Cloud Function Integration Tests

```bash
python test/integration/run_integration_tests.py --cloud-functions
```

### Running Tests with Coverage Report

```bash
python test/integration/run_integration_tests.py --coverage
```

### Running Tests in Verbose Mode

```bash
python test/integration/run_integration_tests.py --verbose
```

### Listing Available Test Modules

```bash
python test/integration/run_integration_tests.py --list
```

## Test Design

The integration tests are designed to simulate real-world usage of the system. Each test module follows these principles:

1. **Sequential Testing**: Tests are designed to be run in sequence, with each test building on the results of the previous test.

2. **Mocking External Dependencies**: External dependencies like Firestore, Vertex AI, and Cloud Run services are mocked to enable testing without actual cloud resources.

3. **End-to-End Validation**: Each module includes an end-to-end test that calls all the other tests in sequence to validate the complete workflow.

4. **Realistic Data**: Tests use realistic data that mimics what would be used in production.

## Adding New Integration Tests

To add a new integration test:

1. Create a new test file following the naming convention `test_*.py`
2. Import the necessary modules and test fixtures
3. Create test cases using the `unittest` framework
4. Add an end-to-end test that calls all the other tests in sequence
5. Run the tests using the test runner

Example:

```python
import unittest
from unittest.mock import patch, MagicMock

class TestNewWorkflow(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        pass

    def test_step1(self):
        # Test implementation
        pass

    def test_step2(self):
        # Call test_step1 first to get its result
        result = self.test_step1()
        # Test implementation using result
        pass

    def test_end_to_end_workflow(self):
        # Call all tests in sequence
        self.test_step2()

if __name__ == '__main__':
    unittest.main()
```
