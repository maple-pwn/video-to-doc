"""Interactive command-line interface for video-to-doc."""

import sys
from pathlib import Path
import questionary
from questionary import Style
from .config import Config
from .pipeline import VideoToDocPipeline


# Custom style for better UI
custom_style = Style(
    [
        ("qmark", "fg:#673ab7 bold"),
        ("question", "bold"),
        ("answer", "fg:#f44336 bold"),
        ("pointer", "fg:#673ab7 bold"),
        ("highlighted", "fg:#673ab7 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
    ]
)


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║        🎥  Video to Documentation Converter  📝           ║
    ║                                                            ║
    ║        将视频自动转换为技术文档                              ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_url(url: str) -> bool:
    """Validate URL input."""
    if not url or len(url.strip()) == 0:
        return "URL 不能为空"
    if not (url.startswith("http://") or url.startswith("https://")):
        return "请输入有效的 URL (以 http:// 或 https:// 开头)"
    return True


def get_user_inputs():
    """Interactively collect user inputs."""

    questions = [
        {
            "type": "text",
            "name": "url",
            "message": "请输入视频 URL:",
            "validate": validate_url,
        },
        {
            "type": "text",
            "name": "output_name",
            "message": "自定义输出文件名 (按 Enter 跳过使用默认名称):",
            "default": "",
        },
        {
            "type": "select",
            "name": "whisper_mode",
            "message": "选择语音转录模式:",
            "choices": [
                {
                    "name": "☁️  API 模式 (推荐) - 快速准确，需要 API 调用",
                    "value": "api",
                },
                {"name": "💻 本地模式 - 免费但需要 GPU", "value": "local"},
            ],
            "default": "api",
        },
        {
            "type": "confirm",
            "name": "extract_frames",
            "message": "是否提取视频关键帧？",
            "default": True,
        },
    ]

    answers = questionary.prompt(questions, style=custom_style)

    if not answers:
        print("\n已取消操作")
        sys.exit(0)

    # Ask frame mode only if extracting frames
    if answers["extract_frames"]:
        frame_mode = questionary.select(
            "选择关键帧提取模式:",
            choices=[
                {"name": "⏱️  间隔模式 - 按固定时间间隔提取", "value": "interval"},
                {"name": "🎯 智能模式 - 基于场景变化智能提取", "value": "smart"},
            ],
            default="interval",
            style=custom_style,
        ).ask()
        answers["frame_mode"] = frame_mode
    else:
        answers["frame_mode"] = "interval"

    # Ask about cleanup
    answers["cleanup"] = questionary.confirm(
        "处理完成后是否清理临时文件？", default=True, style=custom_style
    ).ask()

    # Advanced settings
    advanced = questionary.confirm(
        "是否配置高级选项？", default=False, style=custom_style
    ).ask()

    if advanced:
        answers["api_key"] = questionary.text(
            "OpenAI API Key (按 Enter 使用 .env 配置):",
            default="",
        ).ask()

        answers["model"] = questionary.select(
            "选择 GPT 模型:",
            choices=[
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
            ],
            default="gpt-4-turbo-preview",
            style=custom_style,
        ).ask()

        answers["output_dir"] = questionary.text(
            "输出目录路径 (按 Enter 使用默认):",
            default="",
        ).ask()
    else:
        answers["api_key"] = ""
        answers["model"] = None
        answers["output_dir"] = ""

    return answers


def confirm_settings(answers: dict):
    """Display and confirm settings before processing."""
    print("\n" + "=" * 60)
    print("配置确认")
    print("=" * 60)
    print(f"视频 URL: {answers['url']}")
    print(f"输出文件名: {answers['output_name'] or '(自动生成)'}")
    print(f"转录模式: {answers['whisper_mode'].upper()}")
    print(f"提取关键帧: {'是' if answers['extract_frames'] else '否'}")
    if answers["extract_frames"]:
        print(f"提取模式: {answers['frame_mode']}")
    print(f"清理临时文件: {'是' if answers['cleanup'] else '否'}")

    if answers.get("model"):
        print(f"GPT 模型: {answers['model']}")
    if answers.get("output_dir"):
        print(f"输出目录: {answers['output_dir']}")

    print("=" * 60)

    return questionary.confirm(
        "\n确认开始处理？", default=True, style=custom_style
    ).ask()


def process_video(answers: dict):
    """Process video with given settings."""
    try:
        # Override config if API key provided
        if answers.get("api_key"):
            Config.set_openai_key(answers["api_key"])

        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            print(f"\n❌ 配置错误: {str(e)}")
            print("\n请在 .env 文件中设置 OPENAI_API_KEY 或使用高级选项指定")
            sys.exit(1)

        # Initialize pipeline
        output_dir = Path(answers["output_dir"]) if answers.get("output_dir") else None

        pipeline = VideoToDocPipeline(
            whisper_mode=answers["whisper_mode"],
            openai_model=answers.get("model"),
            output_dir=output_dir,
        )

        print("\n🚀 开始处理视频...\n")

        # Process video
        results = pipeline.process(
            url=answers["url"],
            output_name=answers["output_name"] if answers["output_name"] else None,
            extract_frames=answers["extract_frames"],
            frame_mode=answers["frame_mode"],
        )

        # Display results
        print("\n" + "=" * 60)
        print("✅ 处理完成！")
        print("=" * 60)
        print(f"📹 视频标题: {results['video_info']['title']}")
        print(f"📄 文档路径: {results['documentation_path']}")
        print(f"📊 元数据: {results['metadata_path']}")
        if results.get("frames"):
            print(f"🖼️  关键帧数: {len(results['frames'])} 张")
        print("=" * 60)

        # Cleanup if requested
        if answers["cleanup"]:
            print("\n🧹 清理临时文件...")
            pipeline.cleanup_temp_files()

        print("\n✨ 全部完成！\n")

        # Ask if user wants to process another video
        return questionary.confirm(
            "是否处理另一个视频？", default=False, style=custom_style
        ).ask()

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")

        retry = questionary.confirm(
            "是否重试？", default=False, style=custom_style
        ).ask()

        return retry


def main():
    """Main entry point for interactive CLI."""
    print_banner()

    while True:
        try:
            # Get user inputs
            answers = get_user_inputs()

            if not answers:
                break

            # Confirm settings
            if not confirm_settings(answers):
                print("\n已取消操作")
                continue

            # Process video
            continue_processing = process_video(answers)

            if not continue_processing:
                break

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            sys.exit(0)

    print("\n👋 再见！\n")


if __name__ == "__main__":
    main()
