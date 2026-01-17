"""Video downloader module using yt-dlp."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp
from .config import Config


class VideoDownloader:
    """Download videos from various platforms using yt-dlp."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the downloader.

        Args:
            output_dir: Directory to save downloaded videos. Defaults to Config.TEMP_DIR.
        """
        self.output_dir = output_dir or Config.TEMP_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(
        self, url: str, output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download video from URL.

        Args:
            url: Video URL to download
            output_filename: Optional custom filename (without extension)

        Returns:
            Dict containing video information and file path

        Raises:
            Exception: If download fails
        """
        if output_filename:
            output_template = str(self.output_dir / f"{output_filename}.%(ext)s")
        else:
            output_template = str(self.output_dir / "%(title)s.%(ext)s")

        ydl_opts = {
            "format": "best",
            "outtmpl": output_template,
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading video from: {url}")
                info = ydl.extract_info(url, download=True)

                # Get the actual filename
                if output_filename:
                    video_path = (
                        self.output_dir / f"{output_filename}.{info.get('ext', 'mp4')}"
                    )
                else:
                    video_path = (
                        self.output_dir / f"{info['title']}.{info.get('ext', 'mp4')}"
                    )

                return {
                    "title": info.get("title", "Unknown"),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", "Unknown"),
                    "upload_date": info.get("upload_date", ""),
                    "filepath": str(video_path),
                    "url": url,
                }

        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading.

        Args:
            url: Video URL

        Returns:
            Dict containing video metadata
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", "Unknown"),
                }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
