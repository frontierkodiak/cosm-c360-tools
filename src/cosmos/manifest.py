from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET


class ClipStatus(Enum):
    """Status of a clip's data availability"""
    COMPLETE = "complete"          # All expected segments present
    PARTIAL = "partial"           # Some segments missing
    MISSING = "missing"           # No segments found
    INVALID = "invalid"           # Metadata inconsistency detected


@dataclass
class Position:
    """
    Represents a position in the COSM directory structure.
    
    Format is typically "NH/MM/SS.sss" where:
    - N: Hour number
    - MM: Minute number
    - SS.sss: Second with fractional component
    """
    hour: int
    minute: int
    second: float

    @classmethod
    def from_string(cls, pos_str: str) -> "Position":
        """Parse a position string like '0H/0M/3.8S/'"""
        parts = pos_str.strip('/').split('/')
        if len(parts) != 3:
            raise ValueError(f"Invalid position string format: {pos_str}")
        
        try:
            hour = int(parts[0].rstrip('H'))
            minute = int(parts[1].rstrip('M'))
            second = float(parts[2].rstrip('S'))
            return cls(hour=hour, minute=minute, second=second)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse position string: {pos_str}") from e

    def to_string(self) -> str:
        """Convert position back to string format"""
        return f"{self.hour}H/{self.minute}M/{self.second}S"
    
    def to_seconds(self) -> float:
        """Convert position to total seconds from start of hour"""
        return self.hour * 3600 + self.minute * 60 + self.second


@dataclass
class ClipInfo:
    """
    Information about a single clip from the manifest.
    
    Clips represent continuous recording sessions, each containing multiple
    video segments that should be processed together.
    """
    name: str                     # Clip identifier (e.g., "CLIP1")
    start_epoch: float           # Start timestamp (Unix epoch)
    end_epoch: float             # End timestamp (Unix epoch)
    start_pos: Position          # Starting directory position
    end_pos: Position            # Ending directory position
    start_idx: int              # Starting frame index
    end_idx: int                # Ending frame index
    start_time: datetime        # Human-readable start time
    status: ClipStatus = ClipStatus.MISSING

    @property
    def duration(self) -> float:
        """Duration of clip in seconds"""
        return self.end_epoch - self.start_epoch

    @property
    def frame_count(self) -> int:
        """Total number of frames in clip"""
        return self.end_idx - self.start_idx


class ManifestParser:
    """
    Parser for COSM C360 camera clip manifests.
    
    The manifest XML contains information about recording sessions ("clips"),
    including their temporal boundaries, frame indices, and positions within
    the directory structure.
    """
    
    def __init__(self, manifest_path: Path):
        """
        Initialize parser with path to manifest XML.
        
        Args:
            manifest_path: Path to the manifest XML file
            
        Raises:
            FileNotFoundError: If manifest file doesn't exist
            xml.etree.ElementTree.ParseError: If XML is malformed
        """
        self.manifest_path = manifest_path
        self._clips: Dict[str, ClipInfo] = {}
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        self._parse_manifest()
    
    def _parse_manifest(self) -> None:
        """
        Parse the manifest XML file and extract clip information.
        
        The manifest contains a series of clip entries with attributes:
        - Name: Clip identifier
        - Epoch: Start time in Unix epoch format
        - Pos: Directory position string
        - InIdx/OutIdx: Frame index boundaries
        - InStr: Human-readable timestamp
        """
        tree = ET.parse(self.manifest_path)
        root = tree.getroot()
        
        for elem in root:
            try:
                name = elem.attrib['Name']
                start_epoch = float(elem.attrib['Epoch'])
                pos = Position.from_string(elem.attrib['Pos'])
                start_idx = int(elem.attrib['InIdx'])
                end_idx = int(elem.attrib['OutIdx'])
                start_time = datetime.strptime(
                    elem.attrib['InStr'],
                    "%H:%M:%S.%f %m/%d/%Y"
                )
                
                # Store clip info
                self._clips[name] = ClipInfo(
                    name=name,
                    start_epoch=start_epoch,
                    end_epoch=None,  # Will be determined from segment data
                    start_pos=pos,
                    end_pos=None,    # Will be determined from segment data
                    start_idx=start_idx,
                    end_idx=end_idx,
                    start_time=start_time
                )
                
            except (KeyError, ValueError) as e:
                # Log warning but continue parsing other clips
                print(f"Warning: Failed to parse clip element: {e}")
                continue
    
    def get_clip(self, name: str) -> Optional[ClipInfo]:
        """Get information for a specific clip by name"""
        return self._clips.get(name)
    
    def get_clips(self) -> List[ClipInfo]:
        """Get list of all clips in temporal order"""
        return sorted(
            self._clips.values(),
            key=lambda x: x.start_epoch
        )
    
    def update_clip_status(self, name: str, status: ClipStatus) -> None:
        """Update the status of a clip after validation"""
        if clip := self._clips.get(name):
            clip.status = status
    
    def find_clip_for_timestamp(self, timestamp: float) -> Optional[ClipInfo]:
        """Find the clip containing a given timestamp"""
        for clip in self._clips.values():
            if clip.start_epoch <= timestamp and (
                clip.end_epoch is None or timestamp <= clip.end_epoch
            ):
                return clip
        return None


def find_manifest(base_dir: Path) -> Optional[Path]:
    """
    Find the COSM manifest XML file in a directory.
    
    Args:
        base_dir: Directory to search for manifest
        
    Returns:
        Path to manifest if exactly one is found, None otherwise
        
    Raises:
        ValueError: If multiple manifest files are found
    """
    manifests = list(base_dir.glob("**/*.xml"))
    
    if not manifests:
        return None
    
    if len(manifests) > 1:
        raise ValueError(
            f"Multiple manifest files found: {', '.join(str(p) for p in manifests)}"
        )
    
    return manifests[0]