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