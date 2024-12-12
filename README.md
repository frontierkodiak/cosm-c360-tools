# COSM C360 Tools

**COSM C360 Tools** (referred to as `cosmos`) is a command-line utility for converting specialized video output from COSM C360 cameras into standard MP4 video files suitable for review and downstream analysis. It handles the complex tiled HEVC output and merges multiple streams into a standard video format.

## Key Features

- **Manifest Parsing & Validation**: Automatically finds and parses the camera's XML manifest file, identifying clips and verifying temporal continuity.
- **Segment Analysis**: Gathers `.ts` segments and their corresponding `meta.json` files, ensuring integrity and completeness.
- **Video Assembly**: Extracts and aligns four HEVC tile streams, handles overlapping regions, and assembles frames into a full-resolution video.
- **Multi-Resolution Output**: Outputs a full-resolution master file and can generate downscaled variants (e.g., 4K, 1080p).
- **Cross-Platform & Hardware Acceleration**: Works on Linux, macOS, and Windows. Automatically attempts hardware-accelerated encoding (NVENC, AMF, QSV) and falls back to software (x264).
- **Pre-Flight Checks**: Built-in `--self-test` mode checks system requirements (FFmpeg, disk space, memory) and input directory structure before processing.
- **Interactive & Non-Interactive Modes**: Fully scriptable via CLI flags, or run interactively with guided prompts for non-technical users.
- **Update Checking**: Checks for updates if `git` is available.

## System Requirements

- **Operating System**: Linux, macOS, or Windows.
- **Python**: 3.10 or higher recommended.
- **FFmpeg**: Must be installed and accessible in `PATH`.
- **Memory**: At least 8GB RAM recommended (less may cause slowdowns, consider `--low-memory` mode).
- **Disk Space**: At least 10GB free disk space recommended.
- **Git (Optional)**: To automatically check for updates when running `--check-updates`.

## Input Directory Structure

The input directory should follow a hierarchical structure reflecting the camera output:

```
input_dir/
 ├── 0H/
 │   ├── 0M/
 │   │   ├── 0S/
 │   │   │   ├── meta.json
 │   │   │   ├── <segment .ts files>
 │   │   ├── 1S/
 │   │   │   ├── meta.json
 │   │   │   ├── <segment .ts files>
 │   │   └── ...
 │   └── 1M/
 │       ├── 0S/
 │       │   ├── meta.json
 │       │   ├── <segment .ts files>
 │       └── ...
 ├── MyManifest.xml
 └── AnotherManifest.xml (if multiple manifests exist)
```

- Each second-level directory (`XH/XM/XS`) must contain a `meta.json` file and `.ts` files.
- The top-level directory should contain a single `.xml` manifest file. If multiple `.xml` files are present, you must specify which one to use via `--manifest`.

## Installation

We recommend using [UV](https://github.com/astral-sh/uv?tab=readme-ov-file) for environment management.

### Using UV (Recommended)

**macOS / Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv new cosmos-env
uv activate cosmos-env
pip install -r requirements.txt
```

**Windows (PowerShell)**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv new cosmos-env
uv activate cosmos-env
pip install -r requirements.txt
```

If not using UV, you can still use Python's built-in `venv`:
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Confirm `ffmpeg` is installed and in your PATH:
```bash
ffmpeg -version
```

If `ffmpeg` is not found, please install it according to your platform's instructions.

## Usage

### Non-Interactive Mode

Run `cosmos.py` directly or via `python`:

```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output
```

If multiple `.xml` manifests exist, specify which one:
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --manifest /path/to/manifest.xml
```

Run a system self-test before processing:
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --self-test
```

Check for updates:
```bash
python cosmos.py --check-updates
```

Specify a job name (useful for logs and output notes):
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --job-name MyJobName
```

Adjust logging:
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --log-level DEBUG --log-file mylog.log
```

### Interactive Mode

If you're unsure about the input directory or other parameters, run:
```bash
python cosmos.py --interactive
```

The tool will guide you through selecting the input directory, output directory, and other settings interactively. After confirming, it will proceed with processing.

### Example Commands (All Platforms)

**Windows (PowerShell)**:
```powershell
python .\cosmos.py --input-dir C:\data\cosm_input --output-dir C:\data\cosm_output --self-test
```

**macOS / Linux (Bash)**:
```bash
python cosmos.py --input-dir ~/cosm_input --output-dir ~/cosm_output --interactive
```

## Running Tests

Tests are included to ensure code quality and correctness:

```bash
pytest tests
```

Ensure `pytest` is installed:
```bash
pip install pytest
```

This runs the test suite (unit tests for validation, processing, manifest parsing, and integration tests). Use `TESTING.md` for more detailed testing instructions.

## Additional Notes

- Output files, including `job_info.txt`, are placed in the specified `output` directory.
- If system resources are limited, consider `--low-memory` mode (to be added) or reducing resolution.
- If you wish to contribute or request features, please open an issue or a pull request.