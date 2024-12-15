# File: src/cosmos/cli.py

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .utils import (
    init_logging,
    load_config,
    save_config,
    check_updates,
    check_ffmpeg,
    print_info,
    print_warning,
    print_error
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

def run_interactive_mode(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run an interactive session to gather input_dir, output_dir, and other settings.
    Uses questionary for cross-platform interactive prompts.
    If questionary is not installed, print an error and exit.
    """
    if questionary is None:
        print_error("Interactive mode requested but 'questionary' is not installed.")
        sys.exit(1)

    print_info("Entering interactive mode...")

    # Prompt for input directory
    input_dir = questionary.path(
        "Please select the input directory containing raw segments:",
        default=str(config.get("input_dir", ""))
    ).ask()

    if not input_dir:
        print_error("No input directory specified.")
        sys.exit(1)

    # Prompt for output directory
    output_dir = questionary.path(
        "Please select the output directory for processed files:",
        default=str(config.get("output_dir", ""))
    ).ask()

    if not output_dir:
        print_error("No output directory specified.")
        sys.exit(1)

    # Confirm ffmpeg available
    if not check_ffmpeg():
        print_warning("FFmpeg not found. Please install it before proceeding.")
        cont = questionary.confirm("Do you want to continue anyway?", default=False).ask()
        if not cont:
            print_info("Aborted due to missing FFmpeg.")
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

def run_cli() -> Dict[str, Any]:
    """
    Parse command-line arguments, handle interactive mode if requested,
    load configuration files if provided, and return a final config dict
    for use by cosmos.py.
    """
    args = parse_args()

    # Load config if provided
    config_path = Path(args.config_file) if args.config_file else None
    config = load_config(config_path) if config_path else {}

    # CLI args override config values
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

    # Initialize logging early so we can log further steps
    logfile = Path(config["log_file"]) if "log_file" in config else None
    logger = init_logging(level=config.get("log_level", "INFO"), logfile=logfile)

    # Handle special commands that do not require proceeding to processing
    # (NOTE: Self-test is now handled in cosmos.py, not here)
    if args.check_updates:
        check_updates()
        sys.exit(0)

    # If interactive mode requested, run interactive prompts
    if args.interactive:
        config = run_interactive_mode(config)

    # Validate directories are set
    if "input_dir" not in config or not config["input_dir"]:
        print_error("Input directory not specified. Use --input-dir or run in interactive mode.")
        sys.exit(1)

    if "output_dir" not in config or not config["output_dir"]:
        print_error("Output directory not specified. Use --output-dir or run in interactive mode.")
        sys.exit(1)

    # Save updated config if config file provided
    if config_path:
        save_config(config_path, config)

    logger.info("CLI argument resolution complete. Ready to proceed with processing pipeline.")
    logger.info(f"Input Directory: {config['input_dir']}")
    logger.info(f"Output Directory: {config['output_dir']}")
    if "manifest" in config:
        logger.info(f"Manifest: {config['manifest']}")

    # Add self_test key so cosmos.py can check and handle it
    config["self_test"] = args.self_test

    return config
