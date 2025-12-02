"""
Simplified collision event data structures for video postproduction.

Supports both:
- Full format (from Balls game) - extra fields are ignored
- Simplified format (native) - only essential fields
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CollisionEvent:
    """
    Simplified collision event with only fields used in postproduction.
    
    Full format from Balls game includes additional unused fields:
    - ball_position_x, ball_position_y
    - ball_velocity_x, ball_velocity_y  
    - ball_speed, distance_from_center
    - collision_type (not needed for audio)
    
    These are ignored when loading for backwards compatibility.
    """

    frame_number: int  # Frame number for frame-based sync
    timestamp: float  # Timestamp in seconds (frame-based)
    impact_intensity: float  # Intensity 0.0-1.0 for volume control

    def to_dict(self) -> dict:
        """Convert event to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CollisionEvent:
        """
        Create CollisionEvent from dictionary.
        
        Supports both full format (ignores extra fields) and simplified format.
        """
        return cls(
            frame_number=data["frame_number"],
            timestamp=data["timestamp"],
            impact_intensity=data["impact_intensity"],
        )


@dataclass
class RecordingInfo:
    """Simplified recording metadata - only used fields."""

    total_frames: int  # For frame-based synchronization
    duration: float  # For comparison with actual video duration

    @classmethod
    def from_dict(cls, data: dict) -> RecordingInfo:
        """Create from dictionary, with defaults for missing fields."""
        return cls(
            total_frames=data.get("total_frames", 0),
            duration=data.get("duration", 0.0),
        )


def load_events_from_file(
    filepath: Path | str,
) -> tuple[list[CollisionEvent], RecordingInfo]:
    """
    Load collision events from JSON file.
    
    Supports both full format (from Balls) and simplified format.
    Extra fields in full format are ignored.
    
    Args:
        filepath: Path to JSON events file
        
    Returns:
        Tuple of (list of CollisionEvent, RecordingInfo)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    filepath = Path(filepath)

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    # Parse recording info (with backwards compatibility)
    recording_info = RecordingInfo.from_dict(data.get("recording_info", {}))

    # Parse collision events
    events = [
        CollisionEvent.from_dict(event_data)
        for event_data in data.get("collision_events", [])
    ]

    return events, recording_info


def save_events_to_file(
    filepath: Path | str,
    events: list[CollisionEvent],
    recording_info: RecordingInfo,
) -> None:
    """
    Save collision events to JSON file in simplified format.
    
    Args:
        filepath: Path to output JSON file
        events: List of CollisionEvent objects
        recording_info: Recording metadata
    """
    filepath = Path(filepath)

    data = {
        "recording_info": {
            "total_frames": recording_info.total_frames,
            "duration": recording_info.duration,
        },
        "collision_events": [event.to_dict() for event in events],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

