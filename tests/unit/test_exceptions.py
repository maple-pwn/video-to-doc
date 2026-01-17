"""Unit tests for exceptions module."""

import pytest

from video_to_doc.exceptions import (
    APIKeyError,
    DownloadError,
    FFmpegError,
    InvalidURLError,
    TranscriptionError,
    VideoToDocException,
    handle_exception,
)


class TestExceptions:
    """Test custom exceptions."""

    def test_base_exception_with_message(self):
        """Test base exception with message only."""
        exc = VideoToDocException("Test error")
        assert str(exc) == "Test error"

    def test_base_exception_with_suggestion(self):
        """Test base exception with suggestion."""
        exc = VideoToDocException("Test error", "Try this fix")
        assert "Test error" in str(exc)
        assert "Try this fix" in str(exc)

    def test_invalid_url_error(self):
        """Test InvalidURLError."""
        exc = InvalidURLError("http://invalid.url")
        assert "invalid.url" in str(exc)
        assert "suggestion" in str(exc).lower()

    def test_api_key_error(self):
        """Test APIKeyError."""
        exc = APIKeyError()
        assert "API key" in str(exc)
        assert "OPENAI_API_KEY" in str(exc)

    def test_ffmpeg_error(self):
        """Test FFmpegError."""
        exc = FFmpegError()
        assert "ffmpeg" in str(exc)
        assert "install" in str(exc).lower()

    def test_download_error(self):
        """Test DownloadError."""
        exc = DownloadError("Download failed", "Check connection")
        assert "Download failed" in str(exc)
        assert "Check connection" in str(exc)

    def test_transcription_error(self):
        """Test TranscriptionError."""
        exc = TranscriptionError("Transcription failed")
        assert "Transcription failed" in str(exc)


class TestExceptionHandler:
    """Test exception handling utilities."""

    def test_handle_video_to_doc_exception(self):
        """Test handling VideoToDocException."""
        exc = VideoToDocException("Test error", "Test suggestion")
        result = handle_exception(exc)

        assert "Test error" in result
        assert "Test suggestion" in result

    def test_handle_connection_error(self):
        """Test handling ConnectionError."""
        exc = ConnectionError("Connection failed")
        result = handle_exception(exc)

        assert "Network error" in result or "Connection failed" in result

    def test_handle_keyboard_interrupt(self):
        """Test handling KeyboardInterrupt."""
        exc = KeyboardInterrupt()
        result = handle_exception(exc)

        assert "cancelled" in result.lower()

    def test_handle_unknown_exception(self):
        """Test handling unknown exception."""
        exc = RuntimeError("Unknown error")
        result = handle_exception(exc)

        assert "Unexpected error" in result
        assert "github.com" in result.lower()
