"""Unit tests for configuration module."""

from pathlib import Path

import pytest

from video_to_doc.config import Config


class TestConfig:
    """Test Config class."""

    def test_default_values(self):
        """Test default configuration values."""
        assert Config.OUTPUT_DIR == Path("./output")
        assert Config.TEMP_DIR == Path("./temp")
        assert Config.KEYFRAME_INTERVAL == 30
        assert Config.MAX_KEYFRAMES == 10

    def test_set_openai_key(self):
        """Test setting OpenAI API key."""
        test_key = "sk-test-1234567890"
        Config.set_openai_key(test_key)
        assert Config.OPENAI_API_KEY == test_key

    def test_validate_with_valid_key(self, mock_env_vars):
        """Test validation with valid API key."""
        Config.validate()  # Should not raise

    def test_validate_without_key(self, monkeypatch):
        """Test validation without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        Config.OPENAI_API_KEY = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            Config.validate()


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        from video_to_doc.config_loader import ConfigLoader

        config = ConfigLoader.load()
        assert isinstance(config, dict)
        assert "openai" in config
        assert "whisper" in config
        assert "output" in config

    def test_merge_configs(self):
        """Test configuration merging."""
        from video_to_doc.config_loader import ConfigLoader

        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}, "e": 4}

        result = ConfigLoader._merge_configs(base, override)

        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4

    def test_get_config_with_dot_notation(self, sample_config, monkeypatch):
        """Test getting config value with dot notation."""
        import video_to_doc.config_loader as config_module
        from video_to_doc.config_loader import get_config

        # Set global config using monkeypatch
        monkeypatch.setattr(config_module, "_global_config", sample_config)

        assert get_config("openai.model") == "gpt-4-turbo-preview"
        assert get_config("whisper.mode") == "api"
        assert get_config("nonexistent.key", "default") == "default"
