"""Main pipeline for video to documentation conversion."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
from .config import Config
from .downloader import VideoDownloader
from .transcriber import VideoTranscriber
from .frame_extractor import FrameExtractor
from .doc_generator import DocumentGenerator


class VideoToDocPipeline:
    """Complete pipeline for converting videos to documentation."""

    def __init__(
        self,
        whisper_mode: Optional[str] = None,
        openai_model: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the pipeline.

        Args:
            whisper_mode: "api" or "local" for transcription
            openai_model: OpenAI model for documentation generation
            output_dir: Output directory for results
        """
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.downloader = VideoDownloader()
        self.transcriber = VideoTranscriber(mode=whisper_mode)
        self.frame_extractor = FrameExtractor()
        self.doc_generator = DocumentGenerator(model=openai_model)

    def process(
        self,
        url: str,
        output_name: Optional[str] = None,
        extract_frames: bool = True,
        frame_mode: str = "interval",  # "interval" or "smart"
    ) -> Dict[str, Any]:
        """Process a video URL and generate documentation.

        Args:
            url: Video URL to process
            output_name: Custom name for output files
            extract_frames: Whether to extract keyframes
            frame_mode: Frame extraction mode ("interval" or "smart")

        Returns:
            Dict containing all processing results and file paths
        """
        print(f"\n{'=' * 60}")
        print(f"Starting video to documentation pipeline")
        print(f"{'=' * 60}\n")

        results = {
            "url": url,
            "success": False,
            "video_info": None,
            "transcript": None,
            "frames": [],
            "documentation_path": None,
            "metadata_path": None,
        }

        try:
            # Step 1: Download video
            print("\n[1/4] Downloading video...")
            video_info = self.downloader.download(url, output_filename=output_name)
            results["video_info"] = video_info
            print(f"✓ Downloaded: {video_info['title']}")

            # Step 2: Transcribe video
            print("\n[2/4] Transcribing video...")
            transcript_result = self.transcriber.transcribe(video_info["filepath"])
            results["transcript"] = transcript_result
            print(
                f"✓ Transcription completed ({transcript_result.get('language', 'unknown')} detected)"
            )

            # Step 3: Extract keyframes (optional)
            frames_info = []
            if extract_frames:
                print("\n[3/4] Extracting keyframes...")
                frame_prefix = output_name or Path(video_info["filepath"]).stem

                if frame_mode == "smart":
                    frames_info = self.frame_extractor.extract_smart_frames(
                        video_info["filepath"], output_prefix=frame_prefix
                    )
                else:
                    frames_info = self.frame_extractor.extract_frames(
                        video_info["filepath"], output_prefix=frame_prefix
                    )

                results["frames"] = frames_info
                print(f"✓ Extracted {len(frames_info)} keyframes")
            else:
                print("\n[3/4] Skipping frame extraction")

            # Step 4: Generate documentation
            print("\n[4/4] Generating technical documentation...")
            documentation = self.doc_generator.generate_documentation(
                video_info=video_info,
                transcript=transcript_result["text"],
                frames=frames_info,
            )

            # Save documentation
            doc_filename = f"{output_name or 'documentation'}.md"
            doc_path = self.output_dir / doc_filename
            self.doc_generator.save_documentation(documentation, doc_path)
            results["documentation_path"] = str(doc_path)
            print(f"✓ Documentation saved to: {doc_path}")

            # Save metadata
            metadata_path = (
                self.output_dir / f"{output_name or 'documentation'}_metadata.json"
            )
            self._save_metadata(results, metadata_path)
            results["metadata_path"] = str(metadata_path)

            results["success"] = True

            print(f"\n{'=' * 60}")
            print(f"✓ Pipeline completed successfully!")
            print(f"{'=' * 60}\n")

            return results

        except Exception as e:
            print(f"\n✗ Pipeline failed: {str(e)}")
            results["error"] = str(e)
            raise

    def _save_metadata(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save processing metadata to JSON file.

        Args:
            results: Processing results
            output_path: Path to save metadata
        """
        metadata = {
            "url": results.get("url"),
            "video_info": results.get("video_info"),
            "transcript_language": results.get("transcript", {}).get("language"),
            "frames_count": len(results.get("frames", [])),
            "documentation_path": results.get("documentation_path"),
            "success": results.get("success"),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Metadata saved to: {output_path}")

    def cleanup_temp_files(self) -> None:
        """Clean up temporary video and audio files."""
        import shutil

        if Config.TEMP_DIR.exists():
            shutil.rmtree(Config.TEMP_DIR)
            Config.TEMP_DIR.mkdir(parents=True, exist_ok=True)
            print("Temporary files cleaned up")
