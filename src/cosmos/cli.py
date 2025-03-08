# File: src/cosmos/cli.py

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .utils import (
    init_logging,
    load_config,
    save_config,
    list_configs,
    get_configs_dir,
    create_configs_dir,
    check_updates,
    check_ffmpeg,
    print_info,
    print_warning,
    print_error
)
from .processor import ProcessingMode

try:
    import questionary
except ImportError:
    questionary = None

def parse_resolution(resolution_str: str) -> Dict[str, int]:
    """Parse resolution string into width and height dict."""
    resolution_presets = {
        "720p": {"width": 1280, "height": 720},
        "1080p": {"width": 1920, "height": 1080},
        "4k": {"width": 3840, "height": 2160},
        "8k": {"width": 7680, "height": 4320},
        "original": {"width": 9280, "height": 6300}
    }
    
    # Check if it's a preset
    if resolution_str in resolution_presets:
        return resolution_presets[resolution_str]
    
    # Check if it's a custom resolution (WIDTHxHEIGHT format)
    if "x" in resolution_str:
        try:
            width, height = resolution_str.split("x")
            return {"width": int(width), "height": int(height)}
        except (ValueError, IndexError):
            raise ValueError(f"Invalid resolution format: {resolution_str}. Use WIDTHxHEIGHT format or a preset.")
    
    raise ValueError(f"Invalid resolution: {resolution_str}. Use a preset or WIDTHxHEIGHT format.")

