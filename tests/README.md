# Tests for Video to Documentation

This directory contains the test suite for the video-to-doc project.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/                # Unit tests
│   ├── test_config.py
│   ├── test_logger.py
│   └── test_exceptions.py
├── integration/         # Integration tests
└── fixtures/            # Test fixtures and data
```

## Running Tests

### Install Test Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=video_to_doc

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::TestConfig::test_default_values
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run tests that don't require API keys
pytest -m "not requires_api"
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=video_to_doc --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Markers

- `unit`: Unit tests (fast, no external dependencies)
- `integration`: Integration tests (may require external services)
- `slow`: Tests that take longer to run
- `requires_api`: Tests that require API keys
- `requires_ffmpeg`: Tests that require ffmpeg

## Writing Tests

### Basic Test Structure

```python
import pytest
from video_to_doc import SomeModule

class TestSomeModule:
    """Test SomeModule class."""
    
    def test_something(self):
        """Test description."""
        result = SomeModule.do_something()
        assert result == expected
```

### Using Fixtures

```python
def test_with_temp_dir(temp_dir):
    """Test using temporary directory."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()

def test_with_mock_env(mock_env_vars):
    """Test with mocked environment variables."""
    # OPENAI_API_KEY is already set
    from video_to_doc.config import Config
    Config.validate()
```

### Testing Exceptions

```python
def test_exception_raised():
    """Test that exception is raised."""
    with pytest.raises(ValueError, match="error message"):
        some_function_that_raises()
```

## Continuous Integration

Tests are automatically run on GitHub Actions for:
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Multiple operating systems (Ubuntu, macOS)

See `.github/workflows/tests.yml` for CI configuration.

## Coverage Goals

- Aim for >80% code coverage
- Focus on testing critical paths and error handling
- Mock external API calls to avoid costs and rate limits

## Best Practices

1. **Keep tests fast**: Mock external dependencies
2. **Test one thing**: Each test should verify one behavior
3. **Use descriptive names**: Test names should describe what they test
4. **Clean up resources**: Use fixtures for setup/teardown
5. **Avoid hardcoded values**: Use fixtures and constants

## Debugging Tests

```bash
# Run with print statements visible
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "config"
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
