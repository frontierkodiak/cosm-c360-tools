# File: src/cosmos/cli.py

import argparse
from pathlib import Path
import sys
import logging
from typing import Optional

from .utils import (
    init_logging,
    load_config,
    save_config,
    check_updates,
    check_ffmpeg,
    print_info,
    print_warning,
    print_error,
    print_success
)

try:
    import questionary
except ImportError:
    questionary = None

def parse_args():
    parser = argparse.ArgumentParser(description="COSM C360 Tools CLI")
    parser.add_argument("--input-dir", type=str, help="Path to input directory containing raw segments")
    parser.add_argument("--output-dir", type=str, help="Path to output directory where processed files will be saved")
    parser.add_argument("--manifest", type=str, help="Path to manifest file if not discoverable automatically")
    parser.add_argument("--config-file", type=str, help="Path to a configuration file (JSON)")
    parser.add_argument("--log-file", type=str, help="Path to a logfile")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--self-test", action="store_true", help="Run a self-test and exit")
    parser.add_argument("--check-updates", action="store_true", help="Check for updates and exit")
    parser.add_argument("--job-name", type=str, help="A name for this job, used for logs and output notes")

    return parser.parse_args()

def run_interactive_mode(config: dict) -> dict:
    if questionary is None:
        print_error("Interactive mode requested but 'questionary' is not installed.")
        sys.exit(1)

    print_info("Entering interactive mode...")

    # Prompt for input directory
    input_dir = questionary.path(
        "Please select the input directory containing raw segments:",
        default=str(config.get("input_dir", ""))
    ).ask()

    # Prompt for output directory
    output_dir = questionary.path(
        "Please select the output directory for processed files:",
        default=str(config.get("output_dir", ""))
    ).ask()

    # Confirm ffmpeg available
    if not check_ffmpeg():
        print_warning("FFmpeg not found. Please install it before proceeding.")
        cont = questionary.confirm("Do you want to continue anyway?", default=False).ask()
        if not cont:
            print_info("Aborting due to missing FFmpeg.")
            sys.exit(1)

    # Prompt for log level
    log_level = questionary.select(
        "Select log level:",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=config.get("log_level", "INFO")
    ).ask()

    # Prompt for job name
    job_name = questionary.text(
        "Job name (optional):",
        default=str(config.get("job_name", ""))
    ).ask()

    config["input_dir"] = input_dir
    config["output_dir"] = output_dir
    config["log_level"] = log_level
    if job_name:
        config["job_name"] = job_name

    print_info("Review your settings:")
    print_info(f"  Input Directory: {config['input_dir']}")
    print_info(f"  Output Directory: {config['output_dir']}")
    print_info(f"  Log Level: {config['log_level']}")
    if "job_name" in config:
        print_info(f"  Job Name: {config['job_name']}")
    confirm = questionary.confirm("Proceed with these settings?", default=True).ask()

    if not confirm:
        print_info("Aborted by user.")
        sys.exit(0)

    return config

def main():
    args = parse_args()

    # Load config if provided
    config_path = Path(args.config_file) if args.config_file else None
    config = load_config(config_path) if config_path else {}

    # Command line args override config or fill in missing fields
    if args.log_level:
        config["log_level"] = args.log_level
    if args.log_file:
        config["log_file"] = args.log_file
    if args.input_dir:
        config["input_dir"] = args.input_dir
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.manifest:
        config["manifest"] = args.manifest
    if args.job_name:
        config["job_name"] = args.job_name

    # Initialize logging
    logfile = Path(config["log_file"]) if "log_file" in config else None
    logger = init_logging(level=config.get("log_level", "INFO"), logfile=logfile)

    # Handle special commands first
    if args.check_updates:
        check_updates()
        sys.exit(0)

    # If interactive mode requested, run interactive prompts
    if args.interactive:
        config = run_interactive_mode(config)

    # Validate that we have required directories
    if "input_dir" not in config or not config["input_dir"]:
        print_error("Input directory not specified. Use --input-dir or run in interactive mode.")
        sys.exit(1)

    if "output_dir" not in config or not config["output_dir"]:
        print_error("Output directory not specified. Use --output-dir or run in interactive mode.")
        sys.exit(1)

    # Save updated config if config file provided
    if config_path:
        save_config(config_path, config)

    # Return final config to be consumed by cosmos.py
    config["self_test"] = args.self_test
    return config

if __name__ == "__main__":
    main()

    # From here we would:
    # 1. Use manifest parser to find or load manifest.
    # 2. Validate inputs using InputValidator.
    # 3. Process clips using VideoProcessor.
    #
    # For now, we'll just log that we've completed CLI argument resolution.
    # The next step would be calling into the main cosmos pipeline (e.g. from cosmos.py)
    # This might look like:
    # 
    # from .manifest import find_manifest, ManifestParser
    # from .validation import InputValidator
    # from .processor import VideoProcessor, ProcessingOptions, ProcessingMode
    #
    # # ... load manifest, validate, process, etc.