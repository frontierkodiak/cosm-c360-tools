# File: src/cosmos/utils.py

import logging
import json
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

def init_logging(level: str = "INFO", logfile: Optional[Path] = None) -> logging.Logger:
    """
    Initialize and configure global logger.
    
    Args:
        level: Log level name (e.g. "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        logfile: Optional path to a file where logs should be written.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger("cosmos")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional file handler
    if logfile:
        fh = logging.FileHandler(logfile, encoding='utf-8')
        fh.setLevel(getattr(logging, level.upper(), logging.INFO))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load a JSON configuration from the given path.
    If file does not exist, return empty dict.
    """
    if config_path.is_file():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """
    Save configuration dictionary to a JSON file.
    Overwrite existing file. 
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def check_ffmpeg() -> bool:
    """
    Check if ffmpeg is available.
    Returns:
        True if ffmpeg is found and runs, False otherwise.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def self_test(input_dir: Optional[Path] = None, output_dir: Optional[Path] = None) -> bool:
    """
    Run a basic self-test:
    - Check ffmpeg availability
    - Check output directory write permission
    - Possibly run a very basic encode test (skipped here for brevity)
    
    Args:
        input_dir: Optional directory to test reading from
        output_dir: Optional directory to test writing to

    Returns:
        True if test passes, False otherwise.
    """
    # Check ffmpeg
    if not check_ffmpeg():
        print_error("FFmpeg not found. Self-test failed.")
        return False
    
    # Check output directory write permissions
    if output_dir:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            test_file = output_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            print_error(f"Cannot write to output directory: {e}")
            return False

    print_success("Self-test passed.")
    return True

def check_updates() -> None:
    """
    Check for updates. 
    Placeholder: In real scenario, might query a remote source (GitHub releases or a custom server).
    For now, just print a message.
    """
    # Stub: For demonstration only
    print_info("No update mechanism implemented. You are on the latest known version.")

# Simple helper print functions (no dependencies on color libraries)
def print_info(message: str) -> None:
    print(f"[INFO] {message}")

def print_warning(message: str) -> None:
    print(f"[WARNING] {message}")

def print_error(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)

def print_success(message: str) -> None:
    print(f"[SUCCESS] {message}")
