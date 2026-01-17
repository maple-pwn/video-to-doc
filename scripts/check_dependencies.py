#!/usr/bin/env python3
"""Check if all dependencies are correctly installed."""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python version {version.major}.{version.minor} is too old")
        print("   Required: Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_system_dependencies():
    """Check system dependencies."""
    import subprocess

    dependencies = {
        "ffmpeg": "ffmpeg -version",
    }

    all_ok = True
    for name, command in dependencies.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"✅ {name} installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name} not found")
            all_ok = False

    return all_ok


def check_python_packages():
    """Check Python packages."""
    required_packages = [
        "click",
        "openai",
        "cv2",
        "PIL",
        "requests",
        "bs4",
        "dotenv",
        "tqdm",
        "questionary",
        "gradio",
        "yt_dlp",
    ]

    package_names = {
        "cv2": "opencv-python",
        "PIL": "pillow",
        "bs4": "beautifulsoup4",
        "dotenv": "python-dotenv",
        "yt_dlp": "yt-dlp",
    }

    all_ok = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            display_name = package_names.get(package, package)
            print(f"✅ {display_name}")
        except ImportError:
            display_name = package_names.get(package, package)
            print(f"❌ {display_name} not installed")
            all_ok = False

    return all_ok


def check_env_file():
    """Check .env file."""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and configure your API keys")
        return False

    print("✅ .env file exists")

    # Check if OPENAI_API_KEY is set
    with open(env_path) as f:
        content = f.read()
        if "OPENAI_API_KEY=" in content:
            if "your_" not in content and "sk-" in content:
                print("✅ OPENAI_API_KEY configured")
                return True
            else:
                print("⚠️  OPENAI_API_KEY not configured properly")
                return False

    print("⚠️  OPENAI_API_KEY not found in .env")
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Video to Documentation - Dependency Check")
    print("=" * 60)
    print()

    print("Checking Python version...")
    python_ok = check_python_version()
    print()

    print("Checking system dependencies...")
    system_ok = check_system_dependencies()
    print()

    print("Checking Python packages...")
    packages_ok = check_python_packages()
    print()

    print("Checking configuration...")
    env_ok = check_env_file()
    print()

    print("=" * 60)
    if python_ok and system_ok and packages_ok and env_ok:
        print("✅ All checks passed! You're ready to go!")
        print()
        print("Start using:")
        print("  video-to-doc-interactive  # Interactive mode")
        print("  video-to-doc-web          # Web UI")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        if not system_ok:
            print("Install system dependencies:")
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  macOS: brew install ffmpeg")
        if not packages_ok:
            print()
            print("Install Python packages:")
            print("  pip install -e .")
        if not env_ok:
            print()
            print("Configure environment:")
            print("  cp .env.example .env")
            print("  # Edit .env and set your OPENAI_API_KEY")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
