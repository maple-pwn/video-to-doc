"""Configuration management for video-to-doc."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    # Whisper Configuration
    WHISPER_MODE: str = os.getenv("WHISPER_MODE", "api")  # "api" or "local"

    # Directories
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "./temp"))

    # Video Processing
    KEYFRAME_INTERVAL: int = int(os.getenv("KEYFRAME_INTERVAL", "30"))
    MAX_KEYFRAMES: int = int(os.getenv("MAX_KEYFRAMES", "10"))

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file.")

        # Create directories if they don't exist
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def set_openai_key(cls, api_key: str) -> None:
        """Set OpenAI API key."""
        cls.OPENAI_API_KEY = api_key
