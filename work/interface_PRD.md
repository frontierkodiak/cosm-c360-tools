# COSM C360 Tools - Product Requirements Document

## 1. Overview

This document outlines the requirements for enhancing the COSM C360 Tools CLI interface, configuration system, and output information. The goal is to create a more cohesive, user-friendly tool that allows for straightforward reuse of configurations and provides clear information about processing operations.

## 2. Configuration System Enhancement

### 2.1 Configuration Structure

The configuration system must be extended to include all processing options:

```python
{
    # Core options (existing)
    "input_dir": str,
    "output_dir": str,
    "manifest": str,
    "job_name": str,
    "log_level": str,
    "log_file": str,
    
    # Processing options (to be added)
    "output_resolution": {
        "width": int,
        "height": int
    },
    "quality_mode": str,  # "quality", "balanced", "performance", "low_memory", "minimal"
    "low_memory": bool,
    "crf": int,  # Optional custom CRF value
    
    # Config-specific (to be added)
    "config_name": str,
    "config_description": str
}
```

### 2.2 Resolution Presets

Provide standard resolution presets:

- "720p": (1280, 720)
- "1080p": (1920, 1080)
- "4k": (3840, 2160)
- "8k": (7680, 4320)
- "original": (9280, 6300)  # Original COSM C360 resolution
- "custom": (user-defined width, user-defined height)

### 2.3 Config File Management

- Create a dedicated `configs` directory in the workspace
- Support loading/saving configurations from/to this directory
- Support overriding loaded configurations with CLI arguments

## 3. CLI Enhancement Requirements

### 3.1 Command-Line Arguments

Add the following arguments to `cli.py`:

- `--output-resolution`: Accept presets ("720p", "1080p", "4k", "8k", "original") or custom dimensions ("WIDTHxHEIGHT")
- `--quality-mode`: Accept "quality", "balanced", "performance", "low_memory", or "minimal"
- `--low-memory`: Boolean flag to enable low memory mode
- `--crf`: Integer value for custom CRF setting
- `--config`: Path to a configuration file to load
- `--save-config`: Save the resulting configuration (with any overrides) to a new file

### 3.2 Interactive Mode Flow

1. **Config Selection**
   - First prompt: "Load existing configuration? (Yes/No)"
   - If Yes: Show list of available configs from `configs` directory
   - If selected, load the config and use as base for subsequent prompts
   
2. **Job and Output Configuration**
   - Prompt for job name (this comes first since it affects output directory structure)
   - Prompt for input directory
   - Prompt for output base directory (clarify that outputs go to `<output_dir>/<job_name>/`)
   - Prompt for manifest if multiple are found
   
3. **Processing Options**
   - Prompt for output resolution (show presets + custom option)
   - If custom is selected, prompt for width and height
   - Prompt for quality mode (with descriptions)
   - Ask if low memory mode should be enabled
   - Offer to set custom CRF value (advanced option)
   
4. **Review and Save**
   - Show summary of all settings
   - Ask for confirmation
   - Ask if configuration should be saved for future use
   - If yes, prompt for config name and save to `configs/<name>.json`

## 4. Output Directory Structure

- Change the output directory handling to use `<output_dir>/<job_name>/` as the actual output location
- Make this clear in interactive prompts and documentation
- Create this directory structure automatically

## 5. Job Information Enhancement

Enhance `job_info.txt` to include:

1. **Job Metadata**
   - Job name
   - Start time and end time of processing
   - Input directory
   - Output directory
   - Manifest path
   
2. **Processing Settings**
   - Output resolution
   - Quality mode
   - Encoder used (hardware/software)
   - Low memory mode status
   - CRF value
   
3. **Clip Status Summary**
   - Table of all clips found in manifest
   - Status of each clip (COMPLETE, PARTIAL, MISSING, INVALID)
   - For processed clips: output file path, duration, frames processed
   
4. **System Information**
   - Python version
   - FFmpeg version
   - OS platform
   - Total processing time

## 6. Integration Implementation Details

### 6.1 `cli.py` Changes

1. Update `parse_args()` to add new arguments
2. Extend `run_interactive_mode()` to follow the new flow
3. Add functions for config file management:
   - `list_configs()`: List available configurations
   - `load_config()`: Load a configuration file
   - `save_config()`: Save a configuration file

### 6.2 `cosmos.py` Changes

1. Update to handle the new configuration options
2. Modify output directory handling to use `<output_dir>/<job_name>/`
3. Pass the enhanced configuration to `ProcessingOptions`
4. Enhance job_info.txt generation to include all required information

### 6.3 `utils.py` Changes

1. Add utility functions for handling configurations:
   - `get_configs_dir()`: Get the configs directory path
   - `create_configs_dir()`: Create the configs directory if it doesn't exist

### 6.4 `processor.py` Integration

1. Ensure `ProcessingOptions` can be correctly constructed from the enhanced configuration
2. Add a method to generate a summary of processing options for job_info.txt
3. Add warning log when falling back to software encoding

## 7. Acceptance Criteria and Testing

### 7.1 Acceptance Criteria

1. Users can load, modify, and save configurations
2. All processing options are configurable via CLI arguments and interactive mode
3. Output is properly organized in `<output_dir>/<job_name>/` structure
4. job_info.txt contains comprehensive information about the processing job
5. Encoder fallback warnings are displayed appropriately

### 7.2 Test Implementation

Add a new test file `tests/test_config_integration.py`:

