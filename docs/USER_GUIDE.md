# COSM C360 Tools - User Guide

This user guide provides comprehensive, step-by-step instructions for using COSM C360 Tools to convert specialized COSM camera footage into standard MP4 video files that can be played on any device. This guide is designed for all users, including those with no technical experience.

## 📋 Quick Start Summary

1. Install **Python 3.10+** and **FFmpeg** (detailed instructions below)
2. Download the COSM C360 Tools and extract to a folder
3. Open Terminal/Command Prompt
4. Navigate to the tool's folder
5. Run `pip install -r requirements.txt` to install dependencies
6. Run `python cosmos.py --interactive` to start the interactive mode
7. Follow the on-screen prompts to convert your camera footage

## 🛠️ Detailed Installation Guide

### Step 1: Install Python (Version 3.10 or higher)

#### Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **VERY IMPORTANT**: Check the box that says "Add Python to PATH" during installation
   ![Add Python to PATH checkbox](https://docs.python.org/3/_images/win_installer.png)
4. Click "Install Now"
5. After installation, verify by opening Command Prompt (search for "cmd" in the Start menu) and typing:
   ```
   python --version
   ```
   You should see a version number like `Python 3.10.x` or higher

#### macOS:
1. Install Homebrew (if not already installed):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Follow any on-screen instructions to complete the installation
   
2. Install Python using Homebrew:
   ```
   brew install python
   ```
   
3. Verify by opening Terminal and typing:
   ```
   python3 --version
   ```

#### Linux (Ubuntu/Debian):
1. Open Terminal and run:
   ```
   sudo apt update
   sudo apt install python3 python3-pip
   ```
   
2. Verify with:
   ```
   python3 --version
   ```

### Step 2: Install FFmpeg

#### Windows:
1. **Option 1: Easy Installer (Recommended for beginners)**
   - Download and run the [gyan.dev FFmpeg release](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
   - Extract the ZIP file to a location like `C:\ffmpeg`
   - Copy the full path to the `bin` folder (e.g., `C:\ffmpeg\bin`)

2. Add FFmpeg to your PATH:
   - In Windows search, type "environment variables" and select "Edit the system environment variables"
   - Click the "Environment Variables..." button
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and paste the path to the `bin` folder you copied earlier
   - Click "OK" on all dialogs to save the changes
   
3. **Option 2: Alternative Method**
   - Download the FFmpeg build from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Follow the same steps to extract and add to PATH

4. Verify installation by opening a **new** Command Prompt window and typing:
   ```
   ffmpeg -version
   ```

#### macOS:
1. Using Homebrew:
   ```
   brew install ffmpeg
   ```

2. Verify with:
   ```
   ffmpeg -version
   ```

#### Linux (Ubuntu/Debian):
1. Install with:
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

2. Verify with:
   ```
   ffmpeg -version
   ```

### Step 3: Download and Set Up COSM C360 Tools

1. **Download the tool**:
   - Visit the [GitHub releases page](https://github.com/frontierkodiak/cosm-c360-tools/releases)
   - Download the latest ZIP file (`cosm-c360-tools.zip` or similar)
   - Extract the ZIP file to a folder of your choice

2. **Install Python dependencies**:
   - Open Terminal (macOS/Linux) or Command Prompt (Windows)
   - Navigate to the folder where you extracted the tool:
     ```
     # Example on Windows (change to your actual path)
     cd C:\Users\YourName\Downloads\cosm-c360-tools
     
     # Example on macOS/Linux (change to your actual path)
     cd ~/Downloads/cosm-c360-tools
     ```
   - Install the required packages:
     ```
     pip install -r requirements.txt
     ```
     For macOS/Linux, you might need to use `pip3` instead of `pip`

## 💻 Using the Tool

### Interactive Mode (Recommended for All Users)

Interactive mode guides you through the entire process with simple prompts and explanations:

1. **Start the tool**:
   - Open Terminal (macOS/Linux) or Command Prompt (Windows)
   - Navigate to the tool directory (if you're not already there)
   - Run:
     ```
     python cosmos.py --interactive
     ```
     For macOS/Linux, you might need to use `python3` instead of `python`

2. **Follow the interactive prompts**:
   - **Input directory**: Select the folder containing your COSM camera footage
   - **Output directory**: Choose where you want the processed MP4 files to be saved
   - **Job name**: Give your processing job a name (or use the default)
   - **Output resolution**: Choose from preset options (4K, 1080p, etc.) or specify custom dimensions
   - **Quality mode**: Select the processing quality/speed balance that fits your needs
   - **Low memory mode**: Enable if you have limited RAM (recommended for 16GB or less)

3. **Review your selections** and confirm to begin processing

4. **Wait for processing to complete**:
   - The tool will display progress updates as it works
   - Processing time depends on your computer's performance and the footage size
   - When complete, your converted MP4 files will be available in the output directory

### Command Line Mode (For Advanced Users)

If you prefer using command line arguments instead of interactive prompts:

```
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --job-name MyJob
```

#### Windows Path Format Example:
```
python cosmos.py --input-dir C:\Users\YourName\Videos\COSM_Input --output-dir C:\Users\YourName\Videos\COSM_Output
```

## ⚙️ Configuration Options

### Output Resolution

Choose the size of your output video:

| Resolution | Dimensions | Description |
|------------|------------|-------------|
| original | 9280×6300 | Full source resolution (very large files) |
| 8K | 7680×4320 | Ultra high definition (large files) |
| 4K | 3840×2160 | Default, good balance of quality and size |
| 1080p | 1920×1080 | Standard HD, smaller files |
| 720p | 1280×720 | Smallest file size, good for sharing |

Custom resolutions can be specified using the format `WIDTHxHEIGHT`

### Processing Quality Modes

| Mode | Quality | Speed | Memory Usage | Recommended For |
|------|---------|-------|--------------|----------------|
| quality | Highest | Slowest | High | Final outputs on powerful computers |
| balanced | Good | Medium | Medium | Most users (default) |
| performance | Lower | Fast | Medium | Quick previews |
| low_memory | Good | Slow | Low | Systems with 8-16GB RAM |
| minimal | Lower | Slowest | Lowest | Systems with <8GB RAM |

### For Resource-Constrained Systems (16GB RAM or less)

If you're processing high-resolution footage on a computer with limited resources:

1. Use **low_memory** or **minimal** quality mode
2. Enable the **Low memory mode** option when prompted
3. Consider processing to a lower resolution first (like 1080p)
4. Make sure no other memory-intensive applications are running
5. When using command line mode, add these flags:
   ```
   --quality-mode minimal --low-memory
   ```

## 🔍 Troubleshooting Common Issues

### Python or Command Not Found

**Problem**: When you run a command, you get "python not found" or "command not found" error

**Solutions**:
- Make sure you're in the correct directory where the tool is located
- Try using `python3` instead of `python` (especially on macOS/Linux)
- Verify Python is installed correctly: Run `python --version` or `python3 --version`
- Restart your Command Prompt or Terminal after installing Python

### FFmpeg Not Found

**Problem**: The tool reports that FFmpeg is not found or not installed

**Solutions**:
- Verify FFmpeg is installed: Run `ffmpeg -version`
- If installed but not found:
  - On Windows: Make sure you added FFmpeg to your PATH and restarted the Command Prompt
  - On macOS/Linux: Try installing again with `brew install ffmpeg` or `sudo apt install ffmpeg`

### Out of Memory Errors

**Problem**: The tool crashes or your computer becomes unresponsive during processing

**Solutions**:
- Enable Low Memory Mode: Run with `--low-memory` flag or select this option in interactive mode
- Use the "minimal" quality mode: Add `--quality-mode minimal` or select in interactive mode
- Process a lower resolution output first
- Close other applications while processing
- Temporarily increase your system's virtual memory/swap file

### Input Directory Problems

**Problem**: The tool can't find your camera footage or reports missing files

**Solutions**:
- Make sure the input directory has the correct structure (see [Input Structure](INPUT_STRUCTURE.md))
- Verify that the manifest file is in the top-level directory
- Check if you have read permissions for all the files

### Output Directory Problems

**Problem**: The tool can't write output files or reports permission errors

**Solutions**:
- Make sure you have write permissions for the output directory
- Check available disk space (10GB+ recommended)
- Use a shorter, simpler path for your output directory

## 📱 Advanced Features

### Saving and Loading Configurations

When you find settings that work well, you can save them for future use:

1. In interactive mode, when prompted, choose to save your configuration
2. Give your configuration a name (e.g., "MySettings")
3. To use these settings later, select "Load existing configuration" at the start of interactive mode

### Using Custom CRF Values

The Constant Rate Factor (CRF) controls the quality and file size balance of the video encoding:

- Lower values (18-23) produce higher quality but larger files
- Higher values (24-28) produce smaller files with lower quality
- The default is to use an appropriate value based on your quality mode
- Advanced users can specify a custom value with the `--crf` option

### Processing Specific Manifest Files

If your input directory contains multiple manifest files, you can specify which one to use:

```
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --manifest /path/to/specific_manifest.xml
```

## 🆘 Getting Help

If you encounter any issues not covered in this guide:

1. Run the self-test to check for common problems:
   ```
   python cosmos.py --self-test
   ```

2. Enable detailed logging to get more information:
   ```
   python cosmos.py --log-level DEBUG --log-file debug.log
   ```

3. Contact support:
   - Email [caleb@polli.ai](mailto:caleb@polli.ai) with:
     - A description of the problem
     - The exact command you ran
     - Any error messages (attach the debug.log file if available)
   - Or create an issue on the GitHub repository