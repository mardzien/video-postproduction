#!/usr/bin/env python3
"""
Video Postproduction CLI - Unified command-line interface.

Commands:
    audio    - Mix audio from collision events
    overlay  - Add text overlay to video
    full     - Complete postproduction (audio + overlay)
    
Usage:
    postprod audio --input video.mp4 --sounds-dir sounds/
    postprod overlay --input video.mp4 --text "Level 3"
    postprod full --input video.mp4 --text "Level 3" --sounds-dir sounds/
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

# Add parent to path for imports when running as script
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.parent))

from src.mixer import PostProductionMixer, PostProductionError
from src.overlay import OverlayConfig, OverlayError, process_overlay
from src.templates import TemplateManager, TemplateError, generate_output_filename


def find_events_file(video_path: Path) -> Path:
    """Find matching events JSON file for a video."""
    # Pattern: shorts_video_YYYYMMDD_HHMMSS.mp4 -> shorts_events_YYYYMMDD_HHMMSS.json
    stem = video_path.stem
    ts = stem.replace("shorts_video_", "").replace("_video", "")
    
    # Try different patterns
    candidates = [
        video_path.with_name(f"shorts_events_{ts}.json"),
        video_path.with_name(f"{stem.replace('video', 'events')}.json"),
        video_path.with_suffix(".json"),
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    raise FileNotFoundError(
        f"Events JSON not found for {video_path}. "
        f"Tried: {', '.join(str(c) for c in candidates)}"
    )


def resolve_input(input_path: str) -> list[Path]:
    """Resolve input path or glob pattern to list of files."""
    # Handle glob patterns
    if any(ch in input_path for ch in "*?[]"):
        paths = sorted(glob.glob(input_path))
    else:
        paths = [input_path]
    
    # Convert to Path objects
    result = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            # Try in recordings/ subdirectory
            alt = Path("recordings") / p
            if alt.exists():
                path = alt
        if path.exists():
            result.append(path)
    
    if not result:
        raise FileNotFoundError(f"No files found: {input_path}")
    
    return result


def default_output_path(video_path: Path, suffix: str = "_final") -> Path:
    """Generate default output path for a video."""
    output_dir = Path("final_recordings")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    name = video_path.stem
    # Transform names like shorts_video_XXX to shorts_final_XXX
    if "_video_" in name:
        name = name.replace("_video_", f"{suffix}_")
    else:
        name = f"{name}{suffix}"
    
    return output_dir / f"{name}.mp4"


# ============================================================================
# AUDIO COMMAND
# ============================================================================

def cmd_audio(args: argparse.Namespace) -> int:
    """Handle 'audio' command - mix audio from collision events."""
    try:
        inputs = resolve_input(args.input)
        
        # Initialize mixer
        mixer = PostProductionMixer(
            sounds_folder=args.sounds_dir,
            volume=args.volume,
        )
        
        for video_path in inputs:
            print(f"\n📽️ Processing: {video_path}")
            
            # Find events file
            try:
                events_path = find_events_file(video_path)
            except FileNotFoundError as e:
                print(f"⚠️ {e}")
                continue
            
            # Determine output path
            if args.output and len(inputs) == 1:
                output_path = Path(args.output)
            else:
                output_path = default_output_path(video_path)
            
            # Process
            mixer.process_recording(
                video_file=video_path,
                events_file=events_path,
                output_file=output_path,
                cleanup_temp_files=args.cleanup,
            )
        
        mixer.cleanup()
        return 0
        
    except PostProductionError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# OVERLAY COMMAND
# ============================================================================

def cmd_overlay(args: argparse.Namespace) -> int:
    """Handle 'overlay' command - add text overlay."""
    try:
        inputs = resolve_input(args.input)
        
        config = OverlayConfig(
            text=args.text,
            font=args.font,
            font_file=args.font_file,
            font_size=args.font_size,
            color=args.color,
            bar_color=args.bar_color,
            bar_opacity=args.bar_opacity,
            margin_top=args.margin_top,
            bar_height=args.bar_height,
            padding_x=args.padding_x,
            align=args.align,
            shadow=args.shadow,
            render_engine=args.render_engine,
        )
        
        for video_path in inputs:
            print(f"\n📽️ Processing: {video_path}")
            
            # Determine output path
            if args.output and len(inputs) == 1:
                output_path = Path(args.output)
            else:
                output_path = default_output_path(video_path, "_caption")
            
            process_overlay(video_path, output_path, config)
        
        return 0
        
    except OverlayError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# SHORTS COMMAND
# ============================================================================

def cmd_shorts(args: argparse.Namespace) -> int:
    """Handle 'shorts' command - template-based shorts production."""
    try:
        # Initialize template manager
        template_mgr = TemplateManager()
        
        # List templates if requested
        if args.list_templates:
            templates = template_mgr.list_templates()
            print("\n📋 Available templates:\n")
            if templates:
                for name, desc in templates:
                    print(f"  • {name:25s} - {desc}")
            else:
                print("  (no templates found)")
            print("\n💡 Use: postprod shorts --template <name> --input video.mp4\n")
            return 0
        
        # Load template
        if not args.template:
            print("❌ ERROR: --template required (or use --list-templates)", file=sys.stderr)
            return 1
        
        try:
            template = template_mgr.load_template(args.template)
        except TemplateError as e:
            print(f"❌ {e}", file=sys.stderr)
            return 1
        
        print(f"📋 Using template: {template.name}")
        print(f"   Description: {template.description}")
        
        # Apply overrides
        overrides = {}
        if args.text:
            overrides.setdefault("overlay", {})["text"] = args.text
        if args.sounds_dir:
            overrides.setdefault("audio", {})["sounds_dir"] = args.sounds_dir
        if args.volume is not None:
            overrides.setdefault("audio", {})["volume"] = args.volume
        
        if overrides:
            template = template.merge_overrides(overrides)
        
        # Resolve input files
        inputs = resolve_input(args.input)
        
        # Initialize mixer - MIDI mode only
        mixer = PostProductionMixer(
            midi_file=template.audio.midi_file,
            midi_instrument=template.audio.instrument,
            midi_track=template.audio.midi_track,
            midi_channel=template.audio.midi_channel,
            volume=template.audio.volume,
        )
        
        # Create overlay config from template
        overlay_config = OverlayConfig(
            text=template.overlay.text,
            font=template.overlay.font,
            font_file=template.overlay.font_file,
            font_size=template.overlay.font_size,
            color=template.overlay.color,
            margin_top=template.overlay.margin_top,
            padding_x=template.overlay.padding_x,
            align=template.overlay.align,
            shadow=template.overlay.shadow,
            render_engine=template.overlay.render_engine,
        )
        
        for video_path in inputs:
            print(f"\n📽️ Processing: {video_path}")
            
            # Find events file
            try:
                events_path = find_events_file(video_path)
            except FileNotFoundError as e:
                print(f"⚠️ {e}")
                continue
            
            # Determine output path
            if args.output and len(inputs) == 1:
                final_output = Path(args.output)
            else:
                final_output = generate_output_filename(
                    template,
                    video_path,
                    auto_number=args.auto_number,
                )
            
            # Step 1: Mix audio -> temporary file
            temp_output = default_output_path(video_path, "_temp")
            mixed_path = mixer.process_recording(
                video_file=video_path,
                events_file=events_path,
                output_file=temp_output,
                cleanup_temp_files=False,
            )
            
            # Step 2: Add overlay
            process_overlay(mixed_path, final_output, overlay_config)
            
            # Cleanup intermediate file
            try:
                Path(mixed_path).unlink()
            except Exception:
                pass
            
            # Cleanup source files if requested
            if args.cleanup:
                for f in [video_path, events_path]:
                    try:
                        f.unlink()
                        print(f"   🧹 Deleted: {f.name}")
                    except Exception:
                        pass
        
        mixer.cleanup()
        print(f"\n✅ Shorts production complete!")
        return 0
        
    except (PostProductionError, OverlayError, TemplateError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# FULL COMMAND
# ============================================================================

def cmd_full(args: argparse.Namespace) -> int:
    """Handle 'full' command - complete postproduction (audio + overlay)."""
    try:
        inputs = resolve_input(args.input)
        
        # Initialize mixer
        mixer = PostProductionMixer(
            sounds_folder=args.sounds_dir,
            volume=args.volume,
        )
        
        overlay_config = OverlayConfig(
            text=args.text,
            font=args.font,
            font_file=args.font_file,
            font_size=args.font_size,
            color=args.color,
            bar_color=args.bar_color,
            bar_opacity=args.bar_opacity,
            margin_top=args.margin_top,
            bar_height=args.bar_height,
            padding_x=args.padding_x,
            align=args.align,
            shadow=args.shadow,
            render_engine=args.render_engine,
        )
        
        for video_path in inputs:
            print(f"\n📽️ Processing: {video_path}")
            
            # Find events file
            try:
                events_path = find_events_file(video_path)
            except FileNotFoundError as e:
                print(f"⚠️ {e}")
                continue
            
            # Step 1: Mix audio -> temporary file
            temp_output = default_output_path(video_path, "_temp")
            mixed_path = mixer.process_recording(
                video_file=video_path,
                events_file=events_path,
                output_file=temp_output,
                cleanup_temp_files=False,
            )
            
            # Step 2: Add overlay
            if args.output and len(inputs) == 1:
                final_output = Path(args.output)
            else:
                final_output = default_output_path(video_path, "_caption")
            
            process_overlay(mixed_path, final_output, overlay_config)
            
            # Cleanup intermediate file
            try:
                Path(mixed_path).unlink()
            except Exception:
                pass
            
            # Cleanup source files if requested
            if args.cleanup:
                for f in [video_path, events_path]:
                    try:
                        f.unlink()
                        print(f"   🧹 Deleted: {f.name}")
                    except Exception:
                        pass
        
        mixer.cleanup()
        return 0
        
    except (PostProductionError, OverlayError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# ARGUMENT PARSER
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="postprod",
        description="Video Postproduction - Audio mixing and text overlay",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # ========== AUDIO COMMAND ==========
    audio_parser = subparsers.add_parser(
        "audio",
        help="Mix audio from collision events",
        description="Add collision sounds to silent video based on events JSON",
    )
    audio_parser.add_argument(
        "--input", "-i", required=True,
        help="Input video file or glob pattern",
    )
    audio_parser.add_argument(
        "--output", "-o",
        help="Output file (auto-generated if omitted)",
    )
    audio_parser.add_argument(
        "--sounds-dir", "-s",
        help="Directory with WAV collision sounds",
    )
    audio_parser.add_argument(
        "--volume", type=float, default=0.7,
        help="Volume multiplier (default: 0.7)",
    )
    audio_parser.add_argument(
        "--cleanup", action="store_true",
        help="Delete source files after processing",
    )
    audio_parser.set_defaults(func=cmd_audio)
    
    # ========== OVERLAY COMMAND ==========
    overlay_parser = subparsers.add_parser(
        "overlay",
        help="Add text overlay to video",
        description="Add text caption/banner to video",
    )
    overlay_parser.add_argument(
        "--input", "-i", required=True,
        help="Input video file or glob pattern",
    )
    overlay_parser.add_argument(
        "--text", "-t", required=True,
        help="Text to overlay (supports emoji and \\n for newlines)",
    )
    overlay_parser.add_argument(
        "--output", "-o",
        help="Output file (auto-generated if omitted)",
    )
    # Styling options
    overlay_parser.add_argument("--font", help="Font family name")
    overlay_parser.add_argument("--font-file", help="Path to TTF/OTF font")
    overlay_parser.add_argument("--font-size", type=int, default=60)
    overlay_parser.add_argument("--color", default="white")
    overlay_parser.add_argument("--bar-color", default="black")
    overlay_parser.add_argument("--bar-opacity", type=float, default=0.0)
    overlay_parser.add_argument("--margin-top", type=int, default=100)
    overlay_parser.add_argument("--bar-height", type=int, default=120)
    overlay_parser.add_argument("--padding-x", type=int, default=120)
    overlay_parser.add_argument(
        "--align", choices=["left", "center", "right"], default="center"
    )
    overlay_parser.add_argument(
        "--no-shadow", dest="shadow", action="store_false"
    )
    overlay_parser.add_argument(
        "--render-engine",
        choices=["pango_png", "pillow_png", "ffmpeg_text"],
        default="pango_png",
    )
    overlay_parser.set_defaults(func=cmd_overlay, shadow=True)
    
    # ========== SHORTS COMMAND ==========
    shorts_parser = subparsers.add_parser(
        "shorts",
        help="Template-based YouTube Shorts production",
        description="Complete postproduction using predefined templates",
    )
    shorts_parser.add_argument(
        "--input", "-i",
        help="Input video file or glob pattern",
    )
    shorts_parser.add_argument(
        "--template", "-t",
        help="Template name (use --list-templates to see available)",
    )
    shorts_parser.add_argument(
        "--list-templates", "-l", action="store_true",
        help="List available templates and exit",
    )
    shorts_parser.add_argument(
        "--output", "-o",
        help="Output file (auto-generated if omitted)",
    )
    shorts_parser.add_argument(
        "--auto-number", "-n", action="store_true",
        help="Auto-number output files (shorts_001, shorts_002, etc.)",
    )
    # Override options
    shorts_parser.add_argument(
        "--text",
        help="Override template text",
    )
    shorts_parser.add_argument(
        "--sounds-dir", "-s",
        help="Override template sounds directory",
    )
    shorts_parser.add_argument(
        "--volume", type=float,
        help="Override template volume",
    )
    shorts_parser.add_argument(
        "--cleanup", action="store_true",
        help="Delete source files after processing",
    )
    shorts_parser.set_defaults(func=cmd_shorts)
    
    # ========== FULL COMMAND ==========
    full_parser = subparsers.add_parser(
        "full",
        help="Complete postproduction (audio + overlay)",
        description="Mix audio and add text overlay in one step",
    )
    full_parser.add_argument(
        "--input", "-i", required=True,
        help="Input video file or glob pattern",
    )
    full_parser.add_argument(
        "--text", "-t", required=True,
        help="Text to overlay",
    )
    full_parser.add_argument(
        "--output", "-o",
        help="Output file (auto-generated if omitted)",
    )
    full_parser.add_argument(
        "--sounds-dir", "-s",
        help="Directory with WAV collision sounds",
    )
    full_parser.add_argument(
        "--volume", type=float, default=0.7,
        help="Volume multiplier (default: 0.7)",
    )
    full_parser.add_argument(
        "--cleanup", action="store_true",
        help="Delete source files after processing",
    )
    # Styling options (same as overlay)
    full_parser.add_argument("--font", help="Font family name")
    full_parser.add_argument("--font-file", help="Path to TTF/OTF font")
    full_parser.add_argument("--font-size", type=int, default=60)
    full_parser.add_argument("--color", default="white")
    full_parser.add_argument("--bar-color", default="black")
    full_parser.add_argument("--bar-opacity", type=float, default=0.0)
    full_parser.add_argument("--margin-top", type=int, default=100)
    full_parser.add_argument("--bar-height", type=int, default=120)
    full_parser.add_argument("--padding-x", type=int, default=120)
    full_parser.add_argument(
        "--align", choices=["left", "center", "right"], default="center"
    )
    full_parser.add_argument(
        "--no-shadow", dest="shadow", action="store_false"
    )
    full_parser.add_argument(
        "--render-engine",
        choices=["pango_png", "pillow_png", "ffmpeg_text"],
        default="pango_png",
    )
    full_parser.set_defaults(func=cmd_full, shadow=True)
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    print("🎬 Video Postproduction")
    print(f"   Command: {args.command}")
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

