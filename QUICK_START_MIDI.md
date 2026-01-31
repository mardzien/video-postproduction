# Quick Start: MIDI-based Video Postproduction

## What Changed?

Your video postproduction system now works **directly with MIDI files** instead of generating thousands of WAV files. This means:

✅ **Faster setup** - No need to run generator.py  
✅ **Less space** - 20 MIDI files instead of 3600+ WAV files  
✅ **More flexible** - Change instruments instantly  
✅ **Same workflow** - All your existing commands still work!

---

## Basic Usage (Nothing Changed!)

Your existing commands work exactly the same:

```bash
# List available templates
postprod shorts --list-templates

# Use a template
postprod shorts --template mario --input recordings/video_*.mp4

# Process with cleanup
postprod shorts --template gravity_falls --input video.mp4 --cleanup
```

**The difference?** Now these templates use MIDI files internally, so you can change instruments without regenerating files.

---

## New Feature: Change Instruments on the Fly

Want to hear Mario in a different instrument? Just override:

```bash
# Original: Music Box (instrument 11)
postprod shorts --template mario --input video.mp4

# Try Piano instead (instrument 0)
postprod shorts --template mario --instrument 0 --input video.mp4

# Try Organ (instrument 19)
postprod shorts --template mario --instrument 19 --input video.mp4

# Try Overdriven Guitar (instrument 30)
postprod shorts --template mario --instrument 30 --input video.mp4
```

### GM Instrument Numbers (Most Useful)

**Piano/Keyboard:**
- 0 = Acoustic Grand Piano
- 8 = Celesta
- 11 = Music Box
- 13 = Xylophone

**Organ:**
- 16 = Drawbar Organ
- 19 = Church Organ

**Guitar:**
- 24 = Acoustic Guitar (nylon)
- 25 = Steel String Guitar
- 29 = Overdriven Guitar
- 30 = Distortion Guitar

**Bass:**
- 32 = Acoustic Bass
- 33 = Electric Bass

**Strings:**
- 40 = Violin
- 42 = Cello
- 48 = String Ensemble

**Brass:**
- 56 = Trumpet
- 57 = Trombone
- 61 = Brass Section

**Synth Lead (EDM/Electronic):**
- 80 = Lead 1 (Square wave)
- 81 = Lead 2 (Sawtooth)

**Full list:** [GM Instrument List](https://en.wikipedia.org/wiki/General_MIDI#Program_change_events)

---

## Your Available Templates (All MIDI-based Now)

All 20 templates are now available with MIDI support:

### Gaming Classics 🎮
1. **mario** - Super Mario Bros with Music Box
2. **megalovania** - Undertale battle with Distortion Guitar
3. **tokyo_drift** - Drift racing with Violin (or synth!)
4. **pacman** - Arcade classic with Square wave
5. **tetris** - Russian folk tune with Square wave
6. **gta** - GTA San Andreas with Electric Bass

### TV Series 📺
7. **gravity_falls** - Mystery theme with Church Organ
8. **dexter** - Dark theme with Piano
9. **succession** - Power drama with Piano
10. **true_detective** - Dark mystery with Steel Guitar
11. **white_lotus** - Resort drama with Piano
12. **imperial_march** - Star Wars with Brass Section

### Music Hits 🎵
13. **avicii_levels** - EDM classic with Sawtooth synth
14. **baby_shark** - Children's song with Marimba
15. **better_off** - 90s trance with Church Organ
16. **twinkle** - Lullaby with Music Box

### Film/Entertainment 🎬
17. **circus** - Carnival theme with Music Box
18. **mission_impossible** - Spy action with Piano
19. **pink_panther** - Jazzy mystery with Alto Sax
20. **witcher** - Fantasy epic with String Ensemble

**Use any template:**
```bash
postprod shorts --template [name] --input video.mp4
```

---

## Creating Your Own MIDI-based Template

1. **Add your MIDI file** to `midi_files/` folder

2. **Create a template** in `templates/examples/your_template.yaml`:

```yaml
name: your_template
description: "My custom video template"
video_format: shorts

audio:
  midi_file: midi_files/your_song.mid  # Your MIDI file
  instrument: 0                         # Piano (or any GM instrument)
  track: 0                              # MIDI track (usually 0)
  volume: 1.0                           # Volume level

overlay:
  text: "Your Challenge Text Here 🎵"
  font_size: 50
  color: white
  margin_top: 360
  bar_opacity: 0
  shadow: true
  align: center
  render_engine: pango_png

output:
  prefix: shorts_your_name
  format: mp4
  quality: high
```

3. **Use it:**

```bash
postprod shorts --template your_template --input video.mp4
```

---

## Advanced: Multiple Instrument Variants

Want to quickly try different instruments for the same melody? Use melody mappings:

```bash
# Check what variants are available for a melody
cat templates/melodies/gravity_falls.yaml

# Will show:
# variants:
#   organ: 19      # Church Organ
#   piano: 0       # Piano
#   music_box: 11  # Music Box
#   violin: 40     # Violin
#   guitar: 24     # Guitar
#   edm: 81        # EDM Synth
```

Then use any variant by number:

```bash
# Try different instruments
postprod shorts --template gravity_falls --instrument 40 --input video.mp4  # Violin
postprod shorts --template gravity_falls --instrument 81 --input video.mp4  # EDM
```

---

## What About Old WAV Files?

The old `mido/melodies/` folder with thousands of WAV files is **still there** for backward compatibility, but you don't need it anymore.

**Safe to delete later** once you've verified everything works with MIDI.

---

## Testing Your Setup

Run the integration test to verify everything works:

```bash
python test_midi_integration.py
```

This will check:
- ✅ MIDI renderer works
- ✅ Templates load correctly
- ✅ File syntax is valid

---

## Troubleshooting

### "No module named 'ffmpeg'"

Install dependencies:
```bash
pip install ffmpeg-python scipy numpy mido midi2audio pyyaml
```

### "MIDI file not found"

Make sure your MIDI file exists in `midi_files/` and the path in your template is correct:
```yaml
midi_file: midi_files/your_file.mid  # Correct
midi_file: your_file.mid              # Wrong (missing folder)
```

### "instrument is required when using midi_file"

Add an instrument number to your template:
```yaml
audio:
  midi_file: midi_files/song.mid
  instrument: 0  # <- Add this!
```

### Template not loading

Check YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('templates/examples/your_template.yaml'))"
```

---

## Questions?

- 📖 See `IMPLEMENTATION_SUMMARY.md` for technical details
- 🎵 Check `templates/melodies/*.yaml` for melody mappings
- 📝 Look at `templates/examples/*.yaml` for template examples
- 🧪 Run `python test_midi_integration.py` to verify setup

---

## Summary

**Before:**
```bash
# Generate WAV files (once)
python -m mido.generator

# Use template
postprod shorts --template mario --input video.mp4
```

**After:**
```bash
# No generation needed - just use templates directly!
postprod shorts --template mario --input video.mp4

# Change instrument anytime
postprod shorts --template mario --instrument 30 --input video.mp4
```

🎉 **That's it! Enjoy your streamlined MIDI-based workflow!**
