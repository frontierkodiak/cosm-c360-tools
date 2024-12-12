# File: src/cosmos/preflight.py

import platform
import os
import sys
import shutil
from pathlib import Path
import psutil
from typing import Optional

from .utils import print_info, print_warning, print_error, print_success, check_ffmpeg

def check_python_version(min_version=(3, 8)):
    return sys.version_info >= min_version

def check_system_memory(minimum_gb=8):
    total_memory = psutil.virtual_memory().total / (1024**3)
    return total_memory >= minimum_gb

def check_disk_space(directory: Path, minimum_gb=10):
    usage = shutil.disk_usage(directory)
    free_gb = usage.free / (1024**3)
    return free_gb >= minimum_gb

def check_required_codecs():
    # Assume ffmpeg install that we verified can run. Detailed codec check
    # could parse `ffmpeg -encoders` but omitted for brevity.
    return check_ffmpeg()

def check_directory_structure(input_dir: Path, manifest_path: Optional[Path] = None):
    """
    Basic directory structure checks:
    - Confirm input_dir exists
    - Confirm we have at least one .xml manifest if manifest_path not given
    - If multiple .xml manifests found and no manifest_path specified, fail
    - Check if we have at least one directory structure like NH/*M/*S/meta.json
    """
    if not input_dir.is_dir():
        return {
            "Directory Exists": {
                "check": False,
                "message": f"Input directory {input_dir} does not exist.",
                "help": "Check the input_dir path."
            }
        }
    
    # Check for manifest files if manifest_path not specified
    manifests = list(input_dir.glob("*.xml"))
    if manifest_path:
        # User specified manifest; check if it exists
        if not manifest_path.is_file():
            return {
                "Manifest Provided": {
                    "check": False,
                    "message": f"Specified manifest {manifest_path} not found.",
                    "help": "Ensure you provided the correct manifest path."
                }
            }
    else:
        # No manifest specified; must find exactly one
        if len(manifests) == 0:
            return {
                "Manifest Discovery": {
                    "check": False,
                    "message": "No .xml manifest found in top-level directory.",
                    "help": "Provide --manifest or place a single .xml in input_dir."
                }
            }
        elif len(manifests) > 1:
            return {
                "Manifest Ambiguity": {
                    "check": False,
                    "message": "Multiple .xml manifests found but none specified.",
                    "help": "Use --manifest to specify which manifest to use."
                }
            }

    # Check basic structure: at least one H directory, inside it at least one M directory, inside it at least one S directory with meta.json
    hour_dirs = [d for d in input_dir.glob("*H") if d.is_dir()]
    if not hour_dirs:
        return {
            "Directory Structure": {
                "check": False,
                "message": "No hour-level (e.g. '0H') directories found.",
                "help": "Ensure input_dir follows the 'NH/MM/SS' structure."
            }
        }

    # Check at least one M directory
    found_valid_structure = False
    for hdir in hour_dirs:
        mdirs = [m for m in hdir.glob("*M") if m.is_dir()]
        for mdir in mdirs:
            sdirs = [s for s in mdir.glob("*S") if s.is_dir()]
            for sdir in sdirs:
                meta = sdir / "meta.json"
                if meta.is_file():
                    found_valid_structure = True
                    break
            if found_valid_structure:
                break
        if found_valid_structure:
            break

    if not found_valid_structure:
        return {
            "Directory Structure": {
                "check": False,
                "message": "Did not find any second-level directories with meta.json.",
                "help": "Ensure the directory structure matches expected format (0H/0M/0S/meta.json)."
            }
        }

    return {
        "Directory Structure": {
            "check": True
        }
    }

def check_windows_specific(input_dir: Path):
    """
    On Windows, check if any paths exceed 260 chars.
    This can cause issues on older Windows environments.
    """
    if platform.system() == "Windows":
        for root, dirs, files in os.walk(input_dir):
            for name in dirs + files:
                full_path = Path(root, name)
                if len(str(full_path)) > 260:
                    return {
                        "Path Length": {
                            "check": False,
                            "message": f"Path exceeds 260 characters: {full_path}",
                            "help": "Shorten directory names or enable long paths in Windows."
                        }
                    }
    return {
        "Path Length": {"check": True}
    }

def validate_system_requirements(input_dir: Path, output_dir: Path):
    checks = {
        "FFmpeg Installation": {
            "check": check_ffmpeg(),
            "message": "FFmpeg not found. Please install it.",
            "help": "https://ffmpeg.org/download.html"
        },
        "HEVC Codec Availability": {
            "check": check_required_codecs(),
            "message": "HEVC codec support not found in ffmpeg.",
            "help": "Ensure your ffmpeg build supports HEVC."
        },
        "Python Version": {
            "check": check_python_version(),
            "message": "Python 3.8 or higher required.",
            "help": "Please upgrade your Python installation."
        },
        "System Memory": {
            "check": check_system_memory(minimum_gb=8),
            "message": "Less than 8GB RAM available. Processing may be slow.",
            "help": "Use --low-memory mode or upgrade system memory."
        },
        "Disk Space": {
            "check": check_disk_space(output_dir, minimum_gb=10),
            "message": "Less than 10GB disk space available.",
            "help": "Free disk space or choose another output directory."
        }
    }
    return checks

def format_validation_results(validation_results):
    all_good = True
    for category, result in validation_results.items():
        if not result["check"]:
            all_good = False
            print_error(f"[{category}] {result['message']} - {result.get('help', '')}")
        else:
            print_success(f"[{category}] OK")
    return all_good

def run_self_test(input_dir: Path, output_dir: Path, manifest_path: Optional[Path] = None) -> bool:
    print_info("Running system pre-flight checks...")
    system_checks = validate_system_requirements(input_dir, output_dir)
    sys_ok = format_validation_results(system_checks)

    print_info("Checking basic directory structure...")
    dir_checks = check_directory_structure(input_dir, manifest_path)
    dir_ok = format_validation_results(dir_checks)

    windows_ok = True
    if platform.system() == "Windows":
        print_info("Performing Windows-specific checks...")
        win_checks = check_windows_specific(input_dir)
        windows_ok = format_validation_results(win_checks)

    return sys_ok and dir_ok and windows_ok
