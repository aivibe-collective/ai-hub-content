# Code Coverage for Cloud Functions

This document provides information about the code coverage for the cloud functions in the Agentic AI Content Creation System.

## Overview

We've implemented comprehensive unit tests for the cloud functions to address the critical 0% code coverage issue. The tests cover:

- `cloud_function/main.py`: Core functions for content creation workflow
- `cloud_function/utils.py`: Utility functions for Firestore, Pub/Sub, and Vertex AI

## Running the Tests

You can run the tests and generate a coverage report using the provided script:

```bash
# Run all cloud function tests and generate a coverage report
python3 test/run_coverage.py

# Run specific test modules
python3 test/run_coverage.py --module test/test_cloud_function_main.py

# Generate a coverage report without opening it in a browser
python3 test/run_coverage.py --no-browser
```

## Test Coverage

The tests cover the following functionality:

### Main Functions

1. **initialize_content_creation**:
   - Valid input with successful initialization
   - Missing parameters
   - No JSON data
   - Error in storing metadata

2. **select_template**:
   - Successful template selection
   - No matching template found

3. **generate_content_plan**:
   - Successful content plan generation
   - Error in Vertex AI API call

### Utility Functions

1. **store_content_metadata**:
   - Successful metadata storage
   - Firestore error

2. **publish_event**:
   - Successful event publishing
   - Pub/Sub error

3. **call_vertex_ai**:
   - Successful API call
   - API error
   - Non-JSON response

## CI/CD Integration

We've set up a GitHub Actions workflow to run the tests and generate coverage reports automatically:

- Runs on pushes and pull requests that affect cloud functions
- Runs weekly to ensure coverage doesn't degrade
- Generates a coverage badge
- Creates a coverage report artifact

## Improving Coverage

To further improve coverage:

1. **Add More Test Cases**:
   - Test edge cases and error conditions
   - Test with different input parameters

2. **Add Integration Tests**:
   - Test the interaction between different functions
   - Test the complete workflow

3. **Add Mocking for External Services**:
   - Mock Firestore, Pub/Sub, and Vertex AI
   - Test with different response scenarios

## Coverage Goals

- **Short-term Goal**: Achieve at least 80% coverage for critical functions
- **Medium-term Goal**: Achieve at least 90% overall coverage
- **Long-term Goal**: Maintain at least 95% coverage with comprehensive tests
