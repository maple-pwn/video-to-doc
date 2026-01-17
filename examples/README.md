# 示例文件

本目录包含 Video to Documentation 的使用示例。

## 📁 文件说明

### `sample_output.md`
完整的文档生成示例，展示了从技术教程视频生成的结构化文档的效果。

**特点：**
- 清晰的章节结构
- 关键帧引用
- 代码示例
- 时间戳标注
- 总结和推荐资源

### `sample_video_urls.txt`
批量处理的示例 URL 列表文件。

**使用方法：**
```bash
# 批量处理（功能即将推出）
video-to-doc batch sample_video_urls.txt
```

### `screenshots/`
Web UI 和交互式 CLI 的界面截图。

## 🎯 快速体验

### 1. 单个视频处理
```bash
# 使用交互式模式
video-to-doc-interactive

# 或使用命令行
video-to-doc https://www.youtube.com/watch?v=YOUR_VIDEO_ID -o my_doc
```

### 2. Web 界面
```bash
# 启动 Web UI
video-to-doc-web

# 在浏览器访问
# http://localhost:7860
```

### 3. 查看结果
处理完成后，在 `output/` 目录下查看：
- `*.md` - 生成的文档
- `*_metadata.json` - 元数据信息
- `frames/` - 提取的关键帧

## 💡 提示

1. **选择合适的视频**
   - 技术教程类视频效果最佳
   - 建议视频时长在 10-60 分钟
   - 确保视频有清晰的语音内容

2. **优化输出**
   - 使用智能模式提取关键帧
   - 选择 GPT-4 模型获得更好的文档质量
   - 提供描述性的输出文件名

3. **节省成本**
   - 短视频可使用 gpt-3.5-turbo
   - 考虑使用本地 Whisper 模式（如有 GPU）
   - 合理设置关键帧提取间隔

## 📚 更多示例

访问项目 Wiki 查看更多实际使用案例：
https://github.com/maple-pwn/video-to-doc/wiki
