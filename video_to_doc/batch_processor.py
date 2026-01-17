"""Batch processing for multiple videos."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .pipeline import VideoToDocPipeline
from .logger import get_logger


class BatchProcessor:
    """Process multiple videos in batch."""

    def __init__(
        self,
        whisper_mode: str = "api",
        openai_model: Optional[str] = None,
        output_dir: Optional[Path] = None,
        max_concurrent: int = 3,
        continue_on_error: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize batch processor.

        Args:
            whisper_mode: Whisper transcription mode
            openai_model: OpenAI model to use
            output_dir: Output directory
            max_concurrent: Maximum concurrent processes
            continue_on_error: Continue processing if one video fails
            verbose: Enable verbose logging
        """
        self.pipeline = VideoToDocPipeline(
            whisper_mode=whisper_mode, openai_model=openai_model, output_dir=output_dir
        )
        self.max_concurrent = max_concurrent
        self.continue_on_error = continue_on_error
        self.logger = get_logger(verbose=verbose)

        self.results = []
        self.errors = []

    def process_from_file(
        self, url_file: Path, extract_frames: bool = True, frame_mode: str = "interval"
    ) -> Dict[str, Any]:
        """
        Process videos from a URL list file.

        Args:
            url_file: Path to file containing video URLs (one per line)
            extract_frames: Whether to extract keyframes
            frame_mode: Frame extraction mode

        Returns:
            Batch processing results
        """
        urls = self._read_url_file(url_file)
        return self.process_urls(urls, extract_frames, frame_mode)

    def process_urls(
        self, urls: List[str], extract_frames: bool = True, frame_mode: str = "interval"
    ) -> Dict[str, Any]:
        """
        Process multiple video URLs.

        Args:
            urls: List of video URLs
            extract_frames: Whether to extract keyframes
            frame_mode: Frame extraction mode

        Returns:
            Batch processing results
        """
        self.logger.info(f"Starting batch processing of {len(urls)} videos")
        self.logger.info(f"Max concurrent: {self.max_concurrent}")

        start_time = datetime.now()
        self.results = []
        self.errors = []

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(
                    self._process_single_video, url, extract_frames, frame_mode
                ): url
                for url in urls
            }

            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                completed += 1

                try:
                    result = future.result()
                    if result["status"] == "success":
                        self.results.append(result)
                        self.logger.success(
                            f"[{completed}/{len(urls)}] Completed: {url}"
                        )
                    else:
                        self.errors.append(result)
                        self.logger.failure(f"[{completed}/{len(urls)}] Failed: {url}")
                except Exception as e:
                    error_result = {
                        "url": url,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    self.errors.append(error_result)
                    self.logger.error(f"[{completed}/{len(urls)}] Error: {url} - {e}")

                    if not self.continue_on_error:
                        self.logger.warning("Stopping batch processing due to error")
                        break

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "total": len(urls),
            "success": len(self.results),
            "failed": len(self.errors),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "results": self.results,
            "errors": self.errors,
        }

        self.logger.info(f"\nBatch Processing Summary:")
        self.logger.info(f"  Total: {summary['total']}")
        self.logger.success(f"  Success: {summary['success']}")
        self.logger.failure(f"  Failed: {summary['failed']}")
        self.logger.info(f"  Duration: {duration:.1f}s")

        return summary

    def _process_single_video(
        self, url: str, extract_frames: bool, frame_mode: str
    ) -> Dict[str, Any]:
        """
        Process a single video.

        Args:
            url: Video URL
            extract_frames: Whether to extract keyframes
            frame_mode: Frame extraction mode

        Returns:
            Processing result
        """
        try:
            self.logger.progress(f"Processing: {url}")

            results = self.pipeline.process(
                url=url,
                output_name=None,
                extract_frames=extract_frames,
                frame_mode=frame_mode,
            )

            return {
                "url": url,
                "status": "success",
                "video_title": results["video_info"]["title"],
                "documentation_path": str(results["documentation_path"]),
                "metadata_path": str(results["metadata_path"]),
                "frames_count": len(results.get("frames", [])),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "url": url,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _read_url_file(self, url_file: Path) -> List[str]:
        """
        Read URLs from file.

        Args:
            url_file: Path to URL file

        Returns:
            List of URLs
        """
        if not url_file.exists():
            raise FileNotFoundError(f"URL file not found: {url_file}")

        urls = []
        with open(url_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    urls.append(line)

        if not urls:
            raise ValueError(f"No valid URLs found in {url_file}")

        self.logger.info(f"Loaded {len(urls)} URLs from {url_file}")
        return urls

    def save_report(self, summary: Dict[str, Any], report_file: Path):
        """
        Save batch processing report.

        Args:
            summary: Batch processing summary
            report_file: Path to save report
        """
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.logger.success(f"Report saved to: {report_file}")
