from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import json
import shutil
import subprocess
from datetime import datetime

from .manifest import ClipInfo, ClipStatus, Position, ManifestParser

class ValidationLevel(Enum):
    """Severity level for validation issues"""
    ERROR = "error"          # Fatal issue, cannot proceed
    WARNING = "warning"      # Potential issue, can proceed with caution
    INFO = "info"           # Informational note

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
        return len(self.ts_files) == self.frame_count

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
                        segment_dir: Path) -> Optional[SegmentInfo]:
        """
        Validate a segment directory and its meta.json
        
        Args:
            segment_dir: Path to segment directory
            
        Returns:
            SegmentInfo if valid, None if invalid
        """
        meta_path = segment_dir / "meta.json"
        if not meta_path.is_file():
            return None
            
        try:
            with open(meta_path) as f:
                meta = json.load(f)
                
            if "Time" not in meta or "x0" not in meta["Time"] or "xi-x0" not in meta["Time"]:
                return None
                
            start_time = meta["Time"]["x0"]
            increments = meta["Time"]["xi-x0"]
            
            # Get all .ts files in directory
            ts_files = sorted(segment_dir.glob("*.ts"))
            
            # Create timestamps for each frame
            timestamps = [start_time + inc for inc in increments]
            
            return SegmentInfo(
                directory=segment_dir,
                start_time=start_time,
                frame_timestamps=timestamps,
                ts_files=ts_files
            )
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def validate_clip(self, clip: ClipInfo) -> ClipValidationResult:
        """
        Validate all segments for a clip
        
        Args:
            clip: ClipInfo object to validate
            
        Returns:
            ClipValidationResult with validation details
        """
        issues = []
        segments = []
        missing_positions = []
        
        # Calculate expected segment positions
        start_sec = int(clip.start_pos.second)
        end_sec = int(clip.end_pos.second) if clip.end_pos else start_sec + 60
        
        for second in range(start_sec, end_sec + 1):
            pos = Position(
                hour=clip.start_pos.hour,
                minute=clip.start_pos.minute,
                second=second
            )
            
            # Check if segment exists
            segment_dir = self.input_dir / pos.path_fragment()
            if not segment_dir.is_dir():
                missing_positions.append(pos)
                continue
                
            # Validate segment
            if segment_info := self.validate_segment(segment_dir):
                segments.append(segment_info)
            else:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Invalid segment at {pos.path_fragment()}",
                    context="Missing or corrupt meta.json"
                ))
        
        # Estimate output size (very rough approximation)
        # Assume ~100MB per second of full-res output
        estimated_size = len(segments) * 100 * 1024 * 1024
        
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