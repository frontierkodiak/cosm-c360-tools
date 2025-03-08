# COSM C360 Tools Guidelines

## Commands
- Run all tests: `pytest tests`
- Run a single test: `pytest tests/test_file.py::test_function_name -v`
- Interactive mode: `python cosmos.py --interactive`
- Non-interactive: `python cosmos.py --input-dir /path/to/input --output-dir /path/to/output`
- Debug mode: `python cosmos.py --log-level DEBUG`

## Environment
- Python 3.10+ required
- Dependencies: `uv new cosmos-env && uv activate cosmos-env && pip install -r requirements.txt`
- External: FFmpeg must be installed and accessible in PATH

## Code Style
- Type hints required (from typing import Optional, Dict, List, Any)
- Classes: PascalCase (ManifestParser, InputValidator)
- Functions/methods: snake_case (parse_args, find_manifest)
- Imports: standard library first, then third-party, then local
- Error handling: raise specific exceptions with descriptive messages
- Prioritize user-friendly error messages for non-technical users
- Document public functions with docstrings