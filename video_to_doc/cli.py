"""Command-line interface for video-to-doc."""

import click
import sys
from pathlib import Path
from .config import Config
from .pipeline import VideoToDocPipeline


@click.command()
@click.argument("url")
@click.option(
    "--output-name",
    "-o",
    help="Custom name for output files (without extension)",
    default=None,
)
@click.option("--no-frames", is_flag=True, help="Skip keyframe extraction")
@click.option(
    "--frame-mode",
    type=click.Choice(["interval", "smart"]),
    default="interval",
    help="Frame extraction mode: interval (regular intervals) or smart (scene detection)",
)
@click.option(
    "--whisper-mode",
    type=click.Choice(["api", "local"]),
    help="Whisper transcription mode (overrides .env setting)",
)
@click.option("--api-key", help="OpenAI API key (overrides .env setting)", default=None)
@click.option(
    "--model", help="OpenAI model to use for documentation generation", default=None
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for generated files",
    default=None,
)
@click.option(
    "--cleanup", is_flag=True, help="Clean up temporary files after processing"
)
def main(
    url: str,
    output_name: str,
    no_frames: bool,
    frame_mode: str,
    whisper_mode: str,
    api_key: str,
    model: str,
    output_dir: Path,
    cleanup: bool,
):
    """
    Video to Documentation Converter

    Convert videos from URLs into comprehensive technical documentation using AI.

    Example usage:

        video-to-doc https://www.youtube.com/watch?v=dQw4w9WgXcQ

        video-to-doc https://example.com/video.mp4 -o my_tutorial

        video-to-doc URL --whisper-mode local --no-frames
    """
    click.echo("=" * 60)
    click.echo("Video to Documentation Converter")
    click.echo("=" * 60)

    # Override config if API key provided
    if api_key:
        Config.set_openai_key(api_key)

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        click.echo(f"\n✗ Configuration error: {str(e)}", err=True)
        click.echo(
            "\nPlease set OPENAI_API_KEY in .env file or use --api-key option", err=True
        )
        sys.exit(1)

    # Initialize pipeline
    try:
        pipeline = VideoToDocPipeline(
            whisper_mode=whisper_mode, openai_model=model, output_dir=output_dir
        )

        # Process video
        results = pipeline.process(
            url=url,
            output_name=output_name,
            extract_frames=not no_frames,
            frame_mode=frame_mode,
        )

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("Results Summary")
        click.echo("=" * 60)
        click.echo(f"Video Title: {results['video_info']['title']}")
        click.echo(f"Documentation: {results['documentation_path']}")
        click.echo(f"Metadata: {results['metadata_path']}")
        if results["frames"]:
            click.echo(f"Keyframes: {len(results['frames'])} extracted")
        click.echo("=" * 60)

        # Cleanup if requested
        if cleanup:
            click.echo("\nCleaning up temporary files...")
            pipeline.cleanup_temp_files()

        click.echo("\n✓ Done!")

    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Video to Documentation CLI tools."""
    pass


@cli.command()
@click.argument("url")
def info(url: str):
    """Get video information without processing."""
    try:
        from .downloader import VideoDownloader

        downloader = VideoDownloader()
        info = downloader.get_video_info(url)

        click.echo("\nVideo Information:")
        click.echo(f"Title: {info['title']}")
        click.echo(f"Uploader: {info['uploader']}")
        click.echo(f"Duration: {info['duration']}s")
        if info.get("description"):
            click.echo(f"\nDescription:\n{info['description'][:200]}...")

    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"video-to-doc version {__version__}")


@cli.command()
@click.argument("url_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for generated files",
    default=None,
)
@click.option("--no-frames", is_flag=True, help="Skip keyframe extraction")
@click.option(
    "--frame-mode",
    type=click.Choice(["interval", "smart"]),
    default="interval",
    help="Frame extraction mode",
)
@click.option(
    "--whisper-mode",
    type=click.Choice(["api", "local"]),
    help="Whisper transcription mode",
)
@click.option("--api-key", help="OpenAI API key", default=None)
@click.option("--model", help="OpenAI model to use", default=None)
@click.option(
    "--max-concurrent",
    type=int,
    default=3,
    help="Maximum concurrent video processing",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue processing if one video fails",
)
@click.option(
    "--report",
    type=click.Path(path_type=Path),
    default=Path("batch_report.json"),
    help="Path to save batch processing report",
)
def batch(
    url_file: Path,
    output_dir: Path,
    no_frames: bool,
    frame_mode: str,
    whisper_mode: str,
    api_key: str,
    model: str,
    max_concurrent: int,
    continue_on_error: bool,
    report: Path,
):
    """
    Batch process multiple videos from a URL file.

    URL file should contain one URL per line. Lines starting with # are comments.

    Example:

        video-to-doc batch urls.txt

        video-to-doc batch urls.txt --max-concurrent 5 --report my_report.json
    """
    from .batch_processor import BatchProcessor

    click.echo("=" * 60)
    click.echo("Batch Video Processing")
    click.echo("=" * 60)

    # Override config if API key provided
    if api_key:
        Config.set_openai_key(api_key)

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        click.echo(f"\n✗ Configuration error: {str(e)}", err=True)
        click.echo(
            "\nPlease set OPENAI_API_KEY in .env file or use --api-key option", err=True
        )
        sys.exit(1)

    try:
        processor = BatchProcessor(
            whisper_mode=whisper_mode,
            openai_model=model,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            continue_on_error=continue_on_error,
        )

        summary = processor.process_from_file(
            url_file=url_file,
            extract_frames=not no_frames,
            frame_mode=frame_mode,
        )

        # Save report
        processor.save_report(summary, report)

        click.echo(f"\n✓ Batch processing complete!")
        click.echo(f"Report saved to: {report}")

    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
