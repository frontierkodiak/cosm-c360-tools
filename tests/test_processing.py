# tests/test_processing.py
import os
from pathlib import Path
import pytest
import subprocess
from unittest.mock import Mock, patch

from src.cosmos.processor import (
    ProcessingMode,
    ProcessingOptions,
    EncoderType,
    ProcessingResult,
    VideoProcessor
)
from src.cosmos.validation import ClipValidationResult, SegmentInfo
from src.cosmos.manifest import ClipInfo, Position

# Test fixtures
@pytest.fixture
def mock_clip_info():
    """Create a sample ClipInfo object"""
    return ClipInfo(
        name="TEST_CLIP",
        start_epoch=1723559258.022,
        end_epoch=1723559268.022,
        start_pos=Position(0, 0, 25.183),
        end_pos=Position(0, 0, 35.183),
        start_idx=1511,
        end_idx=14273,
        start_time=None  # Not needed for these tests
    )

@pytest.fixture
def mock_segments(tmp_path):
    """Create sample segment information"""
    segments = []
    for i in range(3):
        segment_dir = tmp_path / f"segment_{i}"
        segment_dir.mkdir()
        ts_files = [
            segment_dir / f"chunk_{j}.ts" for j in range(4)
        ]
        for ts_file in ts_files:
            ts_file.touch()
            
        segments.append(SegmentInfo(
            directory=segment_dir,
            start_time=1723559258.022 + i,
            frame_timestamps=[
                1723559258.022 + i + j*0.017 for j in range(4)
            ],
            ts_files=ts_files
        ))
    return segments

@pytest.fixture
def mock_validation_result(mock_clip_info, mock_segments):
    """Create a sample validation result"""
    return ClipValidationResult(
        clip=mock_clip_info,
        segments=mock_segments,
        missing_segments=[],
        issues=[],
        estimated_size=1000000
    )

@pytest.fixture
def processor(tmp_path):
    """Create a VideoProcessor instance with test configuration"""
    options = ProcessingOptions(
        output_resolution=(3840, 2160),
        quality_mode=ProcessingMode.BALANCED
    )
    return VideoProcessor(tmp_path / "output", options)

class TestVideoProcessor:
    def test_encoder_detection(self, processor):
        """Test encoder detection and ordering"""
        # Mock ffmpeg -encoders output
        ffmpeg_output = """
        Encoders:
         V..... libx264        x264 H.264 / AVC / MPEG-4 AVC
         V..... h264_nvenc     NVIDIA NVENC H.264 encoder
        """
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = ffmpeg_output
            mock_run.return_value.returncode = 0
            
            encoders = processor._detect_encoders()
            
            assert EncoderType.NVIDIA_NVENC in encoders
            assert EncoderType.SOFTWARE_X264 in encoders
            assert encoders.index(EncoderType.NVIDIA_NVENC) < encoders.index(EncoderType.SOFTWARE_X264)

    def test_encoder_detection_fallback(self, processor):
        """Test fallback to software encoding when detection fails"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.SubprocessError()
            
            encoders = processor._detect_encoders()
            
            assert len(encoders) == 1
            assert encoders[0] == EncoderType.SOFTWARE_X264

    def test_filter_complex_generation(self, processor):
        """Test FFmpeg filter complex string generation"""
        filter_complex = processor._build_filter_complex(crop_overlap=32)
        
        assert "[0:v:0]crop" in filter_complex
        assert "hstack=2" in filter_complex
        assert "vstack=2" in filter_complex

    def test_encoder_settings_quality_modes(self, processor):
        """Test encoder settings for different quality modes"""
        # Test QUALITY mode
        options = ProcessingOptions(
            output_resolution=(3840, 2160),
            quality_mode=ProcessingMode.QUALITY
        )
        processor.options = options
        settings = processor._get_encoder_settings(EncoderType.SOFTWARE_X264)
        assert "slower" in settings
        assert "-crf" in settings
        assert "18" in settings  # Highest quality CRF
        
        # Test PERFORMANCE mode
        options.quality_mode = ProcessingMode.PERFORMANCE
        settings = processor._get_encoder_settings(EncoderType.SOFTWARE_X264)
        assert "medium" in settings
        assert "-crf" in settings
        assert "28" in settings  # Lower quality CRF

    def test_thread_control(self, processor):
        """Test thread control for different processing modes"""
        import multiprocessing
        total_threads = multiprocessing.cpu_count()
        
        # Test LOW_MEMORY mode
        options = ProcessingOptions(
            output_resolution=(3840, 2160),
            quality_mode=ProcessingMode.LOW_MEMORY
        )
        processor.options = options
        settings = processor._get_encoder_settings(
            EncoderType.SOFTWARE_X264,
            thread_count=total_threads // 2
        )
        assert "-threads" in settings
        assert str(total_threads // 2) in settings
        
        # Test MINIMAL mode
        options.quality_mode = ProcessingMode.MINIMAL
        settings = processor._get_encoder_settings(
            EncoderType.SOFTWARE_X264,
            thread_count=1
        )
        assert "-threads" in settings
        assert "1" in settings

    @pytest.mark.parametrize("platform", ["win32", "linux", "darwin"])
    def test_cross_platform_paths(self, processor, mock_validation_result, platform):
        """Test path handling across different platforms"""
        with patch('os.name', platform):
            concat_file = processor._create_concat_file(mock_validation_result.segments)
            
            # Check concat file contents
            with open(concat_file) as f:
                content = f.read()
                
            # Verify forward slashes are used regardless of platform
            assert '\\' not in content
            assert all(line.startswith("file '") for line in content.splitlines() if line)

    @patch('subprocess.run')
    def test_process_clip(self, mock_run, processor, mock_validation_result):
        """Test complete clip processing workflow"""
        # Mock successful ffmpeg execution
        mock_run.return_value.returncode = 0
        
        result = processor.process_clip(mock_validation_result)
        
        assert result.success
        assert result.frames_processed > 0
        assert result.output_path.name == f"{mock_validation_result.clip.name}.mp4"
        
        # Verify ffmpeg was called with expected arguments
        assert mock_run.called
        cmd_args = mock_run.call_args[0][0]
        assert "ffmpeg" in cmd_args
        assert "-filter_complex" in cmd_args
        
    @patch('subprocess.run')
    def test_process_clip_error_handling(self, mock_run, processor, mock_validation_result):
        """Test error handling during processing"""
        # Mock ffmpeg failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        
        result = processor.process_clip(mock_validation_result)
        
        assert not result.success
        assert result.error is not None

    def test_windows_specific_flags(self, processor):
        """Test Windows-specific subprocess flags"""
        with patch('os.name', 'nt'):
            # Mock the processing to check command construction
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                processor.process_clip(mock_validation_result)
                
                # Verify CREATE_NO_WINDOW flag was used
                assert 'creationflags' in mock_run.call_args[1]
                assert mock_run.call_args[1]['creationflags'] == subprocess.CREATE_NO_WINDOW