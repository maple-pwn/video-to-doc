"""Generate technical documentation from video content using AI."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import Config


class DocumentGenerator:
    """Generate technical documentation using OpenAI GPT-4."""

    def __init__(self, model: Optional[str] = None):
        """Initialize the document generator.

        Args:
            model: OpenAI model to use. Defaults to Config.OPENAI_MODEL.
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = model or Config.OPENAI_MODEL

    def generate_documentation(
        self,
        video_info: Dict[str, Any],
        transcript: str,
        frames: List[Dict[str, Any]],
        output_format: str = "markdown",
    ) -> str:
        """Generate technical documentation from video content.

        Args:
            video_info: Video metadata
            transcript: Video transcription text
            frames: List of extracted keyframe information
            output_format: Output format (currently only "markdown" supported)

        Returns:
            Generated documentation as a string
        """
        print("Generating technical documentation with AI...")

        # Prepare the prompt
        prompt = self._build_prompt(video_info, transcript, frames)

        # Generate documentation
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a technical writer specializing in creating clear, "
                            "comprehensive technical documentation. Your task is to analyze "
                            "video transcripts and generate well-structured technical documentation. "
                            "Focus on technical accuracy, clarity, and proper formatting."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )

            documentation = response.choices[0].message.content

            # Add metadata header
            doc_with_metadata = self._add_metadata(documentation, video_info)

            print("Documentation generated successfully!")
            return doc_with_metadata

        except Exception as e:
            raise Exception(f"Failed to generate documentation: {str(e)}")

    def _build_prompt(
        self, video_info: Dict[str, Any], transcript: str, frames: List[Dict[str, Any]]
    ) -> str:
        """Build the prompt for AI documentation generation.

        Args:
            video_info: Video metadata
            transcript: Video transcription
            frames: Keyframe information

        Returns:
            Formatted prompt string
        """
        prompt = f"""Please analyze the following video content and generate comprehensive technical documentation.

**Video Information:**
- Title: {video_info.get("title", "Unknown")}
- Duration: {video_info.get("duration", 0)} seconds
- Uploader: {video_info.get("uploader", "Unknown")}

**Video Transcript:**
{transcript}

**Available Screenshots:**
{len(frames)} keyframes have been extracted at various timestamps for illustrations.

**Documentation Requirements:**
1. Create a clear, well-structured technical document in Markdown format
2. Include the following sections:
   - Overview/Introduction
   - Key Concepts (if applicable)
   - Step-by-step guide or explanation
   - Technical details and specifications
   - Code examples (if the video contains code)
   - Best practices and tips
   - Conclusion/Summary
3. Use proper Markdown formatting with headers, lists, code blocks, etc.
4. Reference the timestamps where important information appears (e.g., "At 2:30, the presenter demonstrates...")
5. Suggest where screenshots should be placed with placeholders like: `![Screenshot description](frame_XXX.jpg)`
6. Focus on technical accuracy and clarity
7. Use professional technical writing style

Please generate the documentation now:
"""
        return prompt

    def _add_metadata(self, documentation: str, video_info: Dict[str, Any]) -> str:
        """Add metadata header to the documentation.

        Args:
            documentation: Generated documentation
            video_info: Video metadata

        Returns:
            Documentation with metadata header
        """
        metadata_header = f"""---
title: {video_info.get("title", "Video Documentation")}
source: {video_info.get("url", "Unknown")}
generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
duration: {video_info.get("duration", 0)}s
uploader: {video_info.get("uploader", "Unknown")}
---

"""
        return metadata_header + documentation

    def generate_summary(self, transcript: str, max_length: int = 500) -> str:
        """Generate a brief summary of the video content.

        Args:
            transcript: Video transcription
            max_length: Maximum length of summary in words

        Returns:
            Generated summary
        """
        print("Generating summary...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical writer. Generate concise, accurate summaries.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following video transcript in {max_length} words or less:\n\n{transcript}",
                    },
                ],
                temperature=0.5,
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def save_documentation(self, documentation: str, output_path: Path) -> None:
        """Save documentation to file.

        Args:
            documentation: Documentation content
            output_path: Path to save the documentation
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(documentation)

        print(f"Documentation saved to: {output_path}")
