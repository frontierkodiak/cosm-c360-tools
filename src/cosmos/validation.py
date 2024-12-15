from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import json
import shutil
import subprocess
from datetime import datetime
import logging

from .manifest import ClipInfo, ClipStatus, Position, ManifestParser

class ValidationLevel(Enum):
    """Severity level for validation issues"""
    ERROR = "error"          # Fatal issue, cannot proceed
    WARNING = "warning"      # Potential issue, can proceed with caution
    INFO = "info"            # Informational note

@dataclass
class ValidationIssue:
    """Details about a validation problem"""
    level: ValidationLevel
    message: str
    context: Optional[str] = None
    help_text: Optional[str] = None

@dataclass
class SegmentInfo:
    """Information about a video segment from meta.json"""
    directory: Path
    start_time: float
    frame_timestamps: List[float]
    ts_files: List[Path]
    
    @property
    def end_time(self) -> float:
        """Get end time of segment from last frame timestamp"""
        return self.frame_timestamps[-1] if self.frame_timestamps else self.start_time
    
    @property
    def frame_count(self) -> int:
        """Number of frames in segment"""
        return len(self.frame_timestamps)
    
    @property
    def has_all_files(self) -> bool:
        """Check if all expected .ts files are present"""
        # Note: This check is no longer strictly 1:1 files to frames,
        # because each .ts file can contain multiple frames.
        # If desired, we can remove or adjust this method.
        return True  # For now, we always consider that we have all files. 
                     # Validation is handled by the increments vs expected_frames check.

@dataclass
class ClipValidationResult:
    """Validation results for a single clip"""
    clip: ClipInfo
    segments: List[SegmentInfo]
    missing_segments: List[Position]
    issues: List[ValidationIssue]
    estimated_size: int  # in bytes
    
    @property
    def is_valid(self) -> bool:
        """Check if clip has enough valid data to process"""
        return bool(self.segments) and not any(
            issue.level == ValidationLevel.ERROR 
            for issue in self.issues
        )

@dataclass
class ValidationResult:
    """Complete validation results for input directory"""
    system_issues: List[ValidationIssue]
    clip_results: Dict[str, ClipValidationResult]
    total_size_estimate: int
    available_space: int
    
    @property
    def can_proceed(self) -> bool:
        """Check if processing can proceed with any clips"""
        return (
            not any(i.level == ValidationLevel.ERROR for i in self.system_issues)
            and any(r.is_valid for r in self.clip_results.values())
            and self.available_space > self.total_size_estimate
        )

