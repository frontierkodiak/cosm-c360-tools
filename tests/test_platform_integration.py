# tests/test_platform_integration.py

import os
import sys
import subprocess
import platform
from pathlib import Path
import pytest
import shutil

def get_platform_paths():
    """Get platform-specific paths for testing."""
    if platform.system() == "Linux":
        input_dir = "/datasets/dataZoo/clients/ladybird/batch_0/raw/"
        output_dir = "/datasets/dataZoo/clients/ladybird/batch_0/cosmos"
    elif platform.system() == "Windows":
        input_dir = "\\wsl.localhost\\Ubuntu-22.04\\home\\caleb\\ladybird\\batch_0\\raw"
        output_dir = "\\wsl.localhost\\Ubuntu-22.04\\home\\caleb\\ladybird\\batch_0\\cosmos"
    elif platform.system() == "Darwin":  # macOS
        input_dir = "/Users/caleb/local/ladybird/batch_0/raw"
        output_dir = "/Users/caleb/local/ladybird/batch_0/cosmos"
    else:
        pytest.skip(f"Unsupported platform: {platform.system()}")
    
    return input_dir, output_dir

def test_platform_conversion_1080p():
    """Test the full conversion pipeline outputting 1080p video."""
    input_dir, output_dir = get_platform_paths()
    
    # Create clean output directory
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the tool with 1080p output resolution
    cmd = [
        sys.executable,
        "cosmos.py",
        "--input-dir", input_dir,
        "--output-dir", output_dir,
        "--job-name", f"test_1080p_{platform.system().lower()}"
    ]
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output for debugging
    print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    
    # Check for successful execution
    assert result.returncode == 0, f"Tool failed with exit code {result.returncode}"
    
    # Verify output files exist
    output_files = list(Path(output_dir).glob("*.mp4"))
    assert len(output_files) > 0, "No output MP4 files were created"
    
    # Verify job_info.txt was created
    assert (Path(output_dir) / "job_info.txt").exists(), "job_info.txt was not created"
    
    # Return output files for potential further testing
    return output_files

def test_self_test():
    """Test that the self-test function works properly."""
    input_dir, output_dir = get_platform_paths()
    
    cmd = [
        sys.executable,
        "cosmos.py",
        "--self-test",
        "--input-dir", input_dir,
        "--output-dir", output_dir
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output for debugging
    print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    
    # Self-test should exit with code 0 if successful
    assert result.returncode == 0, f"Self-test failed with exit code {result.returncode}"
    assert "Self-test passed. System ready." in result.stdout, "Self-test success message not found"