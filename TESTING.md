# Testing Guide

This guide explains how to run and write tests for the Telegram Backup Android App.

## Overview

The project uses **pytest** as the testing framework with comprehensive unit and integration tests.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_config.py      # Config module tests
│   ├── managers/           # Manager tests
│   │   ├── test_account_manager.py
│   │   └── test_progress_manager.py
│   ├── utils/              # Utility tests
│   │   └── test_logger.py
│   └── screens/            # Screen tests (future)
└── integration/            # Integration tests (future)
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Specific module
pytest tests/unit/test_config.py

# Specific test class
pytest tests/unit/test_config.py::TestConfig

# Specific test function
pytest tests/unit/test_config.py::TestConfig::test_config_defaults
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
# View at: htmlcov/index.html
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Tests Matching a Pattern

```bash
pytest tests/ -k "config"
```

## Writing Tests

### Basic Test Structure

```python
# tests/unit/test_example.py
import pytest
from app.module import MyClass


class TestMyClass:
    """Test MyClass functionality"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        obj = MyClass()
        result = obj.method()
        assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py` and can be used in any test:

```python
def test_with_temp_dir(temp_dir):
    """Test using temporary directory fixture"""
    # temp_dir is automatically created and cleaned up
    file_path = os.path.join(temp_dir, 'test.txt')
    # ... test code ...
```

Available fixtures:
- `temp_dir` - Temporary directory that's cleaned up after test
- `mock_config` - Mocked Config with temp directories
- `mock_telegram_client` - Mocked Telegram client
- `sample_account` - Sample account data
- `sample_transfer` - Sample transfer data

### Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await async_function()
    assert result == expected
```

### Using Mocks

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    """Test with mocked dependency"""
    mock_client = MagicMock()
    mock_client.method.return_value = 'expected'
    
    result = function_using_client(mock_client)
    assert result == 'expected'
    mock_client.method.assert_called_once()
```

## Best Practices

### 1. Test Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names: `test_save_progress_creates_file`

### 2. Test Organization
- One test class per module/class being tested
- Group related tests together
- Keep tests independent (no shared state)

### 3. Assertions
- Use clear, specific assertions
- One logical assertion per test (when possible)
- Use pytest's assertion rewriting (just use `assert`)

### 4. Coverage Goals
- Aim for >80% code coverage
- Focus on critical business logic
- Don't obsess over 100% coverage

### 5. Test Independence
- Tests should not depend on each other
- Use fixtures for setup/teardown
- Clean up resources in fixtures

### 6. Testing UI Code
- Mock Kivy dependencies when testing business logic
- Keep business logic separate from UI code
- Test UI interactions with integration tests

## Continuous Integration

Tests run automatically on:
- Pull requests to master
- Pushes to master
- Manual workflow dispatch

See `.github/workflows/test.yml` for CI configuration.

## Common Issues

### Import Errors
If you get import errors, ensure:
1. Test dependencies are installed: `pip install -r requirements-test.txt`
2. App dependencies are installed: `pip install -r requirements_full.txt`
3. You're running tests from the project root

### Fixture Not Found
Fixtures are defined in `tests/conftest.py`. Make sure:
1. The fixture is defined
2. You're using the correct fixture name
3. The conftest.py file is in the tests directory

### Async Test Failures
For async tests:
1. Use `@pytest.mark.asyncio` decorator
2. Make test function async: `async def test_...`
3. Use `await` for async calls

## Examples

See existing tests for examples:
- `tests/unit/test_config.py` - Simple unit tests
- `tests/unit/managers/test_progress_manager.py` - Tests with file I/O
- `tests/unit/utils/test_logger.py` - Tests with mocking

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Pytest-cov](https://pytest-cov.readthedocs.io/)
- [Pytest-mock](https://pytest-mock.readthedocs.io/)