class InputValidator:
    """
    Validates input data and system requirements for COSM video processing.
    
    Performs checks at multiple levels:
    1. System requirements (ffmpeg, space, etc.)
    2. Input directory structure
    3. Clip data integrity
    4. Segment availability and validity
    """
    
    def __init__(self, 
                 input_dir: Path,
                 output_dir: Path,
                 manifest_parser: ManifestParser):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.manifest_parser = manifest_parser
        self.logger = logging.getLogger(__name__)
        
    def validate_system(self) -> List[ValidationIssue]:
        """Check system requirements"""
        issues = []
        
        # Check ffmpeg installation
        try:
            subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                check=True
            )
        except subprocess.CalledProcessError:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="FFmpeg not found",
                help_text="Please install FFmpeg to process videos"
            ))
        except FileNotFoundError:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="FFmpeg not found in system PATH",
                help_text="Please install FFmpeg and ensure it's in your PATH"
            ))
            
        # Check output directory
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            test_file = self.output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Cannot write to output directory: {e}",
                help_text="Check permissions and disk space"
            ))
            
        return issues
    
    def validate_segment(self, 
                         segment_dir: Path,
                         clip_fps: int) -> Optional[SegmentInfo]:
        """
        Validate a segment directory and its meta.json using the clip-level FPS.
        
        Args:
            segment_dir: Path to segment directory
            clip_fps: Frames per second derived from the entire clip
            
        Returns:
            SegmentInfo if valid, None if invalid
        """
        meta_path = segment_dir / "meta.json"
        self.logger.debug(f"Validating segment at {segment_dir}")
        
        if not meta_path.is_file():
            self.logger.debug(f"No meta.json found in {segment_dir}")
            return None
        
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                self.logger.debug(f"Loaded meta.json: {meta}")
                
            if "Time" not in meta or "x0" not in meta["Time"] or "xi-x0" not in meta["Time"]:
                self.logger.error(f"Invalid meta.json structure in {segment_dir}")
                return None
                
            start_time = meta["Time"]["x0"]
            increments = meta["Time"]["xi-x0"]
            
            # Get all .ts files in directory
            ts_files = sorted(segment_dir.glob("*.ts"))
            self.logger.debug(f"Found {len(ts_files)} .ts files in {segment_dir}")
            
            # Derive segment duration:
            # Each ts file covers approximately 0.1s of real time.
            # So, segment_duration_s = number_of_ts_files * 0.1s
            segment_duration_s = len(ts_files) * 0.1
            
            # Expected frames in this segment based on clip_fps and segment duration
            expected_frames = int(round(clip_fps * segment_duration_s))
            
            # Check if increments match the expected frame count
            if len(increments) != expected_frames:
                self.logger.warning(
                    f"Mismatch in {segment_dir}: expected {expected_frames} frames "
                    f"(FPS={clip_fps}, duration={segment_duration_s:.1f}s) but got {len(increments)}."
                )
                return None
            
            # Create timestamps for each frame
            timestamps = [start_time + inc for inc in increments]
            
            self.logger.debug(
                f"Segment validation successful: start_time={start_time}, "
                f"frame_count={len(timestamps)}, file_count={len(ts_files)}, "
                f"expected_frames={expected_frames}"
            )
            
            return SegmentInfo(
                directory=segment_dir,
                start_time=start_time,
                frame_timestamps=timestamps,
                ts_files=ts_files
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(f"Warning: failed to parse meta.json in {segment_dir}: {e}")
            return None
    
    def validate_clip(self, clip: ClipInfo) -> ClipValidationResult:
        """Validate all segments for a clip"""
        issues = []
        segments = []
        missing_positions = []
        
        self.logger.debug(f"Validating clip: {clip.name}")
        self.logger.debug(
            f"Clip boundaries: "
            f"start={clip.start_pos.to_string()}, "
            f"frames={clip.start_idx}-{clip.end_idx}"
        )

        # Derive FPS from the clip
        try:
            clip_fps = clip.fps
        except ValueError as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Cannot determine FPS for clip {clip.name}: {e}"
            ))
            # If we can't determine FPS, no point checking segments further
            return ClipValidationResult(
                clip=clip,
                segments=[],
                missing_segments=[],
                issues=issues,
                estimated_size=0
            )

        start_sec = int(clip.start_pos.second)
        end_sec = int(clip.end_pos.second) if clip.end_pos else start_sec + 60
        total_positions = end_sec - start_sec + 1
        
        self.logger.debug(f"Scanning {total_positions} second positions")

        last_success_pos = None
        for second in range(start_sec, end_sec + 1):
            pos = Position(
                hour=clip.start_pos.hour,
                minute=clip.start_pos.minute,
                second=second
            )
            
            segment_dir = self.input_dir / pos.path_fragment()
            self.logger.debug(f"Checking position {pos.to_string()} -> {segment_dir}")
            
            if not segment_dir.is_dir():
                self.logger.debug(f"Missing segment directory: {segment_dir}")
                missing_positions.append(pos)
                continue

            if segment_info := self.validate_segment(segment_dir, clip_fps):
                self.logger.debug(
                    f"Valid segment found: {len(segment_info.ts_files)} files, "
                    f"{len(segment_info.frame_timestamps)} frames"
                )
                segments.append(segment_info)
                last_success_pos = pos
            else:
                self.logger.debug(f"Invalid segment at {segment_dir}")
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Invalid segment at {pos.path_fragment()}",
                    context="Missing or corrupt meta.json or frame mismatch"
                ))

        # Report segment coverage
        found_segments = len(segments)
        if found_segments == 0:
            self.logger.warning(f"No valid segments found for clip {clip.name}")
        else:
            coverage = (found_segments / total_positions) * 100
            self.logger.info(
                f"Clip {clip.name}: Found {found_segments}/{total_positions} "
                f"segments ({coverage:.1f}% coverage)"
            )
            for segment in segments:
                self.logger.debug(
                    f"Segment {segment.directory.name}: "
                    f"{len(segment.ts_files)} files, "
                    f"time range: {segment.start_time:.3f}-{segment.end_time:.3f}"
                )

        # Estimate output size (very rough)
        estimated_size = len(segments) * 100 * 1024 * 1024

        # Update clip end info if we have segments
        if segments:
            clip.end_epoch = segments[-1].end_time
            if last_success_pos:
                clip.end_pos = last_success_pos

        return ClipValidationResult(
            clip=clip,
            segments=segments,
            missing_segments=missing_positions,
            issues=issues,
            estimated_size=estimated_size
        )
    
    def validate_all(self) -> ValidationResult:
        """
        Perform complete validation of system and input data
        
        Returns:
            ValidationResult with all validation details
        """
        # Check system requirements
        system_issues = self.validate_system()
        
        # Validate each clip
        clip_results = {}
        total_size = 0
        
        for clip in self.manifest_parser.get_clips():
            result = self.validate_clip(clip)
            clip_results[clip.name] = result
            total_size += result.estimated_size
            
            # Update clip status based on validation
            if not result.segments:
                clip.status = ClipStatus.MISSING
            elif result.missing_segments:
                clip.status = ClipStatus.PARTIAL
            else:
                clip.status = ClipStatus.COMPLETE
        
        # Check available space
        try:
            available = shutil.disk_usage(self.output_dir).free
        except Exception:
            available = 0
            system_issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Cannot determine available disk space",
                help_text="Check output directory permissions"
            ))
        
        return ValidationResult(
            system_issues=system_issues,
            clip_results=clip_results,
            total_size_estimate=total_size,
            available_space=available
        )
