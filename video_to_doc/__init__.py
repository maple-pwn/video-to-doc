"""Video to Documentation - Convert videos to technical documentation using AI."""

__version__ = "0.2.0"

from .config import Config
from .pipeline import VideoToDocPipeline

__all__ = ["VideoToDocPipeline", "Config", "__version__"]
