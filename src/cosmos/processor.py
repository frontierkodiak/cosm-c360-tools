import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import subprocess
import tempfile
import logging

from .validation import ClipValidationResult, SegmentInfo
from .manifest import ClipInfo

class ProcessingMode(Enum):
    QUALITY = "quality"        # Highest quality, all threads
    BALANCED = "balanced"      # Good quality, all threads
    PERFORMANCE = "speed"      # Faster, all threads
    LOW_MEMORY = "low_memory"  # Half threads
    MINIMAL = "minimal"        # Single thread

@dataclass
class ProcessingOptions:
    """Configuration for video processing"""
    output_resolution: Tuple[int, int]  # Width, height
    quality_mode: ProcessingMode
    low_memory: bool = False
    crf: Optional[int] = None  # Custom CRF value if specified

class EncoderType(Enum):
    """Available encoder types"""
    NVIDIA_NVENC = "h264_nvenc"
    AMD_AMF = "h264_amf"
    INTEL_QSV = "h264_qsv"
    SOFTWARE_X264 = "libx264"

@dataclass
class ProcessingResult:
    """Results from processing a clip"""
    clip: ClipInfo
    output_path: Path
    duration: float
    frames_processed: int
    success: bool
    error: Optional[str] = None

class VideoProcessor:
    """
    Handles video processing operations for COSM camera output.
    
    This class manages:
    - Segment concatenation
    - Tile extraction and alignment
    - Frame assembly
    - Output encoding
    """
    
    def __init__(self, 
                 output_dir: Path,
                 options: ProcessingOptions,
                 logger: Optional[logging.Logger] = None):
        self.output_dir = output_dir
        self.options = options
        self.logger = logger or logging.getLogger(__name__)
        self._available_encoders = self._detect_encoders()
        
        self.logger.debug(f"Initialized VideoProcessor with options: {options}")
        self.logger.debug(f"Available encoders: {[e.value for e in self._available_encoders]}")

    def _detect_encoders(self) -> List[EncoderType]:
        """
        Detect available encoders on the system.
        Returns list of encoders in preferred order.
        """
        available = []
        try:
            # Query ffmpeg for encoder list
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output to detect available encoders
            output = result.stdout.lower()
            
            # Check for hardware encoders first
            if "h264_nvenc" in output:
                available.append(EncoderType.NVIDIA_NVENC)
            if "h264_amf" in output:
                available.append(EncoderType.AMD_AMF)
            if "h264_qsv" in output:
                available.append(EncoderType.INTEL_QSV)
            
            # Software encoder should always be available
            available.append(EncoderType.SOFTWARE_X264)
            
        except subprocess.SubprocessError:
            # If ffmpeg query fails, default to software encoding
            self.logger.warning("Failed to detect encoders, defaulting to software")
            available.append(EncoderType.SOFTWARE_X264)
            
        return available

    def _get_encoder_settings(self, 
                            encoder: EncoderType,
                            thread_count: Optional[int] = None) -> List[str]:
        """
        Get ffmpeg arguments for specified encoder
        
        Args:
            encoder: Encoder to use
            thread_count: Number of threads to use (None for auto)
        """
        # Base quality settings
        crf = self.options.crf or {
            ProcessingMode.QUALITY: 18,
            ProcessingMode.BALANCED: 23,
            ProcessingMode.PERFORMANCE: 28
        }[self.options.quality_mode]
        
        # Start with encoder-specific settings
        if encoder == EncoderType.NVIDIA_NVENC:
            settings = [
                "-c:v", "h264_nvenc",
                "-preset", "p7" if self.options.quality_mode == ProcessingMode.QUALITY else "p4",
                "-qp", str(crf)
            ]
        elif encoder == EncoderType.SOFTWARE_X264:
            settings = [
                "-c:v", "libx264",
                "-preset", "slower" if self.options.quality_mode == ProcessingMode.QUALITY else "medium",
                "-crf", str(crf)
            ]
            
            # Add thread control for software encoding
            if thread_count is not None:
                settings.extend([
                    "-threads", str(thread_count),
                    "-x264-params", f"threads={thread_count}"
                ])
        else:
            # Default settings for other encoders
            settings = ["-c:v", "libx264", "-crf", str(crf)]
        
        return settings

    def _build_filter_complex(self, 
                            crop_overlap: int = 32) -> str:
        """Build ffmpeg filter complex for tile processing."""
        filter_complex = (
            # Crop overlapping regions from tiles
            "[0:v:0]crop=iw-{overlap}:ih-{overlap}:0:0[tl];"
            "[0:v:1]crop=iw-{overlap}:ih-{overlap}:{overlap}:0[tr];"
            "[0:v:2]crop=iw-{overlap}:ih-{overlap}:0:{overlap}[bl];"
            "[0:v:3]crop=iw-{overlap}:ih-{overlap}:{overlap}:{overlap}[br];"
            # Stack tiles horizontally
            "[tl][tr]hstack=2[top];"
            "[bl][br]hstack=2[bottom];"
            # Stack rows vertically
            "[top][bottom]vstack=2"
        ).format(overlap=crop_overlap)
        
        self.logger.debug(f"Generated filter complex:\n{filter_complex}")
        return filter_complex

    def _create_concat_file(self, segments: List[SegmentInfo]) -> Path:
        """Create temporary concat file for ffmpeg"""
        # Use platform-agnostic temp file creation
        temp_file = Path(tempfile.mktemp(suffix='.txt'))
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                for ts_file in segment.ts_files:
                    # Use forward slashes even on Windows
                    path_str = str(ts_file.absolute()).replace('\\', '/')
                    f.write(f"file '{path_str}'\n")
                    
        return temp_file

    def process_clip(self,
                    clip_result: ClipValidationResult) -> ProcessingResult:
        """Process a validated clip."""
        try:
            output_path = self.output_dir / f"{clip_result.clip.name}.mp4"
            concat_file = self._create_concat_file(clip_result.segments)
            
            # Determine thread count for software encoding
            if self.options.low_memory:
                import multiprocessing
                total_threads = multiprocessing.cpu_count()
                # Use half threads in low memory mode
                thread_count = max(1, total_threads // 2)
            else:
                thread_count = None
                
            self.logger.debug(f"Processing clip {clip_result.clip.name}")
            self.logger.debug(f"Created concat file at {concat_file}")
            self.logger.debug(f"Output will be written to {output_path}")
            
            # Log concat file contents for debugging
            with open(concat_file, 'r') as f:
                self.logger.debug(f"Concat file contents:\n{f.read()}")
                
            success = False
            error_messages = []
            
            for encoder in self._available_encoders:
                try:
                    # Build base command
                    cmd = [
                        "ffmpeg", "-y",
                        "-f", "concat",
                        "-safe", "0",
                        "-i", str(concat_file),
                        "-filter_complex", self._build_filter_complex()
                    ]
                    
                    # Add encoder settings with thread control for software encoding
                    use_threads = thread_count if (
                        encoder == EncoderType.SOFTWARE_X264 and 
                        self.options.low_memory
                    ) else None
                    
                    cmd.extend(self._get_encoder_settings(encoder, use_threads))
                    cmd.append(str(output_path))
                    
                    # Run ffmpeg with proper subprocess configuration for Windows
                    self.logger.info(f"Processing {clip_result.clip.name} with {encoder.value}")
                    # Log the complete ffmpeg command
                    self.logger.debug(f"Executing ffmpeg command:\n{' '.join(cmd)}")
                    subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    
                    # # Log ffmpeg output
                    # if result.stdout:
                    #     self.logger.debug(f"FFmpeg stdout:\n{result.stdout}")
                    # if result.stderr:
                    #     self.logger.debug(f"FFmpeg stderr:\n{result.stderr}")
                    
                    success = True
                    break
                    
                except subprocess.SubprocessError as e:
                    error_msg = f"{encoder.value}: {e}"
                    self.logger.error(f"Encoder failed: {error_msg}")
                    error_messages.append(error_msg)
                    continue
                
            if not success:
                raise RuntimeError(
                    f"All encoders failed: {'; '.join(error_messages)}"
                )
            
            # Calculate processing statistics
            duration = clip_result.clip.duration
            frames = sum(seg.frame_count for seg in clip_result.segments)
            
            return ProcessingResult(
                clip=clip_result.clip,
                output_path=output_path,
                duration=duration,
                frames_processed=frames,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Error processing {clip_result.clip.name}: {e}")
            return ProcessingResult(
                clip=clip_result.clip,
                output_path=None,
                duration=0,
                frames_processed=0,
                success=False,
                error=str(e)
            )
            
        finally:
            # Cleanup
            if 'concat_file' in locals():
                concat_file.unlink()