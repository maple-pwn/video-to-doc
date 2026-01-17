"""Video to Documentation - Convert videos to technical documentation using AI."""

__version__ = "0.2.0"

from .pipeline import VideoToDocPipeline
from .config import Config

__all__ = ["VideoToDocPipeline", "Config", "__version__"]
