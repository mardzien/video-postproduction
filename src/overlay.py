"""
Text overlay module for video postproduction.

Adds text captions/banners to videos with:
- Pango-based rendering (best for emoji support)
- PIL fallback for systems without pango
- FFmpeg drawtext as alternative engine
- Hardware acceleration (VAAPI) when available
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class OverlayError(Exception):
    """Exception for overlay-related errors."""


@dataclass
class OverlayConfig:
    """Configuration for text overlay."""

    text: str
    font: str | None = None
    font_file: str | None = None
    font_size: int = 60
    color: str = "white"
    margin_top: int = 100
    padding_x: int = 120
    align: str = "center"  # left, center, right
    shadow: bool = True
    render_engine: str = "pango_png"  # pango_png, pillow_png, ffmpeg_text


def _run_cmd(command: list[str]) -> None:
    """Run command and raise on failure."""
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        raise OverlayError(
            f"Command failed: {' '.join(command)}\nStderr: {process.stderr}"
        )


def _ffprobe_size(path: str) -> tuple[int, int]:
    """Get video dimensions using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        path,
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    if not out:
        raise OverlayError(f"Unable to probe video size: {path}")
    parts = out.split(",")
    return int(parts[0]), int(parts[1])


def _has_vaapi() -> bool:
    """Check if VAAPI hardware acceleration is available."""
    return os.path.exists("/dev/dri/renderD128") or os.path.exists("/dev/dri/card0")


def _wrap_text_for_width(text: str, max_width_px: int, font_size: int) -> str:
    """Simple word-wrapping based on estimated glyph width."""
    if max_width_px <= 0:
        return text

    # Handle explicit newlines
    explicit_lines = text.replace('\\n', '\n').split("\n")
    result_lines: list[str] = []

    avg_char_px = max(1.0, font_size * 0.55)

    for line in explicit_lines:
        words = line.split()
        if not words:
            result_lines.append("")
            continue

        current: list[str] = []
        current_px = 0.0

        for word in words:
            word_px = len(word) * avg_char_px
            sep_px = avg_char_px if current else 0.0

            if current_px + sep_px + word_px > max_width_px and current:
                result_lines.append(" ".join(current))
                current = [word]
                current_px = word_px
            else:
                if current:
                    current_px += sep_px
                current.append(word)
                current_px += word_px

        if current:
            result_lines.append(" ".join(current))

    return "\n".join(result_lines)


def _render_text_png_pango(
    text: str,
    width: int,
    padding_x: int,
    font: str | None,
    font_size: int,
    color: str = "white",
) -> str:
    """Render text to PNG using pango-view (best for emoji)."""
    if not shutil.which("pango-view"):
        raise OverlayError(
            "pango-view not found. Install 'pango' package or use pillow_png engine."
        )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp_path = tmp.name
    tmp.close()

    font_desc = f"{font} {font_size}" if font else f"Sans {font_size}"
    effective_width = max(100, width - max(0, padding_x) * 2)

    # Handle escaped newlines
    text_with_newlines = text.replace('\\n', '\n')
    wrapped_text = _wrap_text_for_width(text_with_newlines, effective_width, font_size)

    # Write text to temp file for pango-view
    text_tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", mode='w', encoding='utf-8'
    )
    text_tmp.write(wrapped_text)
    text_tmp.close()

    try:
        cmd = [
            "pango-view",
            "--font", font_desc,
            "--width", str(effective_width),
            "--align", "center",
            "--wrap", "word",
            "--ellipsize", "end",
            "--foreground", color,
            "--background", "transparent",
            "--no-display",
            "--output", tmp_path,
            text_tmp.name,
        ]
        _run_cmd(cmd)
    finally:
        try:
            os.remove(text_tmp.name)
        except Exception:
            pass

    return tmp_path


