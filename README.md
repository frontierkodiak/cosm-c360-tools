# COSM C360 Tools

**COSM C360 Tools** is a user-friendly utility that converts specialized video output from COSM C360 cameras into standard MP4 files for easy viewing and analysis. No video editing experience required!

## 📋 Quick Start Guide (Windows & macOS)

Follow these steps carefully to set up and run the tool.

**Step 1: Get the Tool Code**

1.  **Install GitHub Desktop:** Download and install from [desktop.github.com](https://desktop.github.com/).
2.  **Clone the Repository:**
    *   Open GitHub Desktop.
    *   Go to `File` > `Clone Repository`.
    *   Select the `URL` tab.
    *   Enter: `https://github.com/frontierkodiak/cosm-c360-tools.git`
    *   Choose a familiar location on your computer (like `Documents` or `Desktop`) to save the tool's files. Click `Clone`.

**Step 2: Install Prerequisites**

1.  **Python:**
    *   Download from [python.org](https://www.python.org/downloads/) (get version 3.10 or newer).
    *   **Windows VERY IMPORTANT:** During installation, check the box labeled **"Add python.exe to PATH"**.
       ![Add Python to PATH checkbox](https://docs.python.org/3/_images/win_installer.png)
    *   **Verify:** Open Command Prompt (Windows: search "cmd") or Terminal (macOS: Applications > Utilities > Terminal) and type `python --version` (or `python3 --version` on some Macs) and press Enter. You should see the version number.
2.  **uv (Python Tool Manager):**
    *   **Windows (in Command Prompt):** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
    *   **macOS/Linux (in Terminal):** `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   **Verify:** Close and reopen Command Prompt/Terminal. Type `uv --version` and press Enter. You should see the version number.
3.  **FFmpeg (Video Tool):**
    *   **Windows:** Download the "ffmpeg-release-essentials.zip" from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/). Extract the ZIP file somewhere simple (like `C:\ffmpeg`). Follow [these visual steps](LINK_TO_SIMPLE_PATH_GUIDE_IF_AVAILABLE_OR_USE_USER_GUIDE_LINK) to add the `bin` subfolder (e.g., `C:\ffmpeg\bin`) inside the extracted folder to your system PATH.
    *   **macOS (in Terminal):** `brew install ffmpeg` (If you don't have Homebrew, install it from [brew.sh](https://brew.sh/)).
    *   **Verify:** Close and reopen Command Prompt/Terminal. Type `ffmpeg -version` and press Enter. You should see version information.

**Step 3: Set Up Project Environment**

1.  Open Command Prompt (Windows) or Terminal (macOS).
2.  Navigate to the tool's folder you created in Step 1:
    *   Windows Example: `cd C:\Users\YourName\Documents\GitHub\cosm-c360-tools` (Replace path as needed)
    *   macOS Example: `cd ~/Documents/GitHub/cosm-c360-tools` (Replace path as needed)
3.  Create a dedicated workspace for the tool's dependencies:
    ```bash
    uv venv .venv
    ```
    (This creates a hidden `.venv` folder inside the tool's directory).
4.  Activate the workspace:
    *   Windows (Command Prompt): `.venv\Scripts\activate`
    *   macOS/Linux (Terminal): `source .venv/bin/activate`
    *   You should see `(.venv)` appear at the start of your command prompt line.
5.  Install the tool and its required packages into the workspace:
    ```bash
    uv pip install -e .
    ```

**Step 4: Run the Tool!**

1.  Make sure your workspace is still active (you see `(.venv)` at the start of the prompt). If not, repeat Step 3.4.
2.  Run the tool in interactive mode:
    ```bash
    python cosmos.py --interactive
    ```
3.  Follow the on-screen prompts! The tool will ask you for the input folder (where your camera files are) and the output folder (where the MP4 videos will be saved).

**(Optional) Updating the Tool:**
1. Open GitHub Desktop.
2. Make sure `cosm-c360-tools` is the current repository.
3. Click `Fetch origin`. If updates are available, a `Pull origin` button will appear. Click it.

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
