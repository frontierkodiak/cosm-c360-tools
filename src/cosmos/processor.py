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
    PERFORMANCE = "performance"      # Faster, all threads
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
    APPLE_VIDEOTOOLBOX = "h264_videotoolbox"  # Apple Silicon hardware encoder
    SOFTWARE_X264 = "libx264"

    @classmethod
    def get_platform_encoders(cls) -> List['EncoderType']:
        """Get list of encoders available on current platform"""
        import platform
        system = platform.system().lower()
        
        # Base encoders available on all platforms
        encoders = [cls.SOFTWARE_X264]
        
        if system == 'darwin':
            # Apple Silicon/Intel Mac
            encoders.insert(0, cls.APPLE_VIDEOTOOLBOX)
        elif system == 'linux':
            # Linux with NVIDIA GPU
            encoders.insert(0, cls.NVIDIA_NVENC)
        elif system == 'windows':
            # Windows with NVIDIA GPU
            encoders.insert(0, cls.NVIDIA_NVENC)
            # Windows with AMD GPU
            encoders.insert(0, cls.AMD_AMF)
            # Windows with Intel GPU
            encoders.insert(0, cls.INTEL_QSV)
            
        return encoders

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
            
            # Get platform-specific encoders
            platform_encoders = EncoderType.get_platform_encoders()
            
            # Check each platform-specific encoder
            for encoder in platform_encoders:
                if encoder.value in output:
                    available.append(encoder)
                    self.logger.debug(f"Found encoder: {encoder.value}")
            
            # Always add software encoder as fallback
            if EncoderType.SOFTWARE_X264 not in available:
                available.append(EncoderType.SOFTWARE_X264)
                self.logger.debug("Added software encoder as fallback")
            
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
            ProcessingMode.PERFORMANCE: 28,
            ProcessingMode.LOW_MEMORY: 23,  # Same as BALANCED
            ProcessingMode.MINIMAL: 28      # Same as PERFORMANCE
        }[self.options.quality_mode]
        
        # Start with encoder-specific settings
        if encoder == EncoderType.NVIDIA_NVENC:
            settings = [
                "-c:v", "h264_nvenc",
                "-preset", "p7" if self.options.quality_mode == ProcessingMode.QUALITY else "p4",
                "-qp", str(crf)
            ]
        elif encoder == EncoderType.APPLE_VIDEOTOOLBOX:
            # Apple Silicon hardware encoder settings
            settings = [
                "-c:v", "h264_videotoolbox",
                "-allow_sw", "1",  # Allow software fallback if needed
                "-realtime", "0",  # Disable realtime mode for better quality
                "-b:v", "0",       # Use CRF mode
                "-crf", str(crf)
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
        # Log the output resolution we're scaling to
        self.logger.debug(f"Building filter complex for output resolution: {self.options.output_resolution}")
        
        # Build the tile processing part (matching working version)
        tile_processing = (
            # Crop overlapping regions from tiles
            "[0:v:0]crop=iw-{overlap}:ih-{overlap}:0:0[tl];"
            "[0:v:1]crop=iw-{overlap}:ih-{overlap}:{overlap}:0[tr];"
            "[0:v:2]crop=iw-{overlap}:ih-{overlap}:0:{overlap}[bl];"
            "[0:v:3]crop=iw-{overlap}:ih-{overlap}:{overlap}:{overlap}[br];"
            # Stack tiles horizontally
            "[tl][tr]hstack=2[top];"
            "[bl][br]hstack=2[bottom];"
            # Stack rows vertically
            "[top][bottom]vstack=2[full]"
        ).format(overlap=crop_overlap)
        
        # Add scaling to target resolution
        width, height = self.options.output_resolution
        scaling = f"[full]scale={width}:{height}:flags=lanczos[out]"
        
        # Combine the filters
        filter_complex = f"{tile_processing};{scaling}"
        
        self.logger.debug(f"Generated filter complex:\n{filter_complex}")
        return filter_complex

    def _create_concat_file(self, segments: List[SegmentInfo]) -> Path:
        """Create temporary concat file for ffmpeg"""
        # Use platform-agnostic temp file creation
        temp_file = Path(tempfile.mktemp(suffix='.txt'))
        
        # Log segment information
        self.logger.debug(f"Creating concat file with {len(segments)} segments")
        for i, segment in enumerate(segments):
            self.logger.debug(f"Segment {i}:")
            self.logger.debug(f"  Directory: {segment.directory}")
            self.logger.debug(f"  TS Files: {len(segment.ts_files)}")
            for ts_file in segment.ts_files:
                if not ts_file.exists():
                    self.logger.error(f"TS file does not exist: {ts_file}")
                else:
                    self.logger.debug(f"  - {ts_file}")
        
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
            
            # Log processing parameters
            self.logger.debug(f"Processing clip {clip_result.clip.name}")
            self.logger.debug(f"Output resolution: {self.options.output_resolution}")
            self.logger.debug(f"Quality mode: {self.options.quality_mode}")
            self.logger.debug(f"Low memory mode: {self.options.low_memory}")
            self.logger.debug(f"Created concat file at {concat_file}")
            self.logger.debug(f"Output will be written to {output_path}")
            
            # Log concat file contents for debugging
            with open(concat_file, 'r') as f:
                self.logger.debug(f"Concat file contents:\n{f.read()}")
                
            success = False
            error_messages = []
            
            # Determine thread count based on quality mode and low memory setting
            import multiprocessing
            total_threads = multiprocessing.cpu_count()
            
            # Set thread count based on quality mode and low memory flag
            if self.options.quality_mode == ProcessingMode.MINIMAL:
                # Minimal mode - always use single thread for max memory savings
                thread_count = 1
                self.logger.info("Using single thread processing (minimal mode)")
            elif self.options.low_memory:
                # Low memory mode - use half available threads
                thread_count = max(1, total_threads // 2)
                self.logger.info(f"Using reduced thread count: {thread_count} (low memory mode)")
            elif self.options.quality_mode == ProcessingMode.LOW_MEMORY:
                # Low memory quality mode - use half available threads
                thread_count = max(1, total_threads // 2)
                self.logger.info(f"Using reduced thread count: {thread_count} (low memory quality mode)")
            else:
                # Normal modes - no thread restrictions
                thread_count = None
                self.logger.info(f"Using all available threads")
                
            for encoder in self._available_encoders:
                try:
                    # Build base command
                    cmd = [
                        "ffmpeg", "-y",
                        "-f", "concat",
                        "-safe", "0",
                        "-i", str(concat_file)
                    ]
                    
                    # Add memory-saving options if enabled
                    memory_opts = []
                    if self.options.low_memory or self.options.quality_mode in [ProcessingMode.LOW_MEMORY, ProcessingMode.MINIMAL]:
                        # Add options to reduce memory usage
                        memory_opts = [
                            "-max_muxing_queue_size", "1024",  # Reduce muxing queue size
                            "-tile-columns", "0",              # Disable tiling to save memory
                            "-frame-parallel", "0"             # Disable parallel frame processing
                        ]
                        self.logger.info("Added memory-saving FFmpeg options")
                    
                    # Add filter complex
                    self.logger.debug(f"Building filter complex with output resolution: {self.options.output_resolution}")
                    filter_complex = self._build_filter_complex()
                    cmd.extend(["-filter_complex", filter_complex])
                    
                    # Map the output of the filter complex
                    cmd.extend(["-map", "[out]"])
                    
                    # Add encoder settings with thread control
                    use_threads = thread_count if (
                        encoder == EncoderType.SOFTWARE_X264 and 
                        (self.options.low_memory or 
                         self.options.quality_mode in [ProcessingMode.LOW_MEMORY, ProcessingMode.MINIMAL])
                    ) else None
                    
                    cmd.extend(self._get_encoder_settings(encoder, use_threads))
                    cmd.extend(memory_opts)
                    cmd.append(str(output_path))
                    
                    # Run ffmpeg with proper subprocess configuration for platform
                    self.logger.info(f"Processing {clip_result.clip.name} with {encoder.value}")
                    # Log the complete ffmpeg command with all arguments
                    self.logger.debug(f"Executing ffmpeg command:\n{' '.join(cmd)}")
                    
                    # Create subprocess with platform-specific settings
                    creation_flags = 0
                    if os.name == 'nt':  # Windows
                        creation_flags = subprocess.CREATE_NO_WINDOW
                    
                    result = subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        creationflags=creation_flags
                    )
                    
                    # Log command output at debug level
                    if result.stdout.strip():
                        self.logger.debug(f"FFmpeg stdout:\n{result.stdout.strip()}")
                    if result.stderr.strip():
                        self.logger.debug(f"FFmpeg stderr:\n{result.stderr.strip()}")
                    
                    success = True
                    break
                    
                except subprocess.SubprocessError as e:
                    error_msg = f"{encoder.value}: {e}"
                    self.logger.error(f"Encoder failed: {error_msg}")
                    error_messages.append(error_msg)
                    
                    # If we're in low memory mode and this is not the last encoder, try to free memory
                    if (self.options.low_memory or 
                        self.options.quality_mode in [ProcessingMode.LOW_MEMORY, ProcessingMode.MINIMAL]):
                        self.logger.info("Attempting to free memory before trying next encoder...")
                        import gc
                        gc.collect()  # Explicit garbage collection
                    
                    continue
                
            if not success:
                raise RuntimeError(
                    f"All encoders failed: {'; '.join(error_messages)}"
                )
            
            # Calculate processing statistics
            duration = clip_result.clip.duration
            frames = sum(seg.frame_count for seg in clip_result.segments)
            
            # Add platform-specific optimizations for output file
            if output_path.exists():
                # Attempt to minimize disk cache usage on Windows
                if os.name == 'nt':
                    try:
                        with open(str(output_path), 'rb+') as f:
                            # FILE_FLAG_NO_BUFFERING equivalent in Python
                            # This is a Windows-specific optimization
                            os.fsync(f.fileno())
                    except Exception as e:
                        self.logger.debug(f"Non-critical error optimizing file cache: {e}")
            
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
            if 'concat_file' in locals() and concat_file.exists():
                try:
                    concat_file.unlink()
                    self.logger.debug("Cleaned up temporary concat file")
                except Exception as e:
                    self.logger.debug(f"Failed to clean up concat file: {e}")
                    
            # Force garbage collection to free memory
            if self.options.low_memory or self.options.quality_mode in [ProcessingMode.LOW_MEMORY, ProcessingMode.MINIMAL]:
                import gc
                gc.collect()
                self.logger.debug("Forced garbage collection after processing")