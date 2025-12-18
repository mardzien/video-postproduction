# YouTube Shorts Templates

Comprehensive guide to using predefined templates for rapid YouTube Shorts production.

## 📋 Overview

Templates provide complete configurations (audio, text, styling) for video postproduction. Instead of specifying all parameters manually, you can use a template and optionally override specific values.

## 🚀 Quick Start

### List Available Templates

```bash
make list-templates

# Or directly:
postprod shorts --list-templates
```

### Use a Template

```bash
# Basic usage
make shorts INPUT=recordings/video.webm TEMPLATE=christmas

# With auto-numbering
make shorts INPUT=recordings/video.webm TEMPLATE=christmas AUTO_NUMBER=1

# Override template text
make shorts INPUT=recordings/video.webm TEMPLATE=christmas TEXT="Custom Text 🎄"
```

### Direct CLI Usage

```bash
# Process single video
postprod shorts \
  --input recordings/BallGame_2025-12-02_22-18-38.webm \
  --template christmas

# Process with overrides
postprod shorts \
  --input recordings/*.webm \
  --template mario_challenge \
  --text "New Challenge! 🎮" \
  --auto-number

# Batch processing with glob pattern
postprod shorts \
  --input "recordings/BallGame_*.webm" \
  --template epic_imperial \
  --auto-number
```

## 📦 Available Templates

### `christmas`

**Description:** Christmas-themed short with jingle bells

**Features:**
- 🎄 Christmas emoji (tree, bells, reindeer, Santa)
- 🎵 Jingle Bells melody sounds
- 🟢 Dark green background bar (subtle)
- 📏 Large text (75pt) centered at top

**Text:** `🎄🔔 Will the bass escape? 🦌🎅`

**Output:** `shorts_christmas_001.mp4`, `shorts_christmas_002.mp4`, etc.

---

### `christmas_carol_of_bells`

**Description:** Carol of the Bells challenge

**Features:**
- 🔔 Classic Christmas melody
- ⏱️ 3-second escape challenge text
- 🟢 Christmas theme

**Text:**
```
🎄🔔 Each ball has 3 s 🔔🎄
🕐Will it escape in time?🕐
```

**Output:** `shorts_christmas_carol_001.mp4`, etc.

---

### `christmas_deck_the_halls`

**Description:** Deck the Halls challenge

**Features:**
- 🎅 Joyful Christmas melody
- ⏱️ 3-second escape challenge text

**Text:**
```
🎅 Each ball has 3 s 🎅
🕐Will it escape in time?🕐
```

**Output:** `shorts_christmas_deck_001.mp4`, etc.

---

### `christmas_we_wish_you`

**Description:** We Wish You a Merry Christmas challenge

**Features:**
- 🎄 Waltz-style melody
- ⏱️ 3-second escape challenge text

**Text:**
```
🎄 Each ball has 3 s 🎄
🕐Will it escape in time?🕐
```

**Output:** `shorts_christmas_wewish_001.mp4`, etc.

---

### `mario_challenge`

**Description:** Mario-themed challenge with classic sounds

**Features:**
- 🍄 Mario-themed emoji
- 🎵 Super Mario Bros melody sounds
- 🔴 Red background bar
- 📝 Two-line text with challenge prompt

**Text:**
```
🍄 Mario Challenge 🎮
Can you beat the high score?
```

**Output:** `shorts_mario_001.mp4`, `shorts_mario_002.mp4`, etc.

---

### `epic_imperial`

**Description:** Epic theme with Imperial March

**Features:**
- ⚔️ Epic/dramatic emoji
- 🎵 Imperial March melody sounds
- ⚫ Dark gray background bar (stronger opacity)
- 🔠 Extra large text (80pt)

**Text:** `⚔️ EPIC MODE ⚔️`

**Output:** `shorts_epic_001.mp4`, `shorts_epic_002.mp4`, etc.

---

### `basic_minimal`

**Description:** Minimal clean template with default sounds

**Features:**
- 👀 Simple emoji
- 🎵 Default sound set
- 🚫 No background bar (transparent)
- 📏 Medium text (65pt)

**Text:** `Watch This! 👀`

**Output:** `shorts_001.mp4`, `shorts_002.mp4`, etc.

## 🎨 Template Structure

Templates are defined in YAML files located in `templates/examples/`. Here's the structure:

```yaml
name: template_name
description: Short description of the template
video_format: shorts  # shorts (9:16) or landscape (16:9)

audio:
  sounds_dir: mido/melodies/jingle_bells  # Path to WAV sounds
  volume: 0.75                            # Volume multiplier (0.0-1.0)

overlay:
  text: "🎄🔔 Will the bass escape? 🦌🎅"
  font_size: 75                           # Font size in pixels
  color: white                            # Text color
  margin_top: 120                         # Top margin in pixels
  bar_opacity: 0.2                        # Background bar opacity (0-1)
  bar_color: "#1a472a"                    # Background bar color (hex/name)
  shadow: true                            # Text shadow enabled
  render_engine: pango_png                # pango_png/pillow_png/ffmpeg_text
  align: center                           # left/center/right
  font: null                              # Font family (optional)
  font_file: null                         # TTF/OTF path (optional)
  bar_height: 120                         # Background bar height
  padding_x: 120                          # Horizontal padding

output:
  prefix: shorts_christmas                # Output filename prefix
  format: mp4                             # Output format
  quality: high                           # high/medium/low (CRF 18/23/28)
```

## 🔧 Overriding Template Values

You can override specific template values via CLI arguments:

### Override Text

```bash
postprod shorts \
  --template christmas \
  --text "🎅 Santa's Challenge! 🎁" \
  --input video.webm
```

### Override Sounds

