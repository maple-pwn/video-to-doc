"""Configuration loader for video-to-doc."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .config import Config


class ConfigLoader:
    """Load and merge configuration from multiple sources."""

    DEFAULT_CONFIG_PATHS = [
        Path("config.yaml"),
        Path("~/.config/video-to-doc/config.yaml").expanduser(),
        Path("/etc/video-to-doc/config.yaml"),
    ]

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_path: Path to config file (optional)

        Returns:
            Configuration dictionary
        """
        config = cls._get_default_config()

        # Try to load from specified path or default paths
        paths_to_try = [config_path] if config_path else cls.DEFAULT_CONFIG_PATHS

        for path in paths_to_try:
            if path and path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        user_config = yaml.safe_load(f)
                        if user_config:
                            config = cls._merge_configs(config, user_config)
                    break
                except Exception as e:
                    print(f"Warning: Failed to load config from {path}: {e}")

        return config

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "openai": {
                "api_key": "",
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 4000,
            },
            "whisper": {
                "mode": "api",
                "model": "whisper-1",
                "language": "auto",
            },
            "download": {
                "format": "best",
                "max_filesize": 500,
                "subtitles": False,
                "proxy": "",
            },
            "keyframes": {
                "enabled": True,
                "mode": "interval",
                "interval": 30,
                "max_frames": 10,
                "quality": 90,
                "min_scene_score": 30,
            },
            "output": {
                "dir": "./output",
                "format": "markdown",
                "include_metadata": True,
                "include_frames": True,
                "cleanup_temp": True,
            },
            "temp": {
                "dir": "./temp",
                "keep_video": False,
                "keep_audio": False,
            },
            "processing": {
                "timeout": 3600,
                "retry_attempts": 3,
                "retry_delay": 5,
            },
            "cache": {
                "enabled": True,
                "dir": "./.cache",
                "ttl": 86400,
                "max_size": 1000,
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": "logs/video_to_doc.log",
                "max_size": 10,
                "backup_count": 5,
            },
            "documentation": {
                "language": "auto",
                "style": "technical",
                "include_timestamps": True,
                "include_code_blocks": True,
                "max_length": 10000,
                "sections": ["overview", "key_concepts", "examples", "summary"],
            },
            "batch": {
                "max_concurrent": 3,
                "continue_on_error": True,
                "report_file": "batch_report.json",
            },
            "advanced": {
                "user_agent": "",
                "cookies_file": "",
                "ffmpeg_path": "",
                "custom_prompt": "",
            },
        }

    @classmethod
    def _merge_configs(
        cls, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = cls._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    @classmethod
    def apply_to_env(cls, config: Dict[str, Any]):
        """
        Apply configuration to environment/Config class.

        Args:
            config: Configuration dictionary
        """
        # Apply OpenAI config
        if config.get("openai", {}).get("api_key"):
            Config.set_openai_key(config["openai"]["api_key"])

        # Apply other configs through environment variables or Config class
        # This can be extended as needed

    @classmethod
    def create_example_config(cls, path: Path):
        """
        Create an example configuration file.

        Args:
            path: Path to create config file
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read the example file
        example_path = Path(__file__).parent.parent / "config.yaml.example"
        if example_path.exists():
            import shutil

            shutil.copy(example_path, path)
        else:
            # Generate from default config
            config = cls._get_default_config()
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Example configuration created at: {path}")
        print("   Edit this file to customize your settings")


# Global configuration instance
_global_config: Optional[Dict[str, Any]] = None


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load global configuration.

    Args:
        config_path: Optional path to config file

    Returns:
        Configuration dictionary
    """
    global _global_config

    if _global_config is None:
        _global_config = ConfigLoader.load(config_path)

    return _global_config


def get_config(key: str = None, default: Any = None) -> Any:
    """
    Get configuration value.

    Args:
        key: Configuration key (dot-notation supported, e.g., 'openai.model')
        default: Default value if key not found

    Returns:
        Configuration value
    """
    config = load_config()

    if key is None:
        return config

    # Support dot notation
    keys = key.split(".")
    value = config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value
