# 🎵 MIDI Postproduction - Cheat Sheet

## Podstawowe Komendy

```bash
# Lista templatek
postprod shorts --list-templates

# Użyj templateki
postprod shorts --template NAZWA --input video.mp4

# Zmień instrument
postprod shorts --template NAZWA --instrument NUMER --input video.mp4

# Batch processing
postprod shorts --template NAZWA --input recordings/*.webm --auto-number
```

---

## 20 Templatek (Szybki Wybór)

| Kategoria | Templateki |
|-----------|-----------|
| **Gaming 🎮** | mario, megalovania, tokyo_drift, pacman, tetris, gta |
| **TV 📺** | gravity_falls, dexter, succession, true_detective, white_lotus, imperial_march |
| **Music 🎵** | avicii_levels, baby_shark, better_off, twinkle |
| **Film 🎬** | circus, mission_impossible, pink_panther, witcher |

---

## Top 10 Instrumentów

| Nr | Instrument | Kiedy używać |
|----|-----------|--------------|
| **0** | Piano | Uniwersalny, klasyczny |
| **11** | Music Box | Dziecięcy, lullaby |
| **19** | Organ | Majestatyczny, kościelny |
| **30** | Distortion Guitar | Epic, rock, metal |
| **40** | Violin | Smyczkowy, elegancki |
| **48** | Strings | Orkiestrowy, filmowy |
| **52** | Choir | Epickie chóry |
| **61** | Brass | Złowieszczy, potężny |
| **80** | Square Lead | Retro gaming, 8-bit |
| **81** | Sawtooth Lead | EDM, trance, aggressive |

---

## Szybkie Przykłady

### Test Jednej Templateki
```bash
postprod shorts --template mario --input video.mp4
```

### Test Różnych Instrumentów
```bash
postprod shorts --template mario --instrument 0 --input video.mp4    # Piano
postprod shorts --template mario --instrument 30 --input video.mp4   # Guitar
postprod shorts --template mario --instrument 81 --input video.mp4   # EDM
```

### Batch Processing
```bash
postprod shorts --template gravity_falls --input recordings/*.webm --auto-number
```

### Własny MIDI
```bash
postprod shorts --template mario \
  --midi "midi_files/custom.mid" \
  --instrument 19 \
  --input video.mp4
```

---

## Kategorie Instrumentów (GM)

| Zakres | Kategoria | Przykłady |
|--------|-----------|-----------|
| 0-7 | Piano | 0=Piano, 6=Harpsichord |
| 8-15 | Chromatic | 11=Music Box, 14=Bells |
| 16-23 | Organ | 19=Church Organ, 21=Accordion |
| 24-31 | Guitar | 25=Steel Guitar, 30=Distortion |
| 32-39 | Bass | 33=Electric Bass, 38=Synth Bass |
| 40-47 | Strings | 40=Violin, 42=Cello |
| 48-55 | Ensemble | 48=Strings, 52=Choir |
| 56-63 | Brass | 56=Trumpet, 61=Brass Section |
| 64-71 | Reed | 65=Alto Sax, 68=Oboe |
| 72-79 | Pipe | 73=Flute, 78=Whistle |
| 80-87 | Synth Lead | 80=Square, 81=Sawtooth |
| 88-103 | Synth Pad/FX | 88=New Age, 98=Crystal |
| 104-119 | Ethnic/Percussive | 105=Banjo, 114=Steel Drums |

---

## Szybkie Kombinacje (Copy-Paste Ready)

### Gaming Challenge
```bash
postprod shorts --template mario --instrument 80 --input video.mp4
postprod shorts --template tetris --instrument 80 --input video.mp4
postprod shorts --template pacman --instrument 80 --input video.mp4
```

### Epic/Cinematic
```bash
postprod shorts --template imperial_march --instrument 61 --input video.mp4
postprod shorts --template witcher --instrument 48 --input video.mp4
postprod shorts --template megalovania --instrument 30 --input video.mp4
```

### EDM/Electronic
```bash
postprod shorts --template avicii_levels --instrument 81 --input video.mp4
postprod shorts --template tokyo_drift --instrument 81 --input video.mp4
postprod shorts --template better_off --instrument 81 --input video.mp4
```

### Kids/Family
```bash
postprod shorts --template baby_shark --instrument 12 --input video.mp4
postprod shorts --template twinkle --instrument 11 --input video.mp4
postprod shorts --template circus --instrument 11 --input video.mp4
```

### Dark/Mystery
```bash
postprod shorts --template dexter --instrument 0 --input video.mp4
postprod shorts --template true_detective --instrument 25 --input video.mp4
postprod shorts --template gravity_falls --instrument 19 --input video.mp4
```

---

## Parametry CLI

```bash
--template, -t      # Nazwa templateki (wymagane)
--input, -i         # Plik wideo lub pattern (wymagane)
--output, -o        # Plik wyjściowy (opcjonalne)
--midi, -m          # Override: plik MIDI
--instrument, -I    # Override: instrument GM (0-127)
--track, -T         # Override: track MIDI
--channel, -C       # Override: channel MIDI (0-15)
--text              # Override: tekst overlaya
--volume            # Override: głośność (0.0-1.0)
--auto-number, -n   # Autonumerowanie (shorts_001, shorts_002, ...)
--cleanup           # Usuń pliki źródłowe po przetworzeniu
--list-templates, -l # Pokaż dostępne templateki
```

---

## Troubleshooting

### "No module named 'ffmpeg'"
```bash
pip install ffmpeg-python scipy numpy mido midi2audio pyyaml
```

### "MIDI file not found"
Sprawdź ścieżkę:
```bash
ls midi_files/  # Plik musi istnieć
```

### "instrument is required"
Dodaj instrument w templatece lub CLI:
```bash
--instrument 0  # Piano
```

### Template nie ładuje się
Sprawdź YAML:
```bash
python -c "import yaml; yaml.safe_load(open('templates/examples/mario.yaml'))"
```

---

## Dokumentacja

- **Quick Start:** `QUICK_START_MIDI.md`
- **Wszystkie Templateki:** `TEMPLATES_OVERVIEW.md`
- **Lista Instrumentów:** `INSTRUMENTS_GUIDE.md`
- **Szczegóły Techniczne:** `IMPLEMENTATION_SUMMARY.md`

---

## 🎯 Pro Tips

1. **Eksperymentuj** - Ten sam MIDI, różne instrumenty = różne viby
2. **Batch processing** - Użyj `*.webm` i `--auto-number`
3. **Override wszystko** - Każdy parametr templateki można nadpisać
4. **Kategorie instrumentów** - 80-87 = Synth Leads (gaming/EDM)
5. **Własne MIDI** - Dodaj plik do `midi_files/` i użyj `--midi`

---

**Formula sukcesu:**
```
Twój MIDI + Dobry instrument + Ciekawy tekst = Viral Short! 🚀
```
