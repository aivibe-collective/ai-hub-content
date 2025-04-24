# Testing Guide

This document provides guidelines for testing the AI Hub Content Creation System, including unit tests, integration tests, and end-to-end tests.

## Table of Contents

- [Testing Environment Setup](#testing-environment-setup)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [End-to-End Tests](#end-to-end-tests)
- [Performance Tests](#performance-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

## Testing Environment Setup

### Prerequisites

- Python 3.9 or higher
- pytest 7.4.0 or higher
- pytest-cov 4.1.0 or higher
- A test Supabase project (separate from production)
- A Google Generative AI API key

### Installation

1. Install testing dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env.test` file with test environment variables:

```env
# Supabase Configuration (Test Environment)
SUPABASE_URL="https://your-test-project-id.supabase.co"
SUPABASE_KEY="your-test-supabase-key"

# Google Generative AI Configuration (Test Environment)
GOOGLE_GENAI_API_KEY="your-google-genai-api-key"

# Flask Configuration (Test Environment)
FLASK_SECRET_KEY="your-test-flask-secret-key"

# Test Configuration
TEST_MODE=True
TEST_OUTPUT_DIR="test_output"
```

3. Create test database tables:

```bash
# Run SQL scripts in your test Supabase project
# First create_tables.sql, then sql/create_content_versions_table.sql
```

### Test Directory Structure

```
test/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_supabase_client.py     # Tests for supabase_client.py
├── test_google_ai_client.py    # Tests for google_ai_client.py
├── test_content_workflow.py    # Tests for content_workflow_supabase.py
├── test_web_view.py            # Tests for web_view.py
├── test_integration.py         # Integration tests
└── test_end_to_end.py          # End-to-end tests
```

## Unit Tests

Unit tests focus on testing individual functions and classes in isolation.

### Writing Unit Tests

1. Create a test file for each module:

```python
# test/test_supabase_client.py
import os
import pytest
from unittest.mock import patch, MagicMock
from supabase_client import is_connected, get_content_by_id, update_content_status

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('supabase_client.supabase') as mock_supabase:
        yield mock_supabase

def test_is_connected(mock_supabase):
    """Test is_connected function."""
    # Arrange
    mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(count=10)
    
    # Act
    result = is_connected()
    
    # Assert
    assert result is True
    mock_supabase.table.assert_called_once_with('content_inventory')
    mock_supabase.table.return_value.select.assert_called_once_with('count', count='exact')

def test_get_content_by_id(mock_supabase):
    """Test get_content_by_id function."""
    # Arrange
    mock_content = {'content_id': 'LRN-BEG-001', 'title': 'Test Content'}
    mock_supabase.table.return_value.select.return_value.filter.return_value.execute.return_value = MagicMock(data=[mock_content])
    
    # Act
    result = get_content_by_id('LRN-BEG-001')
    
    # Assert
    assert result == mock_content
    mock_supabase.table.assert_called_once_with('content_inventory')
    mock_supabase.table.return_value.select.assert_called_once_with('*')
    mock_supabase.table.return_value.select.return_value.filter.assert_called_once_with('content_id', 'eq', 'LRN-BEG-001')

def test_update_content_status(mock_supabase):
    """Test update_content_status function."""
    # Arrange
    mock_supabase.table.return_value.update.return_value.filter.return_value.execute.return_value = MagicMock(data=[{'content_id': 'LRN-BEG-001', 'status': 'In Progress'}])
    
    # Act
    result = update_content_status('LRN-BEG-001', 'In Progress')
    
    # Assert
    assert result is True
    mock_supabase.table.assert_called_once_with('content_inventory')
    mock_supabase.table.return_value.update.assert_called_once()
    mock_supabase.table.return_value.update.return_value.filter.assert_called_once_with('content_id', 'eq', 'LRN-BEG-001')
```

2. Test with environment variables:

```python
# test/test_google_ai_client.py
import os
import pytest
from unittest.mock import patch, MagicMock
from google_ai_client import generate_content, generate_json

@pytest.fixture
def mock_genai():
    """Mock Google Generative AI client."""
    with patch('google_ai_client.genai') as mock_genai:
        yield mock_genai

@pytest.fixture
def mock_env_vars():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    os.environ['GOOGLE_GENAI_API_KEY'] = 'test-api-key'
    yield
    os.environ.clear()
    os.environ.update(original_env)

def test_generate_content(mock_genai, mock_env_vars):
    """Test generate_content function."""
    # Arrange
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = 'Generated content'
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Act
    result = generate_content('Test prompt', model_name='gemini-1.5-flash', temperature=0.7)
    
    # Assert
    assert result == 'Generated content'
    mock_genai.configure.assert_called_once_with(api_key='test-api-key')
    mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')
    mock_model.generate_content.assert_called_once()
```

3. Test exception handling:

```python
def test_generate_content_error(mock_genai, mock_env_vars):
    """Test generate_content function with error."""
    # Arrange
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception('API error')
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        generate_content('Test prompt')
    
    assert 'API error' in str(excinfo.value)
```

### Running Unit Tests

```bash
# Run all unit tests
pytest test/

# Run tests for a specific module
pytest test/test_supabase_client.py

# Run a specific test
pytest test/test_supabase_client.py::test_is_connected

# Run tests with verbose output
pytest -v test/

# Run tests with coverage
pytest --cov=. test/
```

## Integration Tests

Integration tests focus on testing the interaction between different components.

### Writing Integration Tests

1. Create fixtures for integration tests:

```python
# test/conftest.py
import os
import pytest
import uuid
from dotenv import load_dotenv
from supabase_client import supabase, get_content_by_id, update_content_status

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def test_content_id():
    """Generate a unique test content ID."""
    return f"TEST-{uuid.uuid4().hex[:8].upper()}"

@pytest.fixture
def test_content_item(test_content_id):
    """Create a test content item in Supabase."""
    # Create test content item
    content_item = {
        'content_id': test_content_id,
        'title': f'Test Content {test_content_id}',
        'section': 'Test Section',
        'status': 'Not Started'
    }
    
    # Insert into Supabase
    supabase.table('content_inventory').insert(content_item).execute()
    
    yield content_item
    
    # Clean up
    supabase.table('content_inventory').delete().filter('content_id', 'eq', test_content_id).execute()

@pytest.fixture
def test_session_id():
    """Generate a unique test session ID."""
    return str(uuid.uuid4())
```

2. Write integration tests:

```python
# test/test_integration.py
import os
import pytest
from supabase_client import get_content_by_id, update_content_status, log_prompt, log_generation_output
from google_ai_client import generate_content
from content_workflow_supabase import generate_content_for_item

def test_content_workflow_integration(test_content_item, test_session_id):
    """Test the integration between Supabase client and content workflow."""
    # Arrange
    content_id = test_content_item['content_id']
    
    # Act
    # 1. Update content status to In Progress
    update_result = update_content_status(content_id, 'In Progress')
    
    # 2. Log a prompt
    prompt_text = f"Generate content for {content_id}"
    prompt_id = log_prompt(
        session_id=test_session_id,
        prompt_type='content_generation',
        prompt_text=prompt_text,
        model='gemini-1.5-flash',
        temperature=0.7,
        content_id=content_id
    )
    
    # 3. Generate content
    content_text = "# Test Content\n\nThis is test content generated for integration testing."
    
    # 4. Log generation output
    output_result = log_generation_output(
        prompt_id=prompt_id,
        output_text=content_text,
        content_id=content_id,
        status='completed',
        metadata={'test': True}
    )
    
    # 5. Update content status to Completed
    complete_result = update_content_status(content_id, 'Completed')
    
    # Assert
    assert update_result is True
    assert prompt_id is not None
    assert output_result is True
    assert complete_result is True
    
    # Verify content status
    updated_content = get_content_by_id(content_id)
    assert updated_content is not None
    assert updated_content['status'] == 'Completed'
```

3. Test the full content generation workflow:

```python
def test_generate_content_for_item(test_content_item):
    """Test the generate_content_for_item function."""
    # Arrange
    content_id = test_content_item['content_id']
    output_dir = os.environ.get('TEST_OUTPUT_DIR', 'test_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Act
    success, output_file = generate_content_for_item(
        content_id=content_id,
        model_name='gemini-1.5-flash',
        temperature=0.7,
        output_dir=output_dir,
        force=True
    )
    
    # Assert
    assert success is True
    assert output_file is not None
    assert os.path.exists(output_file)
    
    # Verify content status
    updated_content = get_content_by_id(content_id)
    assert updated_content is not None
    assert updated_content['status'] == 'Completed'
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
```

### Running Integration Tests

```bash
# Run integration tests
pytest test/test_integration.py

# Run integration tests with verbose output
pytest -v test/test_integration.py

# Run integration tests with coverage
pytest --cov=. test/test_integration.py
```

## End-to-End Tests

End-to-end tests focus on testing the entire system from a user's perspective.

### Writing End-to-End Tests

1. Create fixtures for end-to-end tests:

```python
# test/conftest.py
import os
import pytest
import tempfile
from flask import Flask
from web_view import app as flask_app

@pytest.fixture
def app():
    """Create a Flask test client."""
    # Configure app for testing
    flask_app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'localhost.localdomain',
        'WTF_CSRF_ENABLED': False
    })
    
    # Create a test client
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client
```

2. Write end-to-end tests:

```python
# test/test_end_to_end.py
import os
import pytest
from flask import url_for

def test_home_page(app):
    """Test the home page."""
    # Act
    response = app.get('/')
    
    # Assert
    assert response.status_code == 200
    assert b'AI Hub Content Creation System' in response.data

def test_content_inventory_page(app):
    """Test the content inventory page."""
    # Act
    response = app.get('/content')
    
    # Assert
    assert response.status_code == 200
    assert b'Content Inventory' in response.data

def test_content_detail_page(app, test_content_item):
    """Test the content detail page."""
    # Arrange
    content_id = test_content_item['content_id']
    
    # Act
    response = app.get(f'/content/{content_id}')
    
    # Assert
    assert response.status_code == 200
    assert content_id.encode() in response.data
    assert test_content_item['title'].encode() in response.data

def test_content_edit_workflow(app, test_content_item):
    """Test the content editing workflow."""
    # Arrange
    content_id = test_content_item['content_id']
    
    # Act - Get edit page
    response = app.get(f'/content/{content_id}/edit')
    assert response.status_code == 200
    
    # Act - Submit edit form
    edit_data = {
        'content_text': '# Updated Content\n\nThis content has been updated.',
        'edit_notes': 'Updated for testing'
    }
    response = app.post(f'/content/{content_id}/edit', data=edit_data, follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    assert b'Content updated successfully' in response.data
    assert b'Updated Content' in response.data
```

3. Test the content generation workflow:

```python
def test_content_generation_workflow(app, test_content_item):
    """Test the content generation workflow."""
    # Arrange
    content_id = test_content_item['content_id']
    
    # Act - Get regenerate page
    response = app.get(f'/content/{content_id}/regenerate')
    assert response.status_code == 200
    
    # Act - Submit regenerate form
    regenerate_data = {
        'model': 'gemini-1.5-flash',
        'temperature': '0.7'
    }
    response = app.post(f'/content/{content_id}/regenerate', data=regenerate_data, follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    assert b'Content generation started' in response.data
```

### Running End-to-End Tests

```bash
# Run end-to-end tests
pytest test/test_end_to_end.py

# Run end-to-end tests with verbose output
pytest -v test/test_end_to_end.py

# Run end-to-end tests with coverage
pytest --cov=. test/test_end_to_end.py
```

## Performance Tests

Performance tests focus on measuring the performance of the system under different conditions.

### Writing Performance Tests

1. Create fixtures for performance tests:

```python
# test/conftest.py
import os
import pytest
import time
import statistics

@pytest.fixture
def performance_timer():
    """Measure execution time of a function."""
    class Timer:
        def __init__(self):
            self.times = []
        
        def measure(self, func, *args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            self.times.append(execution_time)
            return result, execution_time
        
        def stats(self):
            if not self.times:
                return {'min': 0, 'max': 0, 'avg': 0, 'median': 0, 'count': 0}
            return {
                'min': min(self.times),
                'max': max(self.times),
                'avg': statistics.mean(self.times),
                'median': statistics.median(self.times),
                'count': len(self.times)
            }
    
    return Timer()
```

2. Write performance tests:

```python
# test/test_performance.py
import os
import pytest
import time
from google_ai_client import generate_content
from supabase_client import get_content_inventory, get_content_by_id

def test_google_ai_performance(performance_timer):
    """Test the performance of Google AI content generation."""
    # Arrange
    prompt = "Write a short introduction to AI ethics."
    models = ['gemini-1.5-flash', 'gemini-2.0-flash']
    iterations = 3
    
    # Act & Assert
    for model in models:
        print(f"\nTesting model: {model}")
        for i in range(iterations):
            result, execution_time = performance_timer.measure(
                generate_content,
                prompt=prompt,
                model_name=model,
                temperature=0.7
            )
            print(f"  Iteration {i+1}: {execution_time:.2f}s")
            assert result is not None
        
        # Print statistics
        stats = performance_timer.stats()
        print(f"  Statistics: min={stats['min']:.2f}s, max={stats['max']:.2f}s, avg={stats['avg']:.2f}s, median={stats['median']:.2f}s")
        
        # Reset timer for next model
        performance_timer.times = []

def test_supabase_query_performance(performance_timer):
    """Test the performance of Supabase queries."""
    # Arrange
    iterations = 5
    
    # Act & Assert
    print("\nTesting get_content_inventory")
    for i in range(iterations):
        result, execution_time = performance_timer.measure(get_content_inventory)
        print(f"  Iteration {i+1}: {execution_time:.2f}s, {len(result)} items")
        assert result is not None
    
    # Print statistics
    stats = performance_timer.stats()
    print(f"  Statistics: min={stats['min']:.2f}s, max={stats['max']:.2f}s, avg={stats['avg']:.2f}s, median={stats['median']:.2f}s")
    
    # Reset timer for next test
    performance_timer.times = []
    
    # Test get_content_by_id
    if result:
        content_id = result[0]['content_id']
        print(f"\nTesting get_content_by_id with {content_id}")
        for i in range(iterations):
            result, execution_time = performance_timer.measure(get_content_by_id, content_id)
            print(f"  Iteration {i+1}: {execution_time:.2f}s")
            assert result is not None
        
        # Print statistics
        stats = performance_timer.stats()
        print(f"  Statistics: min={stats['min']:.2f}s, max={stats['max']:.2f}s, avg={stats['avg']:.2f}s, median={stats['median']:.2f}s")
```

### Running Performance Tests

```bash
# Run performance tests
pytest test/test_performance.py -v

# Run a specific performance test
pytest test/test_performance.py::test_google_ai_performance -v
```

## Test Coverage

Test coverage measures how much of your code is covered by tests.

### Measuring Test Coverage

```bash
# Run tests with coverage
pytest --cov=. test/

# Generate HTML coverage report
pytest --cov=. --cov-report=html test/

# Open coverage report
open htmlcov/index.html
```

### Coverage Goals

- **Unit Tests**: Aim for 80% or higher coverage
- **Integration Tests**: Focus on critical paths and edge cases
- **End-to-End Tests**: Cover main user workflows

## Continuous Integration

Continuous Integration (CI) automates the testing process when code changes are pushed to the repository.

### Setting Up GitHub Actions

1. Create a `.github/workflows/tests.yml` file:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create .env.test file
      run: |
        echo "SUPABASE_URL=${{ secrets.TEST_SUPABASE_URL }}" > .env.test
        echo "SUPABASE_KEY=${{ secrets.TEST_SUPABASE_KEY }}" >> .env.test
        echo "GOOGLE_GENAI_API_KEY=${{ secrets.TEST_GOOGLE_GENAI_API_KEY }}" >> .env.test
        echo "FLASK_SECRET_KEY=test-secret-key" >> .env.test
        echo "TEST_MODE=True" >> .env.test
        echo "TEST_OUTPUT_DIR=test_output" >> .env.test
    
    - name: Run tests
      run: |
        pytest --cov=. test/
    
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
```

2. Add secrets to your GitHub repository:
   - `TEST_SUPABASE_URL`: URL of your test Supabase project
   - `TEST_SUPABASE_KEY`: API key for your test Supabase project
   - `TEST_GOOGLE_GENAI_API_KEY`: Google Generative AI API key for testing

### Running Tests Locally Before Pushing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run specific test categories
pytest test/test_supabase_client.py test/test_google_ai_client.py
```
