"""
Template management for YouTube Shorts production.

Provides predefined configurations (audio, text, styling) for rapid
video postproduction workflow.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


class TemplateError(Exception):
    """Exception for template-related errors."""


@dataclass
class AudioConfig:
    """Audio mixing configuration - MIDI only."""
    midi_file: str
    instrument: int
    midi_track: int | None = None
    midi_channel: int | None = None
    volume: float = 1.0
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.midi_file:
            raise ValueError("midi_file is required")
        if self.instrument is None:
            raise ValueError("instrument is required")


@dataclass
class OverlayTemplateConfig:
    """Text overlay configuration for templates."""
    text: str
    font_size: int = 75
    color: str = "white"
    margin_top: int = 120
    shadow: bool = True
    render_engine: str = "pango_png"
    align: str = "center"
    font: str | None = None
    font_file: str | None = None
    padding_x: int = 120


@dataclass
class OutputConfig:
    """Output file configuration."""
    prefix: str = "shorts"
    format: str = "mp4"
    quality: str = "high"  # high=CRF18, medium=CRF23, low=CRF28


@dataclass
class ShortsTemplate:
    """Complete template for YouTube Shorts production."""
    name: str
    description: str
    audio: AudioConfig
    overlay: OverlayTemplateConfig
    output: OutputConfig = field(default_factory=OutputConfig)
    video_format: str = "shorts"  # shorts (9:16) or landscape (16:9)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShortsTemplate:
        """Create template from dictionary."""
        # Handle audio config with defaults for backward compatibility
        audio_data = data.get("audio", {})
        if not audio_data:
            raise ValueError("audio configuration is required")
        
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            audio=AudioConfig(**audio_data),
            overlay=OverlayTemplateConfig(**data.get("overlay", {})),
            output=OutputConfig(**data.get("output", {})),
            video_format=data.get("video_format", "shorts"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "video_format": self.video_format,
            "audio": asdict(self.audio),
            "overlay": asdict(self.overlay),
            "output": asdict(self.output),
        }

    def merge_overrides(self, overrides: dict[str, Any]) -> ShortsTemplate:
        """Create new template with overridden values."""
        data = self.to_dict()
        
        # Merge audio overrides
        if "audio" in overrides:
            data["audio"].update(overrides["audio"])
        
        # Merge overlay overrides
        if "overlay" in overrides:
            data["overlay"].update(overrides["overlay"])
        
        # Merge output overrides
        if "output" in overrides:
            data["output"].update(overrides["output"])
        
        # Top-level overrides
        for key in ["name", "description", "video_format"]:
            if key in overrides:
                data[key] = overrides[key]
        
        return ShortsTemplate.from_dict(data)


class TemplateManager:
    """Manages loading and saving of shorts templates."""

    def __init__(self, templates_dir: str | Path = "templates"):
        self.templates_dir = Path(templates_dir)

    def load_template(self, name: str) -> ShortsTemplate:
        """
        Load template by name from templates/ directory.
        
        Args:
            name: Template name (without .yaml extension)
            
        Returns:
            Loaded template
            
        Raises:
            TemplateError: If template not found or invalid
        """
        template_path = self.templates_dir / f"{name}.yaml"
        
        if not template_path.exists():
            raise TemplateError(
                f"Template '{name}' not found: {template_path}"
            )
        
        return self._load_from_file(template_path)

    def _load_from_file(self, path: Path) -> ShortsTemplate:
        """Load template from YAML file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data:
                raise TemplateError(f"Empty template file: {path}")
            
            return ShortsTemplate.from_dict(data)
            
        except yaml.YAMLError as e:
            raise TemplateError(f"Invalid YAML in {path}: {e}") from e
        except Exception as e:
            raise TemplateError(f"Failed to load template {path}: {e}") from e

    def save_template(self, template: ShortsTemplate, name: str | None = None) -> Path:
        """
        Save template to YAML file.
        
        Args:
            template: Template to save
            name: Filename (without .yaml), defaults to template.name
            
        Returns:
            Path to saved file
        """
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        filename = (name or template.name) + ".yaml"
        path = self.templates_dir / filename
        
        data = template.to_dict()
        
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        return path

    def list_templates(self) -> list[tuple[str, str]]:
        """
        List all available templates.
        
        Returns:
            List of (name, description) tuples
        """
        templates: list[tuple[str, str]] = []
        
        # Scan templates directory
        if self.templates_dir.exists():
            for path in sorted(self.templates_dir.glob("*.yaml")):
                try:
                    template = self._load_from_file(path)
                    templates.append((template.name, template.description))
                except Exception:
                    # Skip invalid templates
                    pass
        
        return templates

    def save_example_template(self, template: ShortsTemplate, name: str | None = None) -> Path:
        """Save template to examples directory."""
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        filename = (name or template.name) + ".yaml"
        path = self.examples_dir / filename
        
        data = template.to_dict()
        
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        return path

    def create_example_templates(self) -> None:
        """Create default example templates."""
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        # Christmas/Holiday template
        christmas = ShortsTemplate(
            name="christmas",
            description="Christmas-themed short with jingle bells",
            video_format="shorts",
            audio=AudioConfig(
                sounds_dir="mido/melodies/jingle_bells",
                volume=0.75,
            ),
            overlay=OverlayTemplateConfig(
                text="🎄🔔 Will the bass escape? 🦌🎅",
                font_size=75,
                color="white",
                margin_top=120,
                bar_opacity=0.0,  # No background bar
                bar_color="#1a472a",  # Dark green
                shadow=True,
                render_engine="pango_png",
                align="center",
            ),
            output=OutputConfig(
                prefix="shorts_christmas",
                format="mp4",
                quality="high",
            ),
        )
        
        # Mario challenge template
        mario = ShortsTemplate(
            name="mario_challenge",
            description="Mario-themed challenge with classic sounds",
            video_format="shorts",
            audio=AudioConfig(
                sounds_dir="mido/melodies/mario",
                volume=0.7,
            ),
            overlay=OverlayTemplateConfig(
                text="🍄 Mario Challenge 🎮\nCan you beat the high score?",
                font_size=70,
                color="white",
                margin_top=100,
                bar_opacity=0.3,
                bar_color="#e60000",  # Red
                shadow=True,
                render_engine="pango_png",
                align="center",
            ),
            output=OutputConfig(
                prefix="shorts_mario",
                format="mp4",
                quality="high",
            ),
        )
        
        # Epic Imperial March template
        imperial = ShortsTemplate(
            name="epic_imperial",
            description="Epic theme with Imperial March",
            video_format="shorts",
            audio=AudioConfig(
                sounds_dir="mido/melodies/imperial_march",
                volume=0.8,
            ),
            overlay=OverlayTemplateConfig(
                text="⚔️ EPIC MODE ⚔️",
                font_size=80,
                color="white",
                margin_top=140,
                bar_opacity=0.4,
                bar_color="#1a1a1a",  # Dark gray
                shadow=True,
                render_engine="pango_png",
                align="center",
            ),
            output=OutputConfig(
                prefix="shorts_epic",
                format="mp4",
                quality="high",
            ),
        )
        
        # Minimal/Basic template
        minimal = ShortsTemplate(
            name="basic_minimal",
            description="Minimal clean template with default sounds",
            video_format="shorts",
            audio=AudioConfig(
                sounds_dir="sounds",
                volume=0.7,
            ),
            overlay=OverlayTemplateConfig(
                text="Watch This! 👀",
                font_size=65,
                color="white",
                margin_top=100,
                bar_opacity=0.0,  # No background bar
                bar_color="black",
                shadow=True,
                render_engine="pango_png",
                align="center",
            ),
            output=OutputConfig(
                prefix="shorts",
                format="mp4",
                quality="high",
            ),
        )
        
        # Save all examples
        for template in [christmas, mario, imperial, minimal]:
            self.save_example_template(template, template.name)
            print(f"✅ Created template: {template.name}")


def generate_output_filename(
    template: ShortsTemplate,
    input_path: Path,
    auto_number: bool = False,
    output_dir: Path = Path("final_recordings"),
) -> Path:
    """
    Generate output filename based on template and input.
    
    Args:
        template: Template configuration
        input_path: Input video path
        auto_number: Auto-number output files
        output_dir: Output directory
        
    Returns:
        Output file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prefix = template.output.prefix
    ext = template.output.format
    
    if auto_number:
        # Find next available number
        existing = list(output_dir.glob(f"{prefix}_*.{ext}"))
        if existing:
            numbers = []
            for p in existing:
                stem = p.stem  # e.g. "shorts_christmas_001"
                parts = stem.split("_")
                if parts and parts[-1].isdigit():
                    numbers.append(int(parts[-1]))
            next_num = max(numbers, default=0) + 1
        else:
            next_num = 1
        
        filename = f"{prefix}_{next_num:03d}.{ext}"
    else:
        # Use input filename as base
        base = input_path.stem
        filename = f"{prefix}_{base}.{ext}"
    
    return output_dir / filename

