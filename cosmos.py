# File: cosmos.py

import sys
import os
import platform
import subprocess
from pathlib import Path
from datetime import datetime

from src.cosmos.cli import run_cli
from src.cosmos.preflight import run_self_test
from src.cosmos.utils import print_info, print_error, print_success, print_warning
from src.cosmos.manifest import find_manifest, ManifestParser
from src.cosmos.validation import InputValidator
from src.cosmos.processor import VideoProcessor, ProcessingOptions, ProcessingMode, EncoderType

def get_system_info():
    """Gather system information for job_info.txt"""
    info = {
        "python_version": platform.python_version(),
        "os_platform": f"{platform.system()} {platform.release()}",
    }
    
    # Get FFmpeg version
    try:
        ffmpeg_version = subprocess.check_output(["ffmpeg", "-version"], text=True).split('\n')[0]
        info["ffmpeg_version"] = ffmpeg_version
    except (subprocess.SubprocessError, FileNotFoundError):
        info["ffmpeg_version"] = "Unknown"
    
    return info

def main():
    config = run_cli()

    # Use the input_dir directly since it's already properly handled in cli.py
    input_dir = config["input_dir"]
    base_output_dir = Path(config["output_dir"])
    job_name = config.get("job_name", "default_job")
    
    # Create job-specific output directory
    output_dir = base_output_dir / job_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = datetime.now()

    # If self-test requested, run it and exit
    if config.get("self_test", False):
        manifest_path = Path(config["manifest"]) if "manifest" in config else None
        success = run_self_test(input_dir, output_dir, manifest_path)
        if success:
            print_success("Self-test passed. System ready.")
        else:
            print_error("Self-test failed. Please address the above issues.")
            sys.exit(1)
        sys.exit(0)

    # Attempt to find or load manifest
    manifest_path = config.get("manifest")
    if manifest_path:
        manifest_path = Path(manifest_path)
        # We'll trust the user on correctness. If invalid, validation will fail later.
        if not manifest_path.is_file():
            print_error(f"Specified manifest {manifest_path} not found.")
            sys.exit(1)
    else:
        # No manifest specified, try to find it automatically
        try:
            manifest_path = find_manifest(input_dir)
            if manifest_path is None:
                print_error("No manifest found. Please provide --manifest.")
                sys.exit(1)
        except ValueError as e:
            # Multiple manifests found
            print_error(str(e))
            print_error("Use --manifest to specify which manifest to use.")
            sys.exit(1)

    manifest_parser = ManifestParser(manifest_path)

    # Validate input directory and system readiness for actual processing
    validator = InputValidator(input_dir, output_dir, manifest_parser)
    validation_result = validator.validate_all()
    if not validation_result.can_proceed:
        print_error("Validation failed. Cannot proceed with processing.")
        for issue in validation_result.system_issues:
            print_error(f"System Issue: {issue.message}")
        sys.exit(1)

    # At this point, we have validated data and system. Proceed with processing.
    # Get ProcessingMode enum from string
    quality_mode = ProcessingMode.BALANCED  # Default
    try:
        quality_mode = ProcessingMode(config.get("quality_mode", "balanced"))
    except (ValueError, KeyError):
        print_warning(f"Invalid quality mode: {config.get('quality_mode')}. Using balanced.")
    
    # Extract resolution
    resolution = config.get("output_resolution", {"width": 3840, "height": 2160})
    output_resolution = (resolution["width"], resolution["height"])
    
    # Create ProcessingOptions
    options = ProcessingOptions(
        output_resolution=output_resolution,
        quality_mode=quality_mode,
        low_memory=config.get("low_memory", False),
        crf=config.get("crf")
    )
    
    processor = VideoProcessor(output_dir, options)
    
    # Capture the encoder type being used for job_info
    encoder_used = processor._available_encoders[0] if processor._available_encoders else EncoderType.SOFTWARE_X264
    is_hardware = encoder_used != EncoderType.SOFTWARE_X264
    
    # Track processing results for job_info
    processing_results = []

    # Process each valid clip
    for clip_name, clip_result in validation_result.clip_results.items():
        if clip_result.is_valid:
            result = processor.process_clip(clip_result)
            processing_results.append(result)
            if result.success:
                print_success(f"Processed clip: {clip_name}. Output: {result.output_path}")
            else:
                print_error(f"Failed to process clip {clip_name}: {result.error}")

    end_time = datetime.now()
    processing_time = end_time - start_time
    
    # Get system information
    sys_info = get_system_info()

    # Write enhanced job info
    job_info_path = output_dir / "job_info.txt"
    with open(job_info_path, "w", encoding='utf-8') as f:
        # 1. Job Metadata
        f.write("=" * 60 + "\n")
        f.write("JOB METADATA\n")
        f.write("=" * 60 + "\n")
        f.write(f"Job Name: {job_name}\n")
        f.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Processing Time: {processing_time}\n")
        f.write(f"Input Directory: {input_dir}\n")
        f.write(f"Output Directory: {output_dir}\n")
        f.write(f"Manifest: {manifest_path}\n\n")
        
        # 2. Processing Settings
        f.write("=" * 60 + "\n")
        f.write("PROCESSING SETTINGS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Output Resolution: {options.output_resolution[0]}x{options.output_resolution[1]}\n")
        f.write(f"Quality Mode: {options.quality_mode.value}\n")
        f.write(f"Encoder Used: {encoder_used.value} ({'' if is_hardware else 'no '}hardware acceleration)\n")
        f.write(f"Low Memory Mode: {'Enabled' if options.low_memory else 'Disabled'}\n")
        if options.crf is not None:
            f.write(f"Custom CRF Value: {options.crf}\n\n")
        else:
            f.write(f"CRF Value: Auto (based on quality mode)\n\n")
        
        # 3. Clip Status Summary
        f.write("=" * 60 + "\n")
        f.write("CLIP STATUS SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write("| {:<20} | {:<10} | {:<20} | {:<10} | {:<15} |\n".format(
            "Clip Name", "Status", "Output File", "Duration", "Frames Processed"
        ))
        f.write("|" + "-" * 22 + "|" + "-" * 12 + "|" + "-" * 22 + "|" + "-" * 12 + "|" + "-" * 17 + "|\n")
        
        # Add entries for all clips
        for result in processing_results:
            status = "COMPLETE" if result.success else "FAILED"
            output_file = os.path.basename(str(result.output_path)) if result.output_path else "N/A"
            duration = f"{result.duration:.2f}s" if result.success else "N/A"
            frames = str(result.frames_processed) if result.success else "N/A"
            
            f.write("| {:<20} | {:<10} | {:<20} | {:<10} | {:<15} |\n".format(
                result.clip.name, status, output_file, duration, frames
            ))
        
        f.write("\n")
        
        # 4. System Information
        f.write("=" * 60 + "\n")
        f.write("SYSTEM INFORMATION\n")
        f.write("=" * 60 + "\n")
        f.write(f"Python Version: {sys_info['python_version']}\n")
        f.write(f"FFmpeg: {sys_info['ffmpeg_version']}\n")
        f.write(f"Platform: {sys_info['os_platform']}\n")
        
        # Processing summary
        total_clips = len(processing_results)
        successful_clips = sum(1 for r in processing_results if r.success)
        f.write(f"\nProcessed {successful_clips}/{total_clips} clips successfully.\n")

    print_info("All done.")

if __name__ == "__main__":
    main()
