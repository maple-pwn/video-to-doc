# Video to Documentation

自动将视频内容转换为技术文档的开源工具,使用AI技术进行视频转录和文档生成。

## 功能特性

- 支持从各种视频平台下载视频(YouTube、Bilibili等,基于yt-dlp)
- 使用OpenAI Whisper进行高质量语音转文字
  - 支持云端API模式(精确快速)
  - 支持本地模型模式(免费但需要GPU)
- 智能提取视频关键帧作为文档配图
  - 定时间隔提取模式
  - 场景变化智能检测模式
- 使用GPT-4自动生成结构化技术文档
- 输出Markdown格式,易于编辑和发布
- 命令行工具,使用简单

## 安装

### 前置要求

- Python 3.8+
- ffmpeg (用于视频处理)

### 安装ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并安装
```

### 安装项目

```bash
# 克隆仓库
git clone https://github.com/maple-pwn/video-to-doc.git
cd video-to-doc

# 创建虚拟环境(推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 如果需要使用本地Whisper模型
pip install -e ".[whisper]"

# 开发依赖(可选)
pip install -e ".[dev]"
```

## 配置

创建 `.env` 文件并配置以下参数:

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件
nano .env
```

必需配置:

```
# OpenAI API密钥(必需)
OPENAI_API_KEY=your_openai_api_key_here

# 使用的GPT模型
OPENAI_MODEL=gpt-4-turbo-preview

# Whisper模式: api(云端) 或 local(本地)
WHISPER_MODE=api
```

可选配置:

```
# 输出目录
OUTPUT_DIR=./output
TEMP_DIR=./temp

# 关键帧提取间隔(秒)
KEYFRAME_INTERVAL=30
# 最多提取关键帧数量
MAX_KEYFRAMES=10
```

## 使用方法

### 基本用法

```bash
# 处理YouTube视频
video-to-doc https://www.youtube.com/watch?v=VIDEO_ID

# 指定输出文件名
video-to-doc https://example.com/video.mp4 -o my_tutorial

# 不提取关键帧
video-to-doc URL --no-frames

# 使用智能场景检测提取关键帧
video-to-doc URL --frame-mode smart

# 使用本地Whisper模型
video-to-doc URL --whisper-mode local
```

### 高级选项

```bash
video-to-doc [URL] [选项]

选项:
  -o, --output-name TEXT      自定义输出文件名
  --no-frames                 跳过关键帧提取
  --frame-mode [interval|smart]  帧提取模式
  --whisper-mode [api|local]  Whisper转录模式
  --api-key TEXT              临时指定OpenAI API密钥
  --model TEXT                指定GPT模型
  --output-dir PATH           指定输出目录
  --cleanup                   处理完成后清理临时文件
  --help                      显示帮助信息
```

### 其他命令

```bash
# 查看视频信息(不下载处理)
video-to-doc info https://www.youtube.com/watch?v=VIDEO_ID

# 查看版本
video-to-doc version
```

## 工作流程

1. **视频下载**: 使用yt-dlp从URL下载视频
2. **语音转录**: 通过Whisper将视频音频转换为文字
3. **关键帧提取**: 从视频中提取代表性画面
4. **文档生成**: 使用GPT-4分析内容并生成结构化文档
5. **输出保存**: 保存Markdown文档、关键帧图片和元数据

## 输出结果

处理完成后,在输出目录会生成:

```
output/
├── documentation.md              # 生成的技术文档
├── documentation_metadata.json   # 处理过程元数据
└── frames/                       # 提取的关键帧图片
    ├── frame_000_30s.jpg
    ├── frame_001_60s.jpg
    └── ...
```

## 编程接口

除了CLI工具,也可以在Python代码中使用:

```python
from video_to_doc import VideoToDocPipeline

# 初始化pipeline
pipeline = VideoToDocPipeline(
    whisper_mode="api",
    openai_model="gpt-4-turbo-preview"
)

# 处理视频
results = pipeline.process(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    output_name="my_tutorial",
    extract_frames=True,
    frame_mode="smart"
)

print(f"文档已保存到: {results['documentation_path']}")
```

## 示例

### 处理技术教程视频

```bash
video-to-doc https://www.youtube.com/watch?v=dQw4w9WgXcQ \
  -o python_tutorial \
  --frame-mode smart \
  --cleanup
```

生成的文档示例:

```markdown
---
title: Python FastAPI 完整教程
source: https://www.youtube.com/watch?v=...
generated: 2024-01-15 10:30:00
duration: 1820s
uploader: Tech Channel
---

# Python FastAPI 完整教程

## 概述

本教程介绍了如何使用FastAPI构建现代Web API...

## 关键概念

### 1. FastAPI基础

在2:30,讲师展示了基本的FastAPI应用结构:

![FastAPI基本结构](frame_000_150s.jpg)

...
```

## 支持的视频平台

基于yt-dlp,支持1000+视频平台,包括:

- YouTube
- Bilibili
- Vimeo
- Twitter/X
- TikTok
- 等等...

完整列表见: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 故障排除

### 常见问题

**Q: 提示"OPENAI_API_KEY is required"**

A: 确保在.env文件中设置了有效的OpenAI API密钥

**Q: 视频下载失败**

A: 检查网络连接,某些平台可能需要代理或cookies

**Q: 本地Whisper模型运行缓慢**

A: 本地模型需要较强的计算能力,建议使用GPU或改用API模式

**Q: 生成的文档质量不佳**

A: 可以尝试使用更高级的GPT模型,如gpt-4而不是gpt-3.5-turbo

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black video_to_doc/
flake8 video_to_doc/
```

## 贡献

欢迎贡献! 请遵循以下步骤:

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [OpenCV](https://opencv.org/) - 视频处理库
- [OpenAI GPT-4](https://openai.com/) - 文档生成AI

项目链接: https://github.com/maple-pwn/video-to-doc

## 更新日志

### v0.1.0 (2024-01-15)

- 初始版本发布
- 支持视频下载、转录、关键帧提取和文档生成
- CLI工具实现
- 支持API和本地Whisper模式