def parse_args():
    parser = argparse.ArgumentParser(description="COSM C360 Tools CLI")
    
    # Core options
    parser.add_argument("--input-dir", type=str, help="Path to input directory containing raw segments")
    parser.add_argument("--output-dir", type=str, help="Path to output directory where processed files will be saved")
    parser.add_argument("--manifest", type=str, help="Path to manifest file if not discoverable automatically")
    parser.add_argument("--job-name", type=str, help="A name for this job, used for logs and output notes")
    
    # Log options
    parser.add_argument("--log-file", type=str, help="Path to a logfile")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    
    # Processing options
    parser.add_argument("--output-resolution", type=str, 
                      help="Output resolution: '720p', '1080p', '4k', '8k', 'original', or custom 'WIDTHxHEIGHT'")
    parser.add_argument("--quality-mode", type=str, choices=["quality", "balanced", "performance", "low_memory", "minimal"],
                      help="Processing quality mode")
    parser.add_argument("--low-memory", action="store_true", help="Enable low memory mode")
    parser.add_argument("--crf", type=int, help="Custom CRF value for encoding")
    
    # Config management
    parser.add_argument("--config", type=str, help="Path to a configuration file to load")
    parser.add_argument("--save-config", type=str, help="Save the resulting configuration to a new file with this name")
    
    # Special modes
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--self-test", action="store_true", help="Run a self-test and exit")
    parser.add_argument("--check-updates", action="store_true", help="Check for updates and exit")

    args = parser.parse_args()
    
    # Convert resolution to dict if provided
    if args.output_resolution:
        try:
            args.output_resolution = parse_resolution(args.output_resolution)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)
            
    return args

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

    # 1. Config Selection
    load_existing = questionary.confirm(
        "Load existing configuration?", 
        default=False
    ).ask()

    if load_existing:
        configs = list_configs()
        if not configs:
            print_info("No saved configurations found.")
        else:
            config_choices = list(configs.keys())
            selected_config = questionary.select(
                "Select a configuration:",
                choices=config_choices
            ).ask()
            
            if selected_config:
                config_path = configs[selected_config]
                config = load_config(config_path)
                print_info(f"Loaded configuration: {selected_config}")

    # 2. Job and Output Configuration
    
    # Prompt for job name first (affects output directory structure)
    job_name = questionary.text(
        "Job name:",
        default=str(config.get("job_name", "default_job"))
    ).ask()
    
    if job_name:
        config["job_name"] = job_name

    # Prompt for input directory
    input_dir = questionary.path(
        "Input directory containing raw segments:",
        default=str(config.get("input_dir", ""))
    ).ask()

    if not input_dir:
        print_error("No input directory specified.")
        sys.exit(1)
    
    config["input_dir"] = input_dir

    # Prompt for output base directory
    output_dir = questionary.path(
        "Output base directory (outputs will go to <output_dir>/<job_name>/):",
        default=str(config.get("output_dir", ""))
    ).ask()

    if not output_dir:
        print_error("No output directory specified.")
        sys.exit(1)
        
    config["output_dir"] = output_dir

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
    
    config["log_level"] = log_level

    # 3. Processing Options
    
    # Prompt for output resolution
    resolution_presets = [
        "720p (1280x720)",
        "1080p (1920x1080)",
        "4k (3840x2160)",
        "8k (7680x4320)",
        "original (9280x6300)",
        "custom"
    ]
    
    # Determine default resolution selection
    default_res = None
    if "output_resolution" in config:
        width = config["output_resolution"]["width"]
        height = config["output_resolution"]["height"]
        
        for i, preset in enumerate(resolution_presets):
            if f"{width}x{height}" in preset:
                default_res = i
                break
        
        if default_res is None:
            default_res = 5  # Custom
    else:
        default_res = 2  # Default to 4k
    
    resolution_choice = questionary.select(
        "Select output resolution:",
        choices=resolution_presets,
        default=resolution_presets[default_res]
    ).ask()
    
    if resolution_choice.startswith("custom"):
        custom_res = questionary.text(
            "Enter custom resolution (WIDTHxHEIGHT):",
            default="1920x1080"
        ).ask()
        
        try:
            width, height = custom_res.split("x")
            config["output_resolution"] = {
                "width": int(width),
                "height": int(height)
            }
        except (ValueError, IndexError):
            print_error(f"Invalid resolution format: {custom_res}. Using 1080p.")
            config["output_resolution"] = {"width": 1920, "height": 1080}
    else:
        # Extract resolution from the selection
        if "720p" in resolution_choice:
            config["output_resolution"] = {"width": 1280, "height": 720}
        elif "1080p" in resolution_choice:
            config["output_resolution"] = {"width": 1920, "height": 1080}
        elif "4k" in resolution_choice:
            config["output_resolution"] = {"width": 3840, "height": 2160}
        elif "8k" in resolution_choice:
            config["output_resolution"] = {"width": 7680, "height": 4320}
        elif "original" in resolution_choice:
            config["output_resolution"] = {"width": 9280, "height": 6300}
    
    # Prompt for quality mode
    quality_descriptions = {
        "quality": "Highest quality, slower processing",
        "balanced": "Good balance of quality and speed",
        "performance": "Faster processing, lower quality",
        "low_memory": "Reduced memory usage, slower",
        "minimal": "Minimal resource usage, slowest"
    }
    
    quality_choices = [f"{mode} - {desc}" for mode, desc in quality_descriptions.items()]
    
    # Set default quality mode
    default_quality = "balanced"
    if "quality_mode" in config:
        default_quality = config["quality_mode"]
    
    # Find the index of the default quality in the choices
    default_index = 0
    for i, choice in enumerate(quality_choices):
        if choice.startswith(default_quality):
            default_index = i
            break
    
    quality_choice = questionary.select(
        "Select quality mode:",
        choices=quality_choices,
        default=quality_choices[default_index]
    ).ask()
    
    # Extract the quality mode from the selection
    config["quality_mode"] = quality_choice.split(" - ")[0]
    
    # Prompt for low memory mode
    config["low_memory"] = questionary.confirm(
        "Enable low memory mode? (reduces memory usage but slows processing)",
        default=config.get("low_memory", False)
    ).ask()
    
    # Prompt for custom CRF value (advanced option)
    use_custom_crf = questionary.confirm(
        "Set custom CRF value? (advanced option)",
        default=config.get("crf", None) is not None
    ).ask()
    
    if use_custom_crf:
        default_crf = config.get("crf", 23)
        crf = questionary.text(
            "Enter CRF value (lower = higher quality, higher = smaller file, typical range 18-28):",
            default=str(default_crf)
        ).ask()
        
        try:
            config["crf"] = int(crf)
        except ValueError:
            print_warning(f"Invalid CRF value: {crf}. Using default.")
            config["crf"] = None
    else:
        config["crf"] = None

    # 4. Review and Save
    print_info("\nReview your settings:")
    print_info(f"  Job Name: {config['job_name']}")
    print_info(f"  Input Directory: {config['input_dir']}")
    print_info(f"  Output Directory: {config['output_dir']}/{config['job_name']}/")
    print_info(f"  Output Resolution: {config['output_resolution']['width']}x{config['output_resolution']['height']}")
    print_info(f"  Quality Mode: {config['quality_mode']}")
    print_info(f"  Low Memory Mode: {'Enabled' if config['low_memory'] else 'Disabled'}")
    if config.get("crf") is not None:
        print_info(f"  Custom CRF: {config['crf']}")
    print_info(f"  Log Level: {config['log_level']}")
    
    confirm = questionary.confirm("Proceed with these settings?", default=True).ask()
    if not confirm:
        print_info("Aborted by user.")
        sys.exit(0)
    
    # Ask if configuration should be saved
    save_cfg = questionary.confirm(
        "Save this configuration for future use?",
        default=False
    ).ask()
    
    if save_cfg:
        config_name = questionary.text(
            "Enter a name for this configuration:",
            default=config.get("config_name", config.get("job_name", "config"))
        ).ask()
        
        config["config_name"] = config_name
        config["config_description"] = questionary.text(
            "Enter a description (optional):",
            default=config.get("config_description", "")
        ).ask()
        
        create_configs_dir()
        config_path = get_configs_dir() / f"{config_name}.json"
        save_config(config_path, config)
        print_info(f"Configuration saved to {config_path}")

    return config

