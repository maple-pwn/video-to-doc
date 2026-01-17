"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_video_url():
    """Return a sample video URL for testing."""
    # Use a short public domain video for testing
    return "https://www.youtube.com/watch?v=jNQXAC9IVRw"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    monkeypatch.setenv("WHISPER_MODE", "api")


@pytest.fixture
def sample_config():
    """Return a sample configuration dictionary."""
    return {
        "openai": {
            "api_key": "sk-test-key",
            "model": "gpt-4-turbo-preview",
        },
        "whisper": {
            "mode": "api",
        },
        "output": {
            "dir": "./test_output",
        },
    }


@pytest.fixture
def sample_video_info():
    """Return sample video information."""
    return {
        "title": "Test Video",
        "uploader": "Test Uploader",
        "duration": 120,
        "description": "This is a test video",
        "url": "https://example.com/test.mp4",
    }
