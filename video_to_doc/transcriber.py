"""Video transcription module supporting both OpenAI Whisper API and local models."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Config


class VideoTranscriber:
    """Transcribe video audio to text using Whisper."""

    def __init__(self, mode: Optional[str] = None):
        """Initialize the transcriber.

        Args:
            mode: "api" for OpenAI Whisper API, "local" for local model.
                  Defaults to Config.WHISPER_MODE.
        """
        self.mode = mode or Config.WHISPER_MODE

        if self.mode == "api":
            from openai import OpenAI

            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        elif self.mode == "local":
            try:
                import whisper

                self.model = whisper.load_model("base")
            except ImportError:
                raise ImportError(
                    "Local Whisper model requires 'openai-whisper' package. "
                    "Install with: pip install 'video-to-doc[whisper]'"
                )
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'api' or 'local'")

    def transcribe(self, video_path: str) -> Dict[str, Any]:
        """Transcribe video to text.

        Args:
            video_path: Path to video file

        Returns:
            Dict containing transcription text and metadata
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Transcribing video using {self.mode} mode...")

        if self.mode == "api":
            return self._transcribe_api(video_path)
        else:
            return self._transcribe_local(video_path)

    def _transcribe_api(self, video_path: Path) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API.

        Args:
            video_path: Path to video file

        Returns:
            Dict containing transcription result
        """
        try:
            with open(video_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="verbose_json"
                )

            return {
                "text": transcript.text,
                "language": (
                    transcript.language
                    if hasattr(transcript, "language")
                    else "unknown"
                ),
                "duration": (
                    transcript.duration if hasattr(transcript, "duration") else 0
                ),
                "mode": "api",
            }
        except Exception as e:
            raise Exception(f"API transcription failed: {str(e)}")

    def _transcribe_local(self, video_path: Path) -> Dict[str, Any]:
        """Transcribe using local Whisper model.

        Args:
            video_path: Path to video file

        Returns:
            Dict containing transcription result
        """
        try:
            result = self.model.transcribe(str(video_path))

            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "mode": "local",
            }
        except Exception as e:
            raise Exception(f"Local transcription failed: {str(e)}")

    def transcribe_with_timestamps(self, video_path: str) -> Dict[str, Any]:
        """Transcribe with timestamp information.

        Args:
            video_path: Path to video file

        Returns:
            Dict containing transcription with timestamps
        """
        if self.mode == "local":
            result = self._transcribe_local(Path(video_path))
            return {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result["language"],
            }
        else:
            # API mode doesn't provide detailed segments by default
            # For timestamp support, we'd need to use local mode
            print(
                "Warning: Detailed timestamps require local mode. Returning basic transcription."
            )
            result = self._transcribe_api(Path(video_path))
            return {
                "text": result["text"],
                "segments": [],
                "language": result["language"],
            }