def _render_text_png_pillow(
    text: str,
    width: int,
    bar_height: int,
    color: str,
    font_size: int,
    align: str,
    padding_x: int,
    font_file: str | None,
) -> str:
    """Render text to PNG using Pillow."""
    # Load font
    if font_file:
        try:
            font_obj = ImageFont.truetype(font_file, font_size)
        except Exception as exc:
            raise OverlayError(f"Failed to load font '{font_file}': {exc}") from None
    else:
        # Try common system fonts
        font_paths = [
            "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        ]
        font_obj = None
        for font_path in font_paths:
            try:
                font_obj = ImageFont.truetype(font_path, font_size)
                break
            except Exception:
                continue

        if font_obj is None:
            raise OverlayError(
                "Could not load any system font. Install dejavu-sans-fonts or use --font-file"
            )

    # Handle newlines
    text = text.replace('\\n', '\n')

    # Measure text
    temp_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    text_bbox = temp_draw.textbbox((0, 0), text, font=font_obj)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    img_height = max(bar_height, text_h + 40)

    # Create image
    img = Image.new("RGBA", (width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate position
    if align == "left":
        x = padding_x
    elif align == "right":
        x = max(0, width - text_w - padding_x)
    else:
        x = max(0, (width - text_w) // 2)
    y = 20

    # Shadow + text
    draw.text((x + 2, y + 2), text, font=font_obj, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font_obj, fill=(255, 255, 255, 255))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    tmp.close()
    return tmp.name


def _escape_drawtext(text: str) -> str:
    """Escape text for FFmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace(":", "\\:")
    text = text.replace("%", "\\%")
    return text


def _build_ffmpeg_overlay_cmd(
    src: str,
    dst: str,
    overlay_png: str,
    overlay_y: int,
    use_vaapi: bool,
) -> list[str]:
    """Build FFmpeg command for PNG overlay."""
    filters = f"overlay=x=(main_w-overlay_w)/2:y={overlay_y}:shortest=1"

    base = ["ffmpeg", "-y", "-i", src, "-loop", "1", "-i", overlay_png]

    if use_vaapi:
        filters_hw = f"{filters},format=nv12,hwupload"
        base += [
            "-vaapi_device", "/dev/dri/renderD128",
            "-filter_complex", filters_hw,
            "-shortest",
            "-c:v", "h264_vaapi",
            "-qp", "18",
            "-c:a", "copy",
            dst,
        ]
    else:
        base += [
            "-filter_complex", filters,
            "-shortest",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            dst,
        ]

    return base


def _build_ffmpeg_drawtext_cmd(
    src: str,
    dst: str,
    config: OverlayConfig,
    use_vaapi: bool,
) -> list[str]:
    """Build FFmpeg command for drawtext filter."""
    # Positioning
    if config.align == "left":
        x_expr = f"{config.padding_x}"
    elif config.align == "right":
        x_expr = f"w-tw-{config.padding_x}"
    else:
        x_expr = "(w-tw)/2"

    y_expr = f"{config.margin_top}"

    shadow_args = ":shadowcolor=black@0.8:shadowx=2:shadowy=2" if config.shadow else ""

    text_escaped = _escape_drawtext(config.text)
    font_args = ""
    if config.font_file:
        font_args = f":fontfile='{config.font_file}'"
    elif config.font:
        font_args = f":font='{config.font}'"

    drawtext = f"drawtext=text='{text_escaped}'{font_args}:fontcolor={config.color}:fontsize={config.font_size}:x={x_expr}:y={y_expr}{shadow_args}:borderw=0"
    filters = drawtext

    base = ["ffmpeg", "-y", "-i", src]

    if use_vaapi:
        filters_hw = f"{filters},format=nv12,hwupload"
        base += [
            "-vaapi_device", "/dev/dri/renderD128",
            "-filter_complex", filters_hw,
            "-c:v", "h264_vaapi",
            "-qp", "18",
            "-c:a", "copy",
            dst,
        ]
    else:
        base += [
            "-filter_complex", filters,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            dst,
        ]

    return base


def process_overlay(
    input_video: str | Path,
    output_video: str | Path,
    config: OverlayConfig,
) -> str:
    """
    Add text overlay to video.
    
    Args:
        input_video: Source video file
        output_video: Output video file
        config: Overlay configuration
        
    Returns:
        Path to output video
    """
    input_video = Path(input_video)
    output_video = Path(output_video)

    if not input_video.exists():
        raise OverlayError(f"Input video not found: {input_video}")

    # Ensure output directory exists
    output_video.parent.mkdir(parents=True, exist_ok=True)

    use_vaapi = _has_vaapi()
    print(f"🎬 Adding text overlay: {input_video.name}")
    print(f"   Engine: {config.render_engine}")
    print(f"   HW accel: {'VAAPI' if use_vaapi else 'CPU'}")

    png_path: str | None = None

    try:
        if config.render_engine == "ffmpeg_text":
            cmd = _build_ffmpeg_drawtext_cmd(
                str(input_video),
                str(output_video),
                config,
                use_vaapi,
            )

        elif config.render_engine == "pillow_png":
            width, _ = _ffprobe_size(str(input_video))
            png_path = _render_text_png_pillow(
                text=config.text,
                width=width,
                bar_height=config.bar_height,
                color=config.color,
                font_size=config.font_size,
                align=config.align,
                padding_x=config.padding_x,
                font_file=config.font_file,
            )
            cmd = _build_ffmpeg_overlay_cmd(
                str(input_video),
                str(output_video),
                png_path,
                config.margin_top,
                use_vaapi,
            )

        else:  # pango_png (default)
            width, _ = _ffprobe_size(str(input_video))
            png_path = _render_text_png_pango(
                text=config.text,
                width=width,
                padding_x=config.padding_x,
                font=config.font,
                font_size=config.font_size,
            )
            cmd = _build_ffmpeg_overlay_cmd(
                str(input_video),
                str(output_video),
                png_path,
                config.margin_top,
                use_vaapi,
            )

        print(f"🔧 FFmpeg: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OverlayError(f"FFmpeg failed: {result.stderr}")

        print(f"✅ Overlay complete: {output_video}")
        return str(output_video)

    finally:
        if png_path:
            try:
                os.remove(png_path)
            except Exception:
                pass

