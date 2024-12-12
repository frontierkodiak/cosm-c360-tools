# File: cosmos.py

import sys
from pathlib import Path

from src.cosmos.cli import run_cli
from src.cosmos.preflight import run_self_test
from src.cosmos.utils import print_info, print_error, print_success
from src.cosmos.manifest import find_manifest, ManifestParser
from src.cosmos.validation import InputValidator
from src.cosmos.processor import VideoProcessor, ProcessingOptions, ProcessingMode

def main():
    config = run_cli()

    input_dir = Path(config["input_dir"])
    output_dir = Path(config["output_dir"])
    job_name = config.get("job_name", "default_job")

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
    options = ProcessingOptions(
        output_resolution=(3840, 2160),
        quality_mode=ProcessingMode.BALANCED
    )
    processor = VideoProcessor(output_dir, options)

    # Process each valid clip
    for clip_name, clip_result in validation_result.clip_results.items():
        if clip_result.is_valid:
            result = processor.process_clip(clip_result)
            if result.success:
                print_success(f"Processed clip: {clip_name}. Output: {result.output_path}")
            else:
                print_error(f"Failed to process clip {clip_name}: {result.error}")

    # Write job info
    job_info_path = output_dir / "job_info.txt"
    with open(job_info_path, "w", encoding='utf-8') as f:
        f.write(f"Job Name: {job_name}\n")
        f.write(f"Input Directory: {input_dir}\n")
        f.write(f"Output Directory: {output_dir}\n")
        f.write(f"Manifest: {manifest_path}\n")
        f.write("Processing complete.\n")

    print_info("All done.")

if __name__ == "__main__":
    main()
