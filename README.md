# COSM C360 Tools

**COSM C360 Tools** is a user-friendly utility that converts specialized video output from COSM C360 cameras into standard MP4 files for easy viewing and analysis. No video editing experience required!

## 📋 Quick Start Guide for First-Time Users

Our interactive mode will guide you through the entire process with simple prompts and explanations.

### For Windows Users:

1. **Download the tool**: Download the latest release from our [GitHub Releases page](https://github.com/frontierkodiak/cosm-c360-tools/releases)
   - Download and extract the ZIP file to a folder of your choice

2. **Install prerequisites**:
   - [Download and install Python 3.10+](https://www.python.org/downloads/) (Make sure to check "Add Python to PATH" during installation)
   - [Download and install FFmpeg](https://ffmpeg.org/download.html) (Detailed instructions in the [User Guide](docs/USER_GUIDE.md#step-2-install-ffmpeg))

3. **Open Command Prompt**: 
   - Press `Win+R`, type `cmd`, and press Enter
   - Use `cd` to navigate to where you extracted the tool:
     ```
     cd C:\path\to\cosm-c360-tools
     ```

4. **Install dependencies and run**:
   ```
   pip install -r requirements.txt
   python cosmos.py --interactive
   ```

### For macOS/Linux Users:

1. **Install prerequisites**:
   ```bash
   # macOS (using Homebrew)
   brew install python ffmpeg

   # Ubuntu/Debian Linux
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg
   ```

2. **Download and run**:
   ```bash
   # Get the tool
   curl -L https://github.com/frontierkodiak/cosm-c360-tools/archive/refs/heads/main.zip -o cosm-c360-tools.zip
   unzip cosm-c360-tools.zip
   cd cosm-c360-tools-main

   # Install dependencies and run
   pip install -r requirements.txt
   python cosmos.py --interactive
   ```

## 💻 For Users with Limited System Resources

If you're working with high-resolution footage (8K+) on a computer with limited RAM (16GB or less), we recommend these settings:

1. When using interactive mode, select the **"low_memory"** or **"minimal"** quality mode
2. Enable the **"Low memory mode"** option when prompted
3. Consider processing to a lower output resolution (like 1080p) first to verify results

These settings will use a single processing thread which dramatically reduces memory usage but increases processing time.

## 🎥 What This Tool Does

- **Converts Specialized Camera Output**: Transforms tiled HEVC camera footage into standard MP4 files that you can play in any video player
- **Automatic Processing**: Handles complex tasks like parsing manifest files, validating footage segments, and assembling the final video
- **Multiple Resolution Options**: Create videos in various resolutions from 720p to full 8K+
- **Works Everywhere**: Compatible with Windows, macOS, and Linux

## 📚 Complete Documentation

- [User Guide](docs/USER_GUIDE.md) - Detailed installation and usage instructions for all platforms
- [Command Reference](docs/COMMAND_REFERENCE.md) - All available commands and options
- [Input Structure](docs/INPUT_STRUCTURE.md) - Details about the expected directory structure for camera footage

## ⚙️ Quality and Performance Settings

COSM C360 Tools offers several processing modes to balance quality, speed, and resource usage:

| Mode | Quality | Speed | Memory Usage | Recommended For |
|------|---------|-------|--------------|----------------|
| quality | Highest | Slowest | High | High-end systems, final outputs |
| balanced | Good | Medium | Medium | Most systems (default) |
| performance | Lower | Fast | Medium | Quick previews |
| low_memory | Good | Slow | Low | Systems with 8-16GB RAM |
| minimal | Lower | Slowest | Lowest | Systems with <8GB RAM |

## 🧰 Powerful Configuration System

Save your preferred settings for future use:
- **Save your configuration**: The tool will offer to save your settings automatically
- **Reload saved settings**: Quickly pick up where you left off
- **Override any option**: Fine-tune specific settings as needed

## 🖥️ System Requirements

- **Python**: 3.10 or higher
- **FFmpeg**: Required (installation instructions in the [User Guide](docs/USER_GUIDE.md))
- **Disk Space**: 10GB+ free space recommended (more for high-resolution output)
- **Memory**: 
  - 16GB+ RAM recommended for high-resolution processing
  - 8GB RAM workable with low_memory mode
  - 4GB RAM usable with minimal mode (very slow)

## 🔍 Getting Help

If you encounter any issues:
1. Run the self-test: `python cosmos.py --self-test`
2. Enable detailed logging: `python cosmos.py --log-level DEBUG`
3. Check our [User Guide](docs/USER_GUIDE.md#troubleshooting) for common solutions
4. Email support at [caleb@polli.ai](mailto:caleb@polli.ai)

## 📜 License

[MIT License](LICENSE)