# Performance Tests for Agentic AI Content Creation System

This directory contains performance tests for the Agentic AI Content Creation System. These tests measure the system's performance under various load conditions and ensure it meets performance requirements.

## Test Categories

The performance tests are organized into the following categories:

1. **Load Tests**: Measure the system's behavior under expected load conditions.
2. **Stress Tests**: Measure the system's behavior under extreme load conditions.
3. **Endurance Tests**: Measure the system's behavior over extended periods.
4. **Scalability Tests**: Measure how the system scales with increasing load.
5. **API Response Time Tests**: Measure the response time of individual API endpoints.

## Test Metrics

The performance tests measure the following metrics:

1. **Response Time**: Time taken to respond to a request.
2. **Throughput**: Number of requests processed per unit time.
3. **Error Rate**: Percentage of requests that result in errors.
4. **Resource Utilization**: CPU, memory, and network usage.
5. **Concurrency**: Number of simultaneous users/requests the system can handle.

## Running the Tests

### Prerequisites

1. Install performance testing dependencies:

   ```bash
   pip install -r test/performance/requirements.txt
   ```

2. Set up the test environment:

   ```bash
   python test/performance/setup_perf_env.py
   ```

### Running All Performance Tests

```bash
python test/performance/run_performance_tests.py
```

### Running Specific Test Categories

```bash
python test/performance/run_performance_tests.py --category load
python test/performance/run_performance_tests.py --category stress
python test/performance/run_performance_tests.py --category endurance
python test/performance/run_performance_tests.py --category scalability
python test/performance/run_performance_tests.py --category api_response
```

### Running Tests with Specific Parameters

```bash
# Run load tests with 100 concurrent users
python test/performance/run_performance_tests.py --category load --users 100

# Run endurance tests for 1 hour
python test/performance/run_performance_tests.py --category endurance --duration 3600

# Run API response time tests with 10 iterations
python test/performance/run_performance_tests.py --category api_response --iterations 10
```

## Test Reports

Performance test reports are generated in the `test/performance/reports` directory. The reports include:

1. **Summary Report**: Overall performance metrics.
2. **Detailed Report**: Detailed performance metrics for each test.
3. **Charts**: Visual representation of performance metrics.
4. **Logs**: Detailed logs of test execution.

## Performance Requirements

The system should meet the following performance requirements:

1. **Response Time**:
   - API endpoints should respond within 1 second for 95% of requests.
   - Content generation should complete within 30 seconds for 95% of requests.

2. **Throughput**:
   - The system should handle at least 100 requests per minute.

3. **Error Rate**:
   - The error rate should be less than 1% under normal load.
   - The error rate should be less than 5% under peak load.

4. **Concurrency**:
   - The system should support at least 50 concurrent users.

5. **Resource Utilization**:
   - CPU utilization should be less than 80% under normal load.
   - Memory utilization should be less than 80% under normal load.

## Adding New Performance Tests

To add a new performance test:

1. Create a new test file in the appropriate category directory.
2. Implement the test using the performance testing framework.
3. Add the test to the test runner.
4. Update the test documentation.

Example:

```python
from test.performance.framework import PerformanceTest

class MyPerformanceTest(PerformanceTest):
    def setup(self):
        # Set up test resources
        pass
        
    def run(self):
        # Run the test
        pass
        
    def cleanup(self):
        # Clean up test resources
        pass
        
    def report(self):
        # Generate test report
        pass
```
