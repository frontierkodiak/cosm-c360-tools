# COSM C360 Tools - User Guide

This guide provides step-by-step instructions for using the COSM C360 Tools to convert COSM camera footage into standard MP4 video files. It's designed for users with varying levels of technical experience.

## Quick Start (TL;DR)

1. Install Python 3.10 or higher and FFmpeg
2. Download the tool
3. Open Terminal/Command Prompt
4. Run in interactive mode: `python cosmos.py --interactive`
5. Follow the prompts to select input/output folders and settings

## Installation Guide

### Step 1: Install Python

#### Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

#### macOS:
1. Install Homebrew (if not already installed):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```
   brew install python
   ```

#### Linux (Ubuntu/Debian):
```
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Install FFmpeg

#### Windows:
1. Download the FFmpeg build from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the ZIP file to a location like `C:\ffmpeg`
3. Add to PATH:
   - Search for "Environment Variables" in the Start menu
   - Click "Edit the system environment variables"
   - Click "Environment Variables..."
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add the path to the ffmpeg `bin` folder (e.g., `C:\ffmpeg\bin`)
   - Click "OK" on all dialogs

#### macOS:
```
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```
sudo apt update
sudo apt install ffmpeg
```

### Step 3: Download and Set Up the Tool

1. Download the COSM C360 Tools package and extract it to a folder
2. Open Terminal (macOS/Linux) or Command Prompt (Windows)
3. Navigate to the folder containing the tool:
   ```
   cd path/to/cosm-c360-tools
   ```
4. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Using the Tool

### Interactive Mode (Recommended for New Users)

1. Open Terminal (macOS/Linux) or Command Prompt (Windows)
2. Navigate to the tool's directory:
   ```
   cd path/to/cosm-c360-tools
   ```
3. Run in interactive mode:
   ```
   python cosmos.py --interactive
   ```
4. Follow the prompts to:
   - Select your input directory (where the camera footage is stored)
   - Select your output directory (where you want the MP4 files)
   - Set a job name (optional)
   - Confirm your settings

The tool will process the video files and save them to your chosen output directory.

### Command Line Mode (For Advanced Users)

If you prefer using command line arguments:

```
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --job-name MyJob
```

Replace `/path/to/input` and `/path/to/output` with your actual paths.

#### Windows Path Format Example:
```
python cosmos.py --input-dir C:\Users\YourName\Videos\COSM_Input --output-dir C:\Users\YourName\Videos\COSM_Output
```

## Common Commands

### Convert COSM Footage to 4K MP4

```
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output
```

### Run a System Check Before Processing

```
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --self-test
```

### Check for Updates

```
python cosmos.py --check-updates
```

## Troubleshooting

### "Command not found" Error

- Make sure you're in the correct directory where the tool is located
- Verify that Python is installed correctly with `python --version`

### FFmpeg Not Found

- Verify FFmpeg is installed with `ffmpeg -version`
- If installed but not found, check your PATH environment variable

### Processing Errors

- Ensure your input directory has the expected structure with the manifest file
- Check if you have write permissions for the output directory
- Make sure you have enough disk space

## Input Directory Structure

The tool expects a specific directory structure:

```
input_dir/
 ├── 0H/
 │   ├── 0M/
 │   │   ├── 0S/
 │   │   │   ├── meta.json
 │   │   │   ├── segment files...
 │   │   ├── 1S/
 │   │   │   └── ...
 │   │   └── ...
 │   └── 1M/
 │       └── ...
 └── ManifestFile.xml
```

## Need Help?

If you encounter any issues not covered here, please email [caleb@polli.ai] with:
- A description of the problem
- The exact command you ran
- Any error messages you received
Alternatively, feel free to raise an issue on this repo.