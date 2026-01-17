"""Logging system for video-to-doc."""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for terminal output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # Format the message
        return super().format(record)


class Logger:
    """Enhanced logger for video-to-doc."""

    def __init__(
        self,
        name: str = "video_to_doc",
        log_file: Optional[Path] = None,
        verbose: bool = False,
    ):
        """
        Initialize logger.

        Args:
            name: Logger name
            log_file: Optional path to log file
            verbose: Enable verbose (DEBUG) logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        self.logger.handlers.clear()

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_formatter = ColoredFormatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)

    def step(self, message: str):
        """Log a processing step with special formatting."""
        self.info(f"🔄 {message}")

    def success(self, message: str):
        """Log success message."""
        self.info(f"✅ {message}")

    def failure(self, message: str):
        """Log failure message."""
        self.error(f"❌ {message}")

    def progress(self, message: str):
        """Log progress message."""
        self.info(f"⏳ {message}")

    def exception(self, message: str):
        """Log exception with traceback."""
        self.error(f"{message}\n{traceback.format_exc()}")


# Global logger instance
_default_logger: Optional[Logger] = None


def get_logger(
    name: str = "video_to_doc", log_file: Optional[Path] = None, verbose: bool = False
) -> Logger:
    """
    Get or create logger instance.

    Args:
        name: Logger name
        log_file: Optional path to log file
        verbose: Enable verbose logging

    Returns:
        Logger instance
    """
    global _default_logger

    if _default_logger is None:
        _default_logger = Logger(name, log_file, verbose)

    return _default_logger


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> Logger:
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose logging
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    global _default_logger

    if log_file is None:
        # Create default log file in logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"video_to_doc_{timestamp}.log"

    _default_logger = Logger("video_to_doc", log_file, verbose)
    return _default_logger
