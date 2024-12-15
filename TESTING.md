# Testing the COSM C360 Tools

This document outlines how to run tests on macOS, Linux, and Windows.

## Requirements

- Python 3.10 or higher
- `pytest` installed in your environment
- `ffmpeg` installed and accessible in `PATH`
- The input directory specified for integration tests (`/datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy`) must be accessible on your machine.
- The output directory (`/datasets/dataZoo/clients/ladybird_data/LADYBIRD/cosmos_out`) must exist and be writable.

## Installing Test Dependencies

If you used `uv` (recommended):

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
uv new cosmos-env
uv activate cosmos-env
pip install -r requirements.txt

# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv new cosmos-env
uv activate cosmos-env
pip install -r requirements.txt
```

If not using `uv`, you can use `python -m venv` and `pip` as documented in the README.

## Running Tests

To run all tests:
```bash
pytest tests
```

This will run:
- Unit tests for manifest, validation, processing.
- The integration test (`test_integration.py`).

If the integration test fails, ensure that:
- The specified input and output directories are accessible.
- FFmpeg is installed and in `PATH`.
- You have sufficient system resources (disk space, etc.).

## Platform Notes

- **macOS & Linux**: Should work out of the box with `pytest`.
- **Windows**: Ensure Python and ffmpeg are installed, and that `ffmpeg` is in `PATH`. Running `pytest` in `powershell` or `cmd` is supported.

## Additional Tips

- Use `-v` for verbose output:
  ```bash
  pytest -v tests
  ```
- Use `-k` to run a specific test:
  ```bash
  pytest -k test_self_test_integration
  ```

## Inspecting Output Files

To inspect the processed MP4 files and verify their contents, you can use FFmpeg's ffprobe tool:

```bash
# Get detailed information about the video file
ffprobe -v error -show_format -show_streams output.mp4

# Get just the duration and basic format info
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=noprint_wrappers=1 output.mp4

# Show frame information (useful for debugging black frames)
ffprobe -v error -show_frames -of compact output.mp4

# Quick visual check of frames (requires display)
ffplay output.mp4
```

Common issues to check for:
- Duration matches expected clip length
- Video codec is h264
- Frame rate is correct (typically 59.94/60fps for COSM footage)
- Resolution matches expected output (e.g., 3840x2160)
  - COSM output is 9280x6300 (total of the four streams is 9344x6364, but we crop 32px from interior of each stream)
- Presence of video stream (missing video stream but present audio can indicate encoding issues)

Example of checking a specific file:
```bash
# Check if file contains valid video stream
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 output.mp4
```

# DEV
Copy test results from blade to local machine:
```bash
rsync -avz caleb@blade:/datasets/dataZoo/clients/ladybird_data/LADYBIRD/cosmos_out/ ~/cosmos_tests/test0/
```
