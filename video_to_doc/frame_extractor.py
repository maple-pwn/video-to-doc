"""Extract keyframes from video for documentation illustrations."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from PIL import Image

from .config import Config


class FrameExtractor:
    """Extract keyframes from video files."""

    def __init__(
        self,
        interval: Optional[int] = None,
        max_frames: Optional[int] = None,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the frame extractor.

        Args:
            interval: Extract frame every N seconds. Defaults to Config.KEYFRAME_INTERVAL.
            max_frames: Maximum number of frames to extract. Defaults to Config.MAX_KEYFRAMES.
            output_dir: Directory to save frames. Defaults to Config.OUTPUT_DIR / 'frames'.
        """
        self.interval = interval or Config.KEYFRAME_INTERVAL
        self.max_frames = max_frames or Config.MAX_KEYFRAMES
        self.output_dir = output_dir or (Config.OUTPUT_DIR / "frames")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_frames(
        self, video_path: str, output_prefix: str = "frame"
    ) -> List[Dict[str, Any]]:
        """Extract keyframes from video.

        Args:
            video_path: Path to video file
            output_prefix: Prefix for output frame filenames

        Returns:
            List of dicts containing frame information
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(
            f"Extracting keyframes from video (interval: {self.interval}s, max: {self.max_frames})..."
        )

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise Exception(f"Failed to open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(
            f"Video info: {duration:.2f}s duration, {fps:.2f} FPS, {total_frames} total frames"
        )

        frame_interval = int(fps * self.interval)
        frames_info = []

        frame_count = 0
        saved_count = 0

        try:
            while cap.isOpened() and saved_count < self.max_frames:
                ret, frame = cap.read()

                if not ret:
                    break

                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps
                    output_path = (
                        self.output_dir
                        / f"{output_prefix}_{saved_count:03d}_{int(timestamp)}s.jpg"
                    )

                    # Save frame
                    cv2.imwrite(str(output_path), frame)

                    # Get frame dimensions
                    height, width = frame.shape[:2]

                    frames_info.append(
                        {
                            "index": saved_count,
                            "timestamp": timestamp,
                            "path": str(output_path),
                            "width": width,
                            "height": height,
                        }
                    )

                    print(
                        f"  Extracted frame {saved_count + 1}/{self.max_frames} at {timestamp:.2f}s"
                    )
                    saved_count += 1

                frame_count += 1

        finally:
            cap.release()

        print(f"Successfully extracted {len(frames_info)} keyframes")
        return frames_info

    def extract_smart_frames(
        self, video_path: str, output_prefix: str = "frame"
    ) -> List[Dict[str, Any]]:
        """Extract keyframes using scene change detection.

        This method detects significant changes in video content and extracts frames
        at those points, which can provide better representation of the video content.

        Args:
            video_path: Path to video file
            output_prefix: Prefix for output frame filenames

        Returns:
            List of dicts containing frame information
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print("Extracting keyframes using scene detection...")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise Exception(f"Failed to open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames_info = []

        prev_frame = None
        frame_count = 0
        saved_count = 0
        threshold = 30.0  # Scene change threshold

        try:
            while cap.isOpened() and saved_count < self.max_frames:
                ret, frame = cap.read()

                if not ret:
                    break

                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_score = np.mean(diff)

                    # If significant change detected
                    if diff_score > threshold:
                        timestamp = frame_count / fps
                        output_path = (
                            self.output_dir
                            / f"{output_prefix}_scene_{saved_count:03d}_{int(timestamp)}s.jpg"
                        )

                        cv2.imwrite(str(output_path), frame)

                        height, width = frame.shape[:2]

                        frames_info.append(
                            {
                                "index": saved_count,
                                "timestamp": timestamp,
                                "path": str(output_path),
                                "width": width,
                                "height": height,
                                "diff_score": float(diff_score),
                            }
                        )

                        print(
                            f"  Scene change detected at {timestamp:.2f}s (score: {diff_score:.2f})"
                        )
                        saved_count += 1

                prev_frame = gray
                frame_count += 1

        finally:
            cap.release()

        print(f"Successfully extracted {len(frames_info)} scene-based keyframes")
        return frames_info
