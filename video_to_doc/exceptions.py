"""Custom exceptions for video-to-doc."""


class VideoToDocException(Exception):
    """Base exception for video-to-doc."""

    def __init__(self, message: str, suggestion: str = ""):
        """
        Initialize exception.

        Args:
            message: Error message
            suggestion: Suggestion for fixing the error
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)

    def __str__(self):
        """String representation."""
        if self.suggestion:
            return f"{self.message}\n💡 Suggestion: {self.suggestion}"
        return self.message


class DownloadError(VideoToDocException):
    """Error during video download."""

    pass


class TranscriptionError(VideoToDocException):
    """Error during audio transcription."""

    pass


class FrameExtractionError(VideoToDocException):
    """Error during keyframe extraction."""

    pass


class DocumentGenerationError(VideoToDocException):
    """Error during documentation generation."""

    pass


class ConfigurationError(VideoToDocException):
    """Error in configuration."""

    pass


class DependencyError(VideoToDocException):
    """Error with missing or incorrect dependencies."""

    pass


class InvalidURLError(VideoToDocException):
    """Invalid video URL."""

    def __init__(self, url: str):
        super().__init__(
            f"Invalid or unsupported video URL: {url}",
            "Make sure the URL is correct and the platform is supported by yt-dlp",
        )


class APIKeyError(VideoToDocException):
    """OpenAI API key error."""

    def __init__(self):
        super().__init__(
            "OpenAI API key is not set or invalid",
            "Set OPENAI_API_KEY in your .env file or use --api-key option",
        )


class FFmpegError(VideoToDocException):
    """ffmpeg not found or error."""

    def __init__(self):
        super().__init__(
            "ffmpeg is not installed or not found in PATH",
            "Install ffmpeg:\n"
            "  Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/download.html",
        )


class InsufficientStorageError(VideoToDocException):
    """Not enough disk space."""

    def __init__(self, required_mb: int, available_mb: int):
        super().__init__(
            f"Insufficient storage: need {required_mb}MB, only {available_mb}MB available",
            "Free up disk space or specify a different output directory",
        )


class ProcessingTimeoutError(VideoToDocException):
    """Processing timeout."""

    def __init__(self, step: str, timeout: int):
        super().__init__(
            f"Processing timeout in {step} after {timeout} seconds",
            "Try with a shorter video or increase timeout settings",
        )


class NetworkError(VideoToDocException):
    """Network connection error."""

    def __init__(self, details: str = ""):
        super().__init__(
            f"Network error: {details}", "Check your internet connection and try again"
        )


def handle_exception(exc: Exception, logger=None) -> str:
    """
    Handle exception and return user-friendly error message.

    Args:
        exc: Exception to handle
        logger: Optional logger instance

    Returns:
        User-friendly error message
    """
    if isinstance(exc, VideoToDocException):
        error_msg = str(exc)
        if logger:
            logger.error(error_msg)
        return error_msg

    # Handle common exceptions
    error_mapping = {
        ConnectionError: NetworkError("Connection failed"),
        TimeoutError: NetworkError("Request timed out"),
        FileNotFoundError: VideoToDocException(
            str(exc), "Check if the file path is correct"
        ),
        PermissionError: VideoToDocException(
            str(exc), "Check file permissions or run with appropriate privileges"
        ),
        KeyboardInterrupt: VideoToDocException("Operation cancelled by user", ""),
    }

    for exc_type, mapped_exc in error_mapping.items():
        if isinstance(exc, exc_type):
            error_msg = str(mapped_exc)
            if logger:
                logger.error(error_msg)
            return error_msg

    # Unknown exception
    error_msg = f"Unexpected error: {str(exc)}"
    if logger:
        logger.exception("Unexpected error occurred")

    return f"{error_msg}\n💡 Suggestion: Please report this issue at https://github.com/maple-pwn/video-to-doc/issues"
