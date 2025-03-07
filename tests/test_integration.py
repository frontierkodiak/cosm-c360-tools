# File: tests/test_integration.py

import subprocess
import sys

def test_self_test_integration():
    input_dir = "/datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy"
    output_dir = "/datasets/dataZoo/clients/ladybird_data/LADYBIRD/cosmos_out"

    cmd = [
        sys.executable, "cosmos.py",
        "--self-test",
        "--input-dir", input_dir,
        "--output-dir", output_dir
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Self-test failed with non-zero exit code: {result.returncode}\nSTDERR: {result.stderr}"
    assert "Self-test passed. System ready." in result.stdout, f"Expected success message not in output.\nSTDOUT: {result.stdout}"
\