```bash
postprod shorts \
  --template christmas \
  --sounds-dir sounds/mario \
  --input video.webm
```

### Override Volume

```bash
postprod shorts \
  --template epic_imperial \
  --volume 0.9 \
  --input video.webm
```

### Multiple Overrides

```bash
postprod shorts \
  --template basic_minimal \
  --text "New Text! 🔥" \
  --sounds-dir mido/melodies/mario \
  --volume 0.8 \
  --input video.webm
```

## 📝 Creating Custom Templates

### Option 1: Copy and Edit Existing Template

```bash
# Copy example template
cp templates/examples/christmas.yaml templates/my_template.yaml

# Edit with your settings
nano templates/my_template.yaml

# Use your template
postprod shorts --template my_template --input video.webm
```

### Option 2: Create from Python

```python
from src.templates import ShortsTemplate, AudioConfig, OverlayTemplateConfig, OutputConfig, TemplateManager

# Define template
template = ShortsTemplate(
    name="my_custom_template",
    description="My awesome custom template",
    video_format="shorts",
    audio=AudioConfig(
        sounds_dir="sounds/",
        volume=0.7,
    ),
    overlay=OverlayTemplateConfig(
        text="My Custom Text 🚀",
        font_size=70,
        color="yellow",
        bar_opacity=0.3,
        bar_color="#000080",  # Navy blue
    ),
    output=OutputConfig(
        prefix="custom_shorts",
        format="mp4",
        quality="high",
    ),
)

# Save template
mgr = TemplateManager()
mgr.save_template(template, "my_custom_template")
```

## 🎯 Workflow Examples

### Example 1: Christmas Short Campaign

Process multiple videos with Christmas theme:

```bash
# Process all BallGame recordings with Christmas template
postprod shorts \
  --input "recordings/BallGame_*.webm" \
  --template christmas \
  --auto-number

# Output: shorts_christmas_001.mp4, shorts_christmas_002.mp4, etc.
```

### Example 2: A/B Testing Different Styles

Test same video with different templates:

```bash
# Epic style
postprod shorts \
  --input recordings/best_game.webm \
  --template epic_imperial \
  --output final_recordings/test_epic.mp4

# Mario style
postprod shorts \
  --input recordings/best_game.webm \
  --template mario_challenge \
  --output final_recordings/test_mario.mp4

# Minimal style
postprod shorts \
  --input recordings/best_game.webm \
  --template basic_minimal \
  --output final_recordings/test_minimal.mp4
```

### Example 3: Custom Text with Template Styling

Keep template styling but change text:

```bash
postprod shorts \
  --input recordings/level5.webm \
  --template christmas \
  --text "🎄 Level 5 Complete! 🎁" \
  --auto-number
```

## 🎬 Complete Workflow

1. **Record gameplay** → outputs to `recordings/`
2. **Choose template** → `make list-templates`
3. **Process video** → `make shorts INPUT=recordings/game.webm TEMPLATE=christmas`
4. **Review output** → `final_recordings/shorts_christmas_001.mp4`
5. **Upload to YouTube Shorts** 🚀

## 🔄 Batch Processing

Process entire directory with one command:

```bash
# Process all webm files
for video in recordings/*.webm; do
  postprod shorts \
    --input "$video" \
    --template christmas \
    --auto-number
done

# Or use glob pattern (cleaner)
postprod shorts \
  --input "recordings/*.webm" \
  --template christmas \
  --auto-number
```

## 📚 Advanced Topics

### Template Search Order

When loading a template, the system searches:
1. `templates/examples/{name}.yaml` (bundled examples)
2. `templates/{name}.yaml` (custom templates)

### Auto-numbering Logic

With `--auto-number`:
- Scans `final_recordings/` for existing files matching `{prefix}_*.mp4`
- Extracts numbers from filenames (e.g., `shorts_christmas_005.mp4` → 5)
- Uses next available number (e.g., 6 → `shorts_christmas_006.mp4`)

### Quality Settings

| Quality | CRF | Use Case |
|---------|-----|----------|
| `high`  | 18  | Final upload (default) |
| `medium`| 23  | Preview/testing |
| `low`   | 28  | Quick draft |

## 🛠️ Troubleshooting

### Template Not Found

```
❌ Template 'my_template' not found
```

**Solution:** Use `make list-templates` to see available templates.

### Missing Sounds Directory

```
❌ Sounds directory not found: mido/melodies/xyz
```

**Solution:**
- Check path in template YAML
- Generate melody: `make generate-melody MELODY=jingle_bells`
- Override with existing sounds: `--sounds-dir sounds/`

### Text Rendering Issues

If emoji don't render properly:
- Install `pango-view`: `sudo dnf install pango` (Fedora) or `sudo apt install libpango1.0-dev` (Ubuntu)
- Or switch engine: add `render_engine: pillow_png` to template overlay section

## 📖 Reference

### Makefile Targets

```bash
make shorts INPUT=video.webm TEMPLATE=name     # Process with template
make list-templates                            # List available templates
make create-templates                          # Generate example templates
```

### CLI Command

```bash
postprod shorts --help                         # Full help
postprod shorts --list-templates               # List templates
postprod shorts -i video.webm -t template_name # Process video
```

### Template Variables

See [Template Structure](#🎨-template-structure) section above for complete YAML format.

---

## 💡 Tips

1. **Start with examples** - Copy and modify existing templates rather than creating from scratch
2. **Use auto-numbering** - Prevents filename conflicts in batch processing
3. **Test with one video** - Validate template before batch processing
4. **Keep text short** - Shorts viewers scroll quickly, 1-2 lines max
5. **Use emoji wisely** - They grab attention but don't overdo it
6. **Match sound to theme** - Audio reinforces visual message

---

**Happy Shorts Creation! 🎬✨**

