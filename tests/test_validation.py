# tests/test_validation.py
import json
from pathlib import Path
import pytest
import shutil
import subprocess
from datetime import datetime

from cosmos.validation import (
    InputValidator,
    ValidationLevel,
    ValidationIssue,
    SegmentInfo,
    ClipValidationResult,
    ValidationResult
)
from cosmos.manifest import Position, ClipInfo, ManifestParser

# Test fixtures
@pytest.fixture
def mock_input_dir(tmp_path):
    """Create a mock input directory structure with test data"""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    
    # Create a simple directory structure
    # 0H/0M/25S - 0H/0M/27S
    base = input_dir / "0H" / "0M"
    base.mkdir(parents=True)
    
    # Create segment directories with meta.json files
    for second in range(25, 28):
        segment_dir = base / f"{second}S"
        segment_dir.mkdir()
        
        # Create meta.json
        meta = {
            "Time": {
                "x0": 1723559258.0 + second,
                "xi-x0": [0.0, 0.017, 0.033, 0.050]
            }
        }
        with open(segment_dir / "meta.json", "w") as f:
            json.dump(meta, f)
            
        # Create dummy .ts files
        for i in range(4):
            (segment_dir / f"chunk_{i}.ts").touch()
    
    return input_dir

@pytest.fixture
def mock_output_dir(tmp_path):
    """Create a mock output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir

@pytest.fixture
def sample_manifest(tmp_path):
    """Create a test manifest file"""
    manifest_content = """
    <Clip_Manifest NumDirs="498">
      <_1 Name="CLIP1" InIdx="1511" OutIdx="14273" Locked="True" 
          InStr="07:27:38.022 08/13/2024" Epoch="1723559258.022" 
          Pos="0H/0M/25.1833333333333S/" />
    </Clip_Manifest>
    """
    manifest_path = tmp_path / "test_manifest.xml"
    manifest_path.write_text(manifest_content)
    return manifest_path

@pytest.fixture
def validator(mock_input_dir, mock_output_dir, sample_manifest):
    """Create an InputValidator instance with test data"""
    parser = ManifestParser(sample_manifest)
    return InputValidator(mock_input_dir, mock_output_dir, parser)

class TestSegmentInfo:
    @pytest.fixture
    def sample_segment(self, tmp_path):
        """Create a sample SegmentInfo object"""
        return SegmentInfo(
            directory=tmp_path,
            start_time=1723559258.022,
            frame_timestamps=[
                1723559258.022,
                1723559258.039,
                1723559258.056
            ],
            ts_files=[
                tmp_path / "1.ts",
                tmp_path / "2.ts",
                tmp_path / "3.ts"
            ]
        )
    
    def test_end_time(self, sample_segment):
        assert sample_segment.end_time == 1723559258.056
        
    def test_frame_count(self, sample_segment):
        assert sample_segment.frame_count == 3
        
    def test_has_all_files(self, sample_segment):
        assert sample_segment.has_all_files is True

class TestInputValidator:
    def test_validate_system_ffmpeg_missing(self, validator, monkeypatch):
        """Test system validation when ffmpeg is not available"""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        issues = validator.validate_system()
        
        assert any(
            issue.level == ValidationLevel.ERROR and "FFmpeg" in issue.message
            for issue in issues
        )
    
    def test_validate_segment_valid(self, validator, mock_input_dir):
        """Test validation of a valid segment directory"""
        segment_dir = mock_input_dir / "0H" / "0M" / "25S"
        segment_info = validator.validate_segment(segment_dir)
        
        assert segment_info is not None
        assert segment_info.frame_count == 4
        assert len(segment_info.ts_files) == 4
        
    def test_validate_segment_invalid_meta(self, mock_input_dir):
        """Test validation with invalid meta.json"""
        segment_dir = mock_input_dir / "0H" / "0M" / "25S"
        
        # Corrupt meta.json
        with open(segment_dir / "meta.json", "w") as f:
            f.write("invalid json")
            
        validator = InputValidator(
            mock_input_dir,
            mock_input_dir / "output",
            ManifestParser(mock_input_dir / "manifest.xml")
        )
        
        segment_info = validator.validate_segment(segment_dir)
        assert segment_info is None
    
    def test_validate_clip(self, validator):
        """Test validation of a complete clip"""
        clip = validator.manifest_parser.get_clips()[0]
        result = validator.validate_clip(clip)
        
        assert isinstance(result, ClipValidationResult)
        assert len(result.segments) > 0
        assert result.is_valid
        
    def test_validate_clip_missing_segments(self, validator, mock_input_dir):
        """Test validation with missing segments"""
        # Remove a segment directory
        shutil.rmtree(mock_input_dir / "0H" / "0M" / "26S")
        
        clip = validator.manifest_parser.get_clips()[0]
        result = validator.validate_clip(clip)
        
        assert not result.is_valid
        assert len(result.missing_segments) > 0
        
    def test_validate_all(self, validator):
        """Test complete validation process"""
        result = validator.validate_all()
        
        assert isinstance(result, ValidationResult)
        assert result.can_proceed
        assert result.available_space > 0
        assert result.total_size_estimate > 0
        
    def test_validation_with_no_space(self, validator, monkeypatch):
        """Test validation when disk space is insufficient"""
        def mock_disk_usage(*args):
            return type('Usage', (), {'free': 0})()
            
        monkeypatch.setattr(shutil, "disk_usage", mock_disk_usage)
        
        result = validator.validate_all()
        assert not result.can_proceed

def test_validation_issue_creation():
    """Test ValidationIssue creation and attributes"""
    issue = ValidationIssue(
        level=ValidationLevel.ERROR,
        message="Test error",
        context="Test context",
        help_text="Test help"
    )
    
    assert issue.level == ValidationLevel.ERROR
    assert issue.message == "Test error"
    assert issue.context == "Test context"
    assert issue.help_text == "Test help"