# Video Postproduction

Standalone toolkit for video postproduction with audio mixing and text overlay.

## Features

- **Audio Mixing** - Add collision sounds to silent videos based on event metadata
- **Text Overlay** - Add captions/banners with emoji support
- **Frame-based Sync** - Precise audio synchronization using frame numbers
- **Hardware Acceleration** - VAAPI support for fast encoding on AMD/Intel GPUs
- **Melody Generator** - Bundled `mido` module for generating custom sound sets

## Quick Start

```bash
# Setup
make install

# Mix audio from collision events
make audio INPUT=video.mp4

# Add text overlay
make overlay INPUT=video.mp4 TEXT="Level 3 🎮"

# Full postproduction (audio + overlay)
make postprocess INPUT=video.mp4 TEXT="Level 3 🎮"
```

## Installation

### Requirements

- Python 3.11+
- FFmpeg (with ffprobe)
- pango (optional, for best emoji support)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/video-postproduction.git
cd video-postproduction

# Create virtual environment and install dependencies
make install
```

## Usage

### CLI Commands

The project provides a unified CLI with three main commands:

#### Audio Mixing

Mix collision sounds into silent video based on events JSON:

```bash
# Basic usage
postprod audio --input video.mp4

# With custom sounds
postprod audio --input video.mp4 --sounds-dir mido/melodies/mario/

# Adjust volume
postprod audio --input video.mp4 --volume 0.8
```

#### Text Overlay

Add text caption to video:

```bash
# Basic overlay
postprod overlay --input video.mp4 --text "Level 3"

# With emoji
postprod overlay --input video.mp4 --text "Victory! 🏆"

# Custom styling
postprod overlay --input video.mp4 --text "Hello" \
    --font-size 72 \
    --color white \
    --margin-top 50
```

#### Full Postproduction

Complete pipeline (audio + overlay):

```bash
postprod full --input video.mp4 --text "Level 3" --sounds-dir sounds/
```

### Makefile Targets

```bash
make audio INPUT=video.mp4 [SOUNDS_DIR=sounds/]
make overlay INPUT=video.mp4 TEXT="text"
make postprocess INPUT=video.mp4 TEXT="text" [SOUNDS_DIR=sounds/]

# Batch processing
make batch-audio              # Process all in recordings/
make batch-overlay TEXT="Hi"  # Overlay all in final_recordings/

# Melody generator
make generate-melody MELODY=imperial_march
make list-melodies
```

## Input Format

### Video Files

Silent MP4 video files (typically `*_video_*.mp4` from game recordings).

### Events JSON

JSON file with collision events metadata:

```json
{
  "recording_info": {
    "total_frames": 1200,
    "duration": 20.0
  },
  "collision_events": [
    {
      "frame_number": 100,
      "timestamp": 1.666,
      "impact_intensity": 0.85
    }
  ]
}
```

**Note:** This project uses a simplified JSON format with only 3 fields per event.
Full format from Balls game (with position/velocity data) is also supported - extra fields are ignored.

## Project Structure

```
video-postproduction/
├── src/
│   ├── cli.py              # Unified CLI entry point
│   ├── mixer.py            # Audio mixing (PostProductionMixer)
│   ├── overlay.py          # Text overlay
│   └── collision_events.py # Event data structures
├── mido/                   # Melody generator module
│   ├── config.py           # Melody definitions
│   ├── generator.py        # MIDI generation
│   └── melodies/           # Generated WAV/MIDI files
├── sounds/                 # Default collision sounds
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Sound Packs

### Default Sounds

The `sounds/` directory contains numbered WAV files (01.wav, 02.wav, ...) that are played sequentially for each collision, creating a melodic progression.

### Custom Sound Packs

Use the `--sounds-dir` option to specify alternative sound directories:

```bash
# Use Mario-style sounds
make audio INPUT=video.mp4 SOUNDS_DIR=mido/melodies/mario/

# Use Imperial March melody
make audio INPUT=video.mp4 SOUNDS_DIR=mido/melodies/imperial_march/
```

### Generating New Melodies

Use the bundled `mido` module to generate new sound packs:

```bash
# Generate Imperial March notes
make generate-melody MELODY=imperial_march

# Available melodies
make list-melodies
```

## Text Overlay Options

| Option | Default | Description |
|--------|---------|-------------|
| `--text` | required | Caption text (supports emoji) |
| `--font` | Sans | Font family name |
| `--font-file` | - | Path to TTF/OTF font |
| `--font-size` | 60 | Font size in pixels |
| `--color` | white | Text color |
| `--margin-top` | 100 | Top margin in pixels |
| `--align` | center | left/center/right |
| `--bar-opacity` | 0.0 | Background bar opacity (0-1) |
| `--render-engine` | pango_png | pango_png/pillow_png/ffmpeg_text |

## Render Engines

- **pango_png** (default) - Best emoji support, requires `pango-view`
- **pillow_png** - Pure Python, good compatibility
- **ffmpeg_text** - Direct FFmpeg drawtext, fastest but limited emoji

## License

MIT License