def run_cli() -> Dict[str, Any]:
    """
    Parse command-line arguments, handle interactive mode if requested,
    load configuration files if provided, and return a final config dict
    for use by cosmos.py.
    """
    args = parse_args()

    # Load config if provided
    config_path = None
    if args.config:
        if Path(args.config).is_file():
            config_path = Path(args.config)
        else:
            # Check if it's a name in the configs directory
            configs = list_configs()
            if args.config in configs:
                config_path = configs[args.config]
            else:
                print_error(f"Configuration '{args.config}' not found.")
                sys.exit(1)
    
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
    if args.output_resolution:
        config["output_resolution"] = args.output_resolution
    if args.quality_mode:
        config["quality_mode"] = args.quality_mode
    if args.crf:
        config["crf"] = args.crf
    if args.low_memory:
        config["low_memory"] = args.low_memory

    # Initialize logging early so we can log further steps
    logfile = Path(config["log_file"]) if "log_file" in config else None
    logger = init_logging(level=config.get("log_level", "INFO"), logfile=logfile)

    # Handle special commands that do not require proceeding to processing
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

    # Ensure job_name is set (required for output directory structure)
    if "job_name" not in config or not config["job_name"]:
        config["job_name"] = "default_job"
        logger.info(f"No job name specified. Using default: {config['job_name']}")

    # Set default processing options if not specified
    if "output_resolution" not in config:
        config["output_resolution"] = {"width": 3840, "height": 2160}  # Default to 4k
        logger.info(f"No output resolution specified. Using default: 4k (3840x2160)")
    
    if "quality_mode" not in config:
        config["quality_mode"] = "balanced"
        logger.info(f"No quality mode specified. Using default: balanced")
    
    if "low_memory" not in config:
        config["low_memory"] = False

    # Save config if requested
    if args.save_config:
        config["config_name"] = args.save_config
        create_configs_dir()
        save_path = get_configs_dir() / f"{args.save_config}.json"
        save_config(save_path, config)
        logger.info(f"Configuration saved to {save_path}")

    logger.info("CLI argument resolution complete. Ready to proceed with processing pipeline.")
    logger.info(f"Job Name: {config.get('job_name', 'default_job')}")
    logger.info(f"Input Directory: {config['input_dir']}")
    logger.info(f"Output Directory: {config['output_dir']}/{config.get('job_name', 'default_job')}/")
    if "manifest" in config:
        logger.info(f"Manifest: {config['manifest']}")
    logger.info(f"Output Resolution: {config['output_resolution']['width']}x{config['output_resolution']['height']}")
    logger.info(f"Quality Mode: {config['quality_mode']}")
    logger.info(f"Low Memory Mode: {'Enabled' if config.get('low_memory', False) else 'Disabled'}")
    if "crf" in config and config["crf"] is not None:
        logger.info(f"Custom CRF: {config['crf']}")

    # Add self_test key so cosmos.py can check and handle it
    config["self_test"] = args.self_test

    return config
