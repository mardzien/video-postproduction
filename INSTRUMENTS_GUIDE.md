# Przewodnik po Instrumentach MIDI (General MIDI)

## Jak Używać Dowolnego Instrumentu

Możesz użyć **dowolnego z 128 instrumentów General MIDI** w swoich templatekach lub przez CLI.

### Sposób 1: Przez Parametr CLI

```bash
# Użyj dowolnego instrumentu z szablonem
postprod shorts --template mario --instrument 30 --input video.mp4

# Gdzie 30 = Overdriven Guitar
```

### Sposób 2: Bezpośrednio w Templatece

Edytuj plik `.yaml` w `templates/examples/`:

```yaml
audio:
  midi_file: midi_files/your_song.mid
  instrument: 42  # <- Zmień na dowolny numer 0-127
  track: 0
  volume: 1.0
```

### Sposób 3: Stwórz Nową Templatekę

```bash
cp templates/examples/mario.yaml templates/examples/mario_organ.yaml
# Następnie edytuj i zmień instrument na 19 (Church Organ)
```

---

## Pełna Lista Instrumentów General MIDI (0-127)

### 🎹 PIANO (0-7)
- **0** = Acoustic Grand Piano
- **1** = Bright Acoustic Piano
- **2** = Electric Grand Piano
- **3** = Honky-tonk Piano
- **4** = Electric Piano 1
- **5** = Electric Piano 2
- **6** = Harpsichord
- **7** = Clavinet

### 🎼 CHROMATIC PERCUSSION (8-15)
- **8** = Celesta
- **9** = Glockenspiel
- **10** = Music Box ⭐ *Popularny do lullabies*
- **11** = Vibraphone
- **12** = Marimba
- **13** = Xylophone
- **14** = Tubular Bells ⭐ *Świąteczny vibe*
- **15** = Dulcimer

### 🎹 ORGAN (16-23)
- **16** = Drawbar Organ
- **17** = Percussive Organ
- **18** = Rock Organ ⭐ *Vintage keyboard*
- **19** = Church Organ ⭐ *Majestatyczny*
- **20** = Reed Organ
- **21** = Accordion
- **22** = Harmonica
- **23** = Tango Accordion

### 🎸 GUITAR (24-31)
- **24** = Acoustic Guitar (nylon)
- **25** = Acoustic Guitar (steel)
- **26** = Electric Guitar (jazz)
- **27** = Electric Guitar (clean)
- **28** = Electric Guitar (muted)
- **29** = Overdriven Guitar ⭐ *Rock power*
- **30** = Distortion Guitar ⭐ *Metal/Epic*
- **31** = Guitar Harmonics

### 🎸 BASS (32-39)
- **32** = Acoustic Bass
- **33** = Electric Bass (finger)
- **34** = Electric Bass (pick)
- **35** = Fretless Bass
- **36** = Slap Bass 1
- **37** = Slap Bass 2
- **38** = Synth Bass 1
- **39** = Synth Bass 2

### 🎻 STRINGS (40-47)
- **40** = Violin
- **41** = Viola
- **42** = Cello
- **43** = Contrabass
- **44** = Tremolo Strings
- **45** = Pizzicato Strings
- **46** = Orchestral Harp
- **47** = Timpani

### 🎻 ENSEMBLE (48-55)
- **48** = String Ensemble 1 ⭐ *Filmowy*
- **49** = String Ensemble 2
- **50** = Synth Strings 1
- **51** = Synth Strings 2
- **52** = Choir Aahs ⭐ *Epickie chóry*
- **53** = Voice Oohs
- **54** = Synth Voice
- **55** = Orchestra Hit

### 🎺 BRASS (56-63)
- **56** = Trumpet
- **57** = Trombone
- **58** = Tuba
- **59** = Muted Trumpet
- **60** = French Horn
- **61** = Brass Section ⭐ *Imperial March*
- **62** = Synth Brass 1
- **63** = Synth Brass 2

### 🎷 REED (64-71)
- **64** = Soprano Sax
- **65** = Alto Sax ⭐ *Pink Panther jazz*
- **66** = Tenor Sax
- **67** = Baritone Sax
- **68** = Oboe
- **69** = English Horn
- **70** = Bassoon
- **71** = Clarinet

### 🎵 PIPE (72-79)
- **72** = Piccolo
- **73** = Flute
- **74** = Recorder
- **75** = Pan Flute
- **76** = Blown Bottle
- **77** = Shakuhachi
- **78** = Whistle ⭐ *Gravity Falls*
- **79** = Ocarina

### 🎹 SYNTH LEAD (80-87)
- **80** = Lead 1 (square) ⭐ *Retro gaming (Tetris, Pacman)*
- **81** = Lead 2 (sawtooth) ⭐ *EDM/Trance (Tokyo Drift, Avicii)*
- **82** = Lead 3 (calliope) ⭐ *Circus theme*
- **83** = Lead 4 (chiff)
- **84** = Lead 5 (charang)
- **85** = Lead 6 (voice)
- **86** = Lead 7 (fifths)
- **87** = Lead 8 (bass + lead)

### 🎹 SYNTH PAD (88-95)
- **88** = Pad 1 (new age)
- **89** = Pad 2 (warm)
- **90** = Pad 3 (polysynth)
- **91** = Pad 4 (choir)
- **92** = Pad 5 (bowed)
- **93** = Pad 6 (metallic)
- **94** = Pad 7 (halo)
- **95** = Pad 8 (sweep)

### 🎹 SYNTH EFFECTS (96-103)
- **96** = FX 1 (rain)
- **97** = FX 2 (soundtrack)
- **98** = FX 3 (crystal)
- **99** = FX 4 (atmosphere)
- **100** = FX 5 (brightness)
- **101** = FX 6 (goblins)
- **102** = FX 7 (echoes)
- **103** = FX 8 (sci-fi)

### 🎻 ETHNIC (104-111)
- **104** = Sitar
- **105** = Banjo
- **106** = Shamisen
- **107** = Koto
- **108** = Kalimba
- **109** = Bag pipe
- **110** = Fiddle
- **111** = Shanai

### 🥁 PERCUSSIVE (112-119)
- **112** = Tinkle Bell
- **113** = Agogo
- **114** = Steel Drums
- **115** = Woodblock
- **116** = Taiko Drum
- **117** = Melodic Tom
- **118** = Synth Drum
- **119** = Reverse Cymbal

### 🔊 SOUND EFFECTS (120-127)
- **120** = Guitar Fret Noise
- **121** = Breath Noise
- **122** = Seashore
- **123** = Bird Tweet
- **124** = Telephone Ring
- **125** = Helicopter
- **126** = Applause
- **127** = Gunshot

---

## 🎯 Najczęściej Używane Instrumenty

### Dla Muzyki Dziecięcej
- **11** = Music Box
- **12** = Marimba
- **13** = Xylophone
- **9** = Glockenspiel

### Dla EDM/Electronic
- **80** = Lead 1 (Square) - Retro
- **81** = Lead 2 (Sawtooth) - Agresywny EDM
- **38** = Synth Bass 1
- **62** = Synth Brass 1

### Dla Rock/Metal
- **29** = Overdriven Guitar
- **30** = Distortion Guitar
- **33** = Electric Bass
- **61** = Brass Section (dla epic vibes)

### Dla Filmów/Cinematic
- **48** = String Ensemble
- **52** = Choir Aahs
- **61** = Brass Section
- **0** = Acoustic Grand Piano

### Dla Jazz
- **65** = Alto Sax
- **0** = Acoustic Grand Piano
- **32** = Acoustic Bass

### Dla Retro Gaming
- **80** = Lead 1 (Square)
- **81** = Lead 2 (Sawtooth)
- **11** = Music Box

---

## 💡 Przykłady Użycia

### Zmiana Nastroju Tej Samej Melodii

**Mario - Różne Instrumenty = Różny Vibe:**

```bash
# Oryginał: Music Box (dziecięcy)
postprod shorts --template mario --input video.mp4

# Wersja Organ (majestatyczna)
postprod shorts --template mario --instrument 19 --input video.mp4

# Wersja Distortion Guitar (epicka)
postprod shorts --template mario --instrument 30 --input video.mp4

# Wersja EDM Synth (taneczna)
postprod shorts --template mario --instrument 81 --input video.mp4

# Wersja Choir (chóralna)
postprod shorts --template mario --instrument 52 --input video.mp4
```

### Gravity Falls - 6 Wersji

```bash
# Domyślnie: Church Organ
postprod shorts --template gravity_falls --input video.mp4

# Piano (klasyczna)
postprod shorts --template gravity_falls --instrument 0 --input video.mp4

# Music Box (dziecięca)
postprod shorts --template gravity_falls --instrument 11 --input video.mp4

# Violin (smyczkowa)
postprod shorts --template gravity_falls --instrument 40 --input video.mp4

# Guitar (folkowa)
postprod shorts --template gravity_falls --instrument 24 --input video.mp4

# EDM Synth (elektroniczna)
postprod shorts --template gravity_falls --instrument 81 --input video.mp4
```

### Eksperymenty

**Sprawdź jak brzmi Megalovania jako:**
- Choir Aahs (52) - epickie chóry
- Brass Section (61) - orkiestra dęta
- Synth Bass (38) - bassline
- String Ensemble (48) - smyczki

```bash
postprod shorts --template megalovania --instrument 52 --input video.mp4
postprod shorts --template megalovania --instrument 61 --input video.mp4
postprod shorts --template megalovania --instrument 38 --input video.mp4
postprod shorts --template megalovania --instrument 48 --input video.mp4
```

---

## 🎨 Tworzenie Własnych Wariantów

### Metoda 1: Szybkie Testy przez CLI

```bash
# Przetestuj różne instrumenty szybko
for i in 0 11 19 30 48 61 81; do
  postprod shorts --template mario --instrument $i --input video.mp4
done
```

### Metoda 2: Stwórz Osobne Templateki

```bash
# Stwórz warianty dla tej samej melodii
cp templates/examples/mario.yaml templates/examples/mario_piano.yaml
cp templates/examples/mario.yaml templates/examples/mario_organ.yaml
cp templates/examples/mario.yaml templates/examples/mario_guitar.yaml

# Następnie edytuj każdy plik i zmień instrument oraz prefix:
# mario_piano.yaml: instrument: 0, prefix: shorts_mario_piano
# mario_organ.yaml: instrument: 19, prefix: shorts_mario_organ
# mario_guitar.yaml: instrument: 30, prefix: shorts_mario_guitar
```

---

## 📚 Więcej Informacji

- Pełna specyfikacja GM: https://en.wikipedia.org/wiki/General_MIDI
- Interaktywna tabela: https://www.midi.org/specifications/item/gm-level-1-sound-set

---

## 🎵 Podsumowanie

**Możesz użyć DOWOLNEGO instrumentu 0-127 na 3 sposoby:**

1. **CLI**: `--instrument N`
2. **Template**: `instrument: N` w pliku YAML
3. **Stwórz wariant**: Skopiuj template i zmień instrument

**Najczęściej używane:**
- 0 (Piano) - uniwersalny
- 11 (Music Box) - dziecięcy
- 19 (Church Organ) - majestatyczny
- 30 (Distortion Guitar) - epic/rock
- 48 (String Ensemble) - filmowy
- 61 (Brass Section) - złowieszczy
- 80 (Square Lead) - retro gaming
- 81 (Sawtooth Lead) - EDM/trance

**Eksperymentuj!** Każdy instrument nadaje melodii inny charakter. 🎨
