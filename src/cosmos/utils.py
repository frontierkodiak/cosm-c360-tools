# File: src/cosmos/utils.py

import logging
import json
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

__version__ = "0.2.1"  # Just an example version

def init_logging(level: str = "INFO", logfile: Optional[Path] = None) -> logging.Logger:
    """Initialize logging configuration for the entire application."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    
    # Add console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, level.upper(), logging.INFO))
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)
    
    # Add file handler if logfile specified
    if logfile:
        # Create parent directories for log file if they don't exist
        logfile.parent.mkdir(parents=True, exist_ok=True)
        
        fh = logging.FileHandler(logfile, encoding='utf-8')
        fh.setLevel(getattr(logging, level.upper(), logging.INFO))
        fh.setFormatter(formatter)
        root_logger.addHandler(fh)
    
    # Create and return the main application logger
    logger = logging.getLogger("cosmos")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger

def get_configs_dir() -> Path:
    """Get the path to the configs directory."""
    return Path(__file__).parent.parent.parent / "configs"

def create_configs_dir() -> None:
    """Create the configs directory if it doesn't exist."""
    configs_dir = get_configs_dir()
    configs_dir.mkdir(exist_ok=True)

def list_configs() -> Dict[str, Path]:
    """List available configurations in the configs directory."""
    configs_dir = get_configs_dir()
    create_configs_dir()
    
    configs = {}
    for config_file in configs_dir.glob("*.json"):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                name = config_data.get("config_name", config_file.stem)
                configs[name] = config_file
        except (json.JSONDecodeError, OSError):
            # Skip invalid config files
            continue
    
    return configs

def load_config(config_path: Path) -> Dict[str, Any]:
    if config_path and config_path.is_file():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_git_available() -> bool:
    return shutil.which("git") is not None

def check_for_updates(repo_path: Path) -> bool:
    """
    Check if updates are available for a Git repository.
    Returns True if an update is available, False otherwise.
    If any error occurs, returns False.
    """
    try:
        # 'git fetch' to update remote refs
        subprocess.run(["git", "-C", str(repo_path), "fetch"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        remote_head = subprocess.check_output(["git", "-C", str(repo_path), "ls-remote", "origin", "HEAD"], text=True).split()[0]
        local_head = subprocess.check_output(["git", "-C", str(repo_path), "rev-parse", "HEAD"], text=True).strip()
        return remote_head != local_head
    except Exception as e:
        print_error(f"Error checking for updates: {e}")
        return False

def check_updates(repo_path: Path = Path(".")) -> None:
    print_info(f"Current version: {__version__}")
    if is_git_available():
        if check_for_updates(repo_path):
            print_info("An update is available! Run `git pull` to update.")
        else:
            print_info("You are up-to-date.")
    else:
        print_warning("Git is not installed or not accessible. Cannot check for updates.")
        print_info("Visit the repository and `git pull` manually to update.")

def print_info(message: str) -> None:
    print(f"[INFO] {message}")

def print_warning(message: str) -> None:
    print(f"[WARNING] {message}")

def print_error(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)

def print_success(message: str) -> None:
    print(f"[SUCCESS] {message}")
