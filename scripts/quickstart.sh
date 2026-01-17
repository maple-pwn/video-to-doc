#!/bin/bash
# Quick start script for Video to Documentation

set -e

echo "=================================="
echo "Video to Documentation - 快速启动"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg 未安装，正在尝试安装..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    else
        echo "❌ 请手动安装 ffmpeg: https://ffmpeg.org/download.html"
        exit 1
    fi
fi

echo "✅ 系统依赖检查完成"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# Install dependencies
echo "📥 安装依赖包..."
pip install --upgrade pip > /dev/null 2>&1
pip install -e . > /dev/null 2>&1

echo "✅ 依赖安装完成"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚙️  创建 .env 配置文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  请编辑 .env 文件，设置你的 OPENAI_API_KEY"
    echo ""
    read -p "现在要编辑 .env 文件吗? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ .env 配置文件已存在"
fi

echo ""
echo "=================================="
echo "🎉 安装完成！"
echo "=================================="
echo ""
echo "使用方式："
echo ""
echo "1️⃣  交互式模式 (推荐新手):"
echo "   video-to-doc-interactive"
echo ""
echo "2️⃣  Web 界面:"
echo "   video-to-doc-web"
echo ""
echo "3️⃣  命令行模式:"
echo "   video-to-doc <video-url>"
echo ""
echo "4️⃣  Docker 方式:"
echo "   docker-compose up web"
echo ""
echo "=================================="
echo ""
read -p "现在要启动交互式模式吗? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    video-to-doc-interactive
fi
