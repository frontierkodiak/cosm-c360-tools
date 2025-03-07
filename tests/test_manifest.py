# tests/test_manifest.py
from pathlib import Path
import pytest
from datetime import datetime
from src.cosmos.manifest import (
    Position, 
    ClipInfo, 
    ClipStatus, 
    ManifestParser, 
    find_manifest
)

# Test data
SAMPLE_MANIFEST = """
<Clip_Manifest NumDirs="498">
  <_1 Name="CLIP2" In="1.6261465427355111E-307" InIdx="228" Out="1.6261466707242047E-307" OutIdx="4110" Locked="True" InStr="07:27:16.618 08/13/2024" Epoch="1723559236.618" Pos="0H/0M/3.8S/" />
  <_2 Name="CLIP1" In="1.6261465850368715E-307" InIdx="1511" Out="1.6261470057932999E-307" OutIdx="14273" Locked="True" InStr="07:27:38.022 08/13/2024" Epoch="1723559258.0219998" Pos="0H/0M/25.1833333333333S/" />
</Clip_Manifest>
"""

@pytest.fixture
def sample_manifest(tmp_path):
    """Create a temporary manifest file for testing"""
    manifest_path = tmp_path / "test_manifest.xml"
    manifest_path.write_text(SAMPLE_MANIFEST)
    return manifest_path

class TestPosition:
    def test_from_valid_string(self):
        pos = Position.from_string("0H/0M/3.8S/")
        assert pos.hour == 0
        assert pos.minute == 0
        assert pytest.approx(pos.second, 0.001) == 3.8
        
    def test_from_invalid_string(self):
        with pytest.raises(ValueError):
            Position.from_string("invalid")
            
    def test_to_seconds(self):
        pos = Position(hour=1, minute=30, second=15.5)
        assert pytest.approx(pos.to_seconds(), 0.001) == 5415.5
        
    def test_to_string(self):
        pos = Position(hour=0, minute=0, second=3.8)
        assert pos.to_string() == "0H/0M/3.8S"

class TestClipInfo:
    @pytest.fixture
    def sample_clip(self):
        return ClipInfo(
            name="CLIP1",
            start_epoch=1723559258.022,
            end_epoch=1723559268.022,  # 10 seconds duration
            start_pos=Position(0, 0, 25.183),
            end_pos=Position(0, 0, 35.183),
            start_idx=1511,
            end_idx=14273,
            start_time=datetime(2024, 8, 13, 7, 27, 38, 22000)
        )
    
    def test_duration(self, sample_clip):
        assert pytest.approx(sample_clip.duration, 0.001) == 10.0
        
    def test_frame_count(self, sample_clip):
        assert sample_clip.frame_count == 12762

class TestManifestParser:
    def test_parser_initialization(self, sample_manifest):
        parser = ManifestParser(sample_manifest)
        assert len(parser.get_clips()) == 2
        
    def test_nonexistent_manifest(self):
        with pytest.raises(FileNotFoundError):
            ManifestParser(Path("nonexistent.xml"))
            
    def test_get_clip(self, sample_manifest):
        parser = ManifestParser(sample_manifest)
        clip = parser.get_clip("CLIP1")
        assert clip is not None
        assert clip.name == "CLIP1"
        assert pytest.approx(clip.start_epoch, 0.001) == 1723559258.022
        
    def test_clips_temporal_order(self, sample_manifest):
        parser = ManifestParser(sample_manifest)
        clips = parser.get_clips()
        assert len(clips) == 2
        assert clips[0].name == "CLIP2"  # Earlier timestamp
        assert clips[1].name == "CLIP1"
        
    def test_find_clip_for_timestamp(self, sample_manifest):
        parser = ManifestParser(sample_manifest)
        clip = parser.find_clip_for_timestamp(1723559236.618)
        assert clip is not None
        assert clip.name == "CLIP2"
        
    def test_update_clip_status(self, sample_manifest):
        parser = ManifestParser(sample_manifest)
        parser.update_clip_status("CLIP1", ClipStatus.COMPLETE)
        clip = parser.get_clip("CLIP1")
        assert clip.status == ClipStatus.COMPLETE

def test_find_manifest(tmp_path):
    # Test single manifest
    manifest_path = tmp_path / "test.xml"
    manifest_path.write_text(SAMPLE_MANIFEST)
    assert find_manifest(tmp_path) == manifest_path
    
    # Test no manifest
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    assert find_manifest(empty_dir) is None
    
    # Test multiple manifests
    another_manifest = tmp_path / "another.xml"
    another_manifest.write_text(SAMPLE_MANIFEST)
    with pytest.raises(ValueError):
        find_manifest(tmp_path)