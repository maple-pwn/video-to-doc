"""Web UI for video-to-doc using Gradio."""

from typing import List, Optional, Tuple

import gradio as gr

from .config import Config
from .pipeline import VideoToDocPipeline

# Global pipeline instance
pipeline = None


def initialize_pipeline(api_key: str, model: str) -> str:
    """Initialize the processing pipeline."""
    global pipeline

    try:
        if api_key:
            Config.set_openai_key(api_key)

        Config.validate()

        pipeline = VideoToDocPipeline(
            whisper_mode="api",  # Default to API mode for web UI
            openai_model=model if model else None,
        )

        return "✅ 配置成功！可以开始处理视频了。"
    except ValueError as e:
        return f"❌ 配置错误: {str(e)}\n请确保提供有效的 OpenAI API Key。"
    except Exception as e:
        return f"❌ 初始化失败: {str(e)}"


def process_video_ui(
    url: str,
    output_name: str,
    whisper_mode: str,
    extract_frames: bool,
    frame_mode: str,
    api_key: str,
    model: str,
    progress=gr.Progress(),
) -> Tuple[str, str, Optional[str], Optional[List]]:
    """Process video through the web UI."""

    if not pipeline:
        init_msg = initialize_pipeline(api_key, model)
        if "❌" in init_msg:
            return init_msg, "", None, None

    if not url:
        return "❌ 请输入视频 URL", "", None, None

    try:
        progress(0, desc="开始下载视频...")

        # Update pipeline settings
        pipeline.whisper_mode = whisper_mode
        if model:
            pipeline.openai_model = model

        progress(0.2, desc="正在转录音频...")

        # Process video
        results = pipeline.process(
            url=url,
            output_name=output_name if output_name else None,
            extract_frames=extract_frames,
            frame_mode=frame_mode,
        )

        progress(1.0, desc="处理完成！")

        # Read the generated documentation
        doc_path = results["documentation_path"]
        with open(doc_path, "r", encoding="utf-8") as f:
            documentation = f.read()

        # Format metadata for display
        video_info = results.get("video_info", {})

        metadata_display = f"""
## 处理结果

**视频标题:** {video_info.get("title", "N/A")}
**上传者:** {video_info.get("uploader", "N/A")}
**时长:** {video_info.get("duration", 0)} 秒
**提取关键帧:** {len(results.get("frames", []))} 张

**文档路径:** {doc_path}
**元数据文件:** {results.get("metadata_path", "N/A")}
"""

        # Get frame images
        frame_images = None
        if results.get("frames"):
            frame_images = [
                str(f) for f in results["frames"][:10]
            ]  # Limit to 10 frames

        success_msg = f"✅ 处理成功！\n\n视频《{video_info.get('title', 'Unknown')}》已转换为文档。"

        return success_msg, documentation, metadata_display, frame_images

    except Exception as e:
        error_msg = f"❌ 处理失败: {str(e)}"
        return error_msg, "", None, None


def get_video_info_ui(url: str) -> str:
    """Get video information without processing."""
    if not url:
        return "❌ 请输入视频 URL"

    try:
        from .downloader import VideoDownloader

        downloader = VideoDownloader()
        info = downloader.get_video_info(url)

        info_text = f"""
## 视频信息

**标题:** {info.get("title", "N/A")}
**上传者:** {info.get("uploader", "N/A")}
**时长:** {info.get("duration", 0)} 秒
**观看次数:** {info.get("view_count", "N/A")}

**描述:**
{info.get("description", "N/A")[:500]}...
"""
        return info_text

    except Exception as e:
        return f"❌ 获取视频信息失败: {str(e)}"


def create_ui():
    """Create Gradio interface."""

    with gr.Blocks(
        title="Video to Documentation",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px;
            margin: auto;
        }
        """,
    ) as demo:
        gr.Markdown(
            """
        # 🎥 Video to Documentation Converter
        
        将视频自动转换为结构化技术文档
        
        支持 YouTube、Bilibili 等 1000+ 视频平台
        """
        )

        with gr.Tabs():
            # Main processing tab
            with gr.Tab("📝 视频转文档"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 基本设置")

                        url_input = gr.Textbox(
                            label="视频 URL",
                            placeholder="https://www.youtube.com/watch?v=...",
                            lines=1,
                        )

                        output_name = gr.Textbox(
                            label="输出文件名（可选）",
                            placeholder="留空自动生成",
                            lines=1,
                        )

                        whisper_mode = gr.Radio(
                            choices=[("API 模式 (推荐)", "api"), ("本地模式", "local")],
                            value="api",
                            label="语音转录模式",
                        )

                        extract_frames = gr.Checkbox(label="提取关键帧", value=True)

                        frame_mode = gr.Radio(
                            choices=[("间隔模式", "interval"), ("智能模式", "smart")],
                            value="interval",
                            label="关键帧提取模式",
                        )

                        gr.Markdown("### 高级设置")

                        api_key_input = gr.Textbox(
                            label="OpenAI API Key",
                            placeholder="留空使用 .env 配置",
                            type="password",
                            lines=1,
                        )

                        model_select = gr.Dropdown(
                            choices=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
                            value="gpt-4-turbo-preview",
                            label="GPT 模型",
                        )

                        process_btn = gr.Button(
                            "🚀 开始处理", variant="primary", size="lg"
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("### 处理结果")

                        status_output = gr.Textbox(
                            label="状态", lines=3, interactive=False
                        )

                        metadata_output = gr.Markdown(label="元数据")

                        doc_output = gr.Textbox(
                            label="生成的文档", lines=20, interactive=False
                        )

                        frames_gallery = gr.Gallery(
                            label="提取的关键帧", columns=5, height="auto"
                        )

                # Process button click handler
                process_btn.click(
                    fn=process_video_ui,
                    inputs=[
                        url_input,
                        output_name,
                        whisper_mode,
                        extract_frames,
                        frame_mode,
                        api_key_input,
                        model_select,
                    ],
                    outputs=[
                        status_output,
                        doc_output,
                        metadata_output,
                        frames_gallery,
                    ],
                )

            # Video info tab
            with gr.Tab("ℹ️ 视频信息查询"):
                with gr.Row():
                    with gr.Column():
                        info_url = gr.Textbox(
                            label="视频 URL",
                            placeholder="https://www.youtube.com/watch?v=...",
                            lines=1,
                        )
                        info_btn = gr.Button("🔍 获取信息", variant="primary")

                    with gr.Column():
                        info_output = gr.Markdown(label="视频信息")

                info_btn.click(
                    fn=get_video_info_ui, inputs=[info_url], outputs=[info_output]
                )

            # Help tab
            with gr.Tab("❓ 使用说明"):
                gr.Markdown(
                    """
                ## 使用指南
                
                ### 快速开始
                
                1. **输入视频 URL** - 支持 YouTube、Bilibili 等 1000+ 平台
                2. **配置 API Key** - 在高级设置中输入 OpenAI API Key（或使用 .env 配置）
                3. **选择转录模式**:
                   - **API 模式**: 快速准确，需要 OpenAI API 调用
                   - **本地模式**: 免费但需要 GPU 支持
                4. **点击开始处理** - 等待处理完成
                
                ### 功能说明
                
                #### 关键帧提取
                - **间隔模式**: 按固定时间间隔提取画面
                - **智能模式**: 基于场景变化智能提取关键画面
                
                #### 支持的平台
                - YouTube
                - Bilibili
                - Vimeo
                - Twitter/X
                - TikTok
                - 以及 1000+ 其他平台
                
                ### 输出内容
                - **技术文档** (Markdown 格式)
                - **关键帧图片**
                - **处理元数据** (JSON 格式)
                
                ### 注意事项
                - 确保网络连接正常
                - API 模式需要有效的 OpenAI API Key
                - 本地模式需要较强的计算能力（推荐使用 GPU）
                - 视频时长越长，处理时间越长
                
                ### 环境配置
                
                如果使用 `.env` 文件配置，请创建项目根目录下的 `.env` 文件：
                
                ```
                OPENAI_API_KEY=your_api_key_here
                OPENAI_MODEL=gpt-4-turbo-preview
                WHISPER_MODE=api
                ```
                """
                )

        gr.Markdown(
            """
        ---
        
        💡 **提示:** 首次使用建议先在"视频信息查询"标签页测试 URL 是否有效
        
        📚 [项目文档](https://github.com/maple-pwn/video-to-doc) | 🐛 [报告问题](https://github.com/maple-pwn/video-to-doc/issues)
        """
        )

    return demo


def main():
    """Launch the web UI."""
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)


if __name__ == "__main__":
    main()
