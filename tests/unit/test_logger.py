"""Unit tests for logging module."""

from video_to_doc.logger import Logger, get_logger, setup_logging


class TestLogger:
    """Test Logger class."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = Logger("test_logger")
        assert logger.logger.name == "test_logger"

    def test_logger_with_file(self, temp_dir):
        """Test logger with file output."""
        log_file = temp_dir / "test.log"
        logger = Logger("test_logger", log_file=log_file)

        logger.info("Test message")

        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_logger_verbose_mode(self):
        """Test logger verbose mode."""
        logger = Logger("test_logger", verbose=True)
        # In verbose mode, level should be DEBUG
        import logging

        assert logger.logger.level == logging.DEBUG

    def test_logger_special_methods(self, temp_dir):
        """Test logger special methods."""
        log_file = temp_dir / "test.log"
        logger = Logger("test_logger", log_file=log_file)

        logger.step("Processing step")
        logger.success("Success message")
        logger.failure("Failure message")
        logger.progress("Progress update")

        content = log_file.read_text()
        assert "Processing step" in content
        assert "Success message" in content
        assert "Failure message" in content
        assert "Progress update" in content


class TestLoggerFunctions:
    """Test logger utility functions."""

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger()
        assert isinstance(logger, Logger)

    def test_setup_logging(self, temp_dir):
        """Test setup_logging function."""
        log_file = temp_dir / "setup.log"
        logger = setup_logging(verbose=True, log_file=log_file)

        assert isinstance(logger, Logger)
        assert log_file.parent.exists()