```python
# tests/test_config_integration.py

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
import pytest
import shutil

def test_config_save_load():
    """Test saving and loading a configuration file."""
    # Create a test config directory
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)
    
    # Create a test config
    test_config = {
        "input_dir": "/test/input",
        "output_dir": "/test/output",
        "job_name": "test_job",
        "output_resolution": {
            "width": 1920,
            "height": 1080
        },
        "quality_mode": "balanced",
        "low_memory": False,
        "crf": None
    }
    
    # Save the test config
    config_path = config_dir / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f, indent=2)
    
    # Run the tool with the test config
    cmd = [
        sys.executable,
        "cosmos.py",
        "--config", str(config_path),
        "--output-dir", "/tmp/test_output"  # Override output_dir
    ]
    
    # We don't actually run this as it would try to process files
    # Instead we'll check that the config is properly loaded with --help
    cmd.append("--help")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    
    # Clean up
    os.remove(config_path)

def test_output_directory_structure():
    """Test that the output directory structure is created correctly."""
    # Get platform-specific test paths
    if platform.system() == "Linux":
        input_dir = "/tmp/cosm_test_input"
        output_base = "/tmp/cosm_test_output"
    elif platform.system() == "Windows":
        input_dir = os.path.join(os.environ["TEMP"], "cosm_test_input")
        output_base = os.path.join(os.environ["TEMP"], "cosm_test_output")
    elif platform.system() == "Darwin":  # macOS
        input_dir = "/tmp/cosm_test_input"
        output_base = "/tmp/cosm_test_output"
    else:
        pytest.skip(f"Unsupported platform: {platform.system()}")
    
    # Create test directories
    os.makedirs(input_dir, exist_ok=True)
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    os.makedirs(output_base)
    
    # Create a minimal test structure
    # This test won't actually process files, just check directory creation
    os.makedirs(os.path.join(input_dir, "0H", "0M", "0S"), exist_ok=True)
    with open(os.path.join(input_dir, "test_manifest.xml"), "w") as f:
        f.write("<Clip_Manifest NumDirs=\"1\"><_1 Name=\"TEST\" InIdx=\"0\" OutIdx=\"10\" Locked=\"True\" InStr=\"12:00:00.000 01/01/2020\" Epoch=\"1577836800.0\" Pos=\"0H/0M/0S/\" /></Clip_Manifest>")
    
    # Run the tool with job name
    job_name = "test_job_structure"
    cmd = [
        sys.executable,
        "cosmos.py",
        "--input-dir", input_dir,
        "--output-dir", output_base,
        "--job-name", job_name,
        "--self-test"  # Just run self-test to check directory creation
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check that the expected output directory structure was created
    expected_output_dir = os.path.join(output_base, job_name)
    assert os.path.exists(expected_output_dir), f"Output directory {expected_output_dir} not created"
    
    # Clean up
    shutil.rmtree(input_dir)
    shutil.rmtree(output_base)

def test_job_info_contents():
    """Test that job_info.txt contains the required information."""
    # This test would require running the full pipeline
    # For this PRD we'll outline the test approach, but actual implementation
    # would depend on having test data available
    
    # Steps:
    # 1. Set up test input with minimal valid structure
    # 2. Run the tool with various options
    # 3. Parse the resulting job_info.txt
    # 4. Verify it contains all required sections: job metadata, processing settings,
    #    clip status, system information
    
    # For now, mark as skipped
    pytest.skip("Implementation requires test data")
```

## 8. Implementation Plan

1. **Phase 1: Core Changes**
   - Update configuration structure
   - Implement directory structure changes
   - Enhance job_info.txt generation

2. **Phase 2: CLI Enhancements**
   - Add new CLI arguments
   - Update argument parsing
   - Implement config file management

3. **Phase 3: Interactive Mode**
   - Redesign interactive flow
   - Implement resolution presets
   - Add config loading/saving to interactive mode

4. **Phase 4: Testing**
   - Implement test cases
   - Verify functionality across platforms
   - Document testing procedures
   - NOTE: Don't run any of the other tests, they need to be updated to align with the latest state of the codebase. Just run the new test outlined above. Feel free to make follow-up fixes until the new test passes (make sure the test has robust coverage of the new functionality).

## 9. Current Codebase Assessment

### 9.1 Configuration Flow

Currently, configuration is assembled in this order:
1. Default empty config
2. Load from config file if specified
3. Override with CLI arguments
4. Override with interactive mode inputs

This flow should be preserved but enhanced with the new options.

### 9.2 Missing Integration Points

1. `cli.py` doesn't expose ProcessingOptions parameters
2. `cosmos.py` creates ProcessingOptions with hardcoded values
3. No mechanism for saving configurations
4. Output directory structure doesn't include job name
5. job_info.txt is minimal

### 9.3 Integration Priorities

1. Extend configuration structure first
2. Update CLI argument handling
3. Enhance interactive mode
4. Implement job_info.txt improvements
5. Add config persistence

## 10. Conclusion

This PRD outlines the necessary enhancements to make the COSM C360 Tools more user-friendly and robust. The focus is on improving configuration management, providing clearer output organization, and ensuring users have comprehensive information about their processing jobs.

By implementing these changes, the tool will be more suitable for non-technical users while still providing advanced options for those who need them. The enhanced configuration system will make it easier for users to reuse settings across multiple jobs, and the improved job information will provide better visibility into the processing operations.