# 🎵 MIDO VIRAL MELODIES - Przewodnik Użytkownika

## 🔥 SUPER VIRALNE MELODIE!

Moduł MIDO zawiera teraz **16 mega popularnych melodii**, które możesz wygenerować jako pliki WAV i używać w swoich projektach!

## 📋 Lista Dostępnych Melodii

| Emoji | Nazwa | Opis | Typ |
|-------|--------|------|-----|
| 🎮 | `tetris` | Tetris Theme (Korobeiniki) | MEGA VIRAL! |
| 📱 | `nokia` | Nokia Ringtone | Nostalgiczny HIT! |
| 🎬 | `imperial_march` | Imperial March (Star Wars) | Epicki! |
| 🍄 | `mario` | Super Mario Bros | Legendarny! |
| 🎂 | `happy_birthday` | Happy Birthday | Klasyk! |
| ⭐ | `twinkle` | Twinkle Twinkle Little Star | Dziecięcy hit! |
| 🎄 | `jingle_bells` | Jingle Bells | Świąteczny hit! |
| 🔔 | `carol_of_the_bells` | Carol of the Bells | Świąteczny klasyk! |
| 🎄 | `deck_the_halls` | Deck the Halls | Radosna kolęda! |
| 🎅 | `we_wish_you` | We Wish You a Merry Christmas | Życzenia! |
| 🕵️ | `mission_impossible` | Mission Impossible | Szpiegowski hit! |
| 🐾 | `pink_panther` | Pink Panther | Jazzowy hit! |
| 🎼 | `fur_elise` | Für Elise (Beethoven) | Klasyczny hit! |
| 💍 | `canon_in_d` | Canon in D (Pachelbel) | Ślubny hit! |
| 🎸 | `smoke_on_water` | Smoke on the Water | Rockowy hit! |
| 🕺 | `staying_alive` | Staying Alive (Bee Gees) | Disco hit! |
| 🎺 | `saints` | When the Saints Go Marching In | Jazzowy standard! |
| 💖 | `titanic` | My Heart Will Go On (Titanic) | Romantyczny hit! |
| 👻 | `ghost_intro` | Oryginalny ghost intro | Pierwotny |

## 🚀 Szybki Start

### 1. Zobacz wszystkie dostępne melodie
```bash
cd mido/
make list-melodies
```

### 2. Wygeneruj konkretną melodię
```bash
# Tetris Theme - MEGA VIRAL!
make generate-melody MELODY=tetris

# Nokia Ringtone - Nostalgiczny!
make generate-melody MELODY=nokia

# Star Wars Imperial March - Epicki!
make generate-melody MELODY=imperial_march
```

### 3. Wygeneruj TOP 4 viralne hity na raz
```bash
make viral-hits
```
*Generuje: Tetris, Nokia, Mario, Imperial March*

### 4. Odtwórz melodię
```bash
# Automatycznie wygeneruje jeśli nie istnieje
make play-melody MELODY=tetris
```

### 5. Wygeneruj wszystkie melodie
```bash
make generate
```

## 🎯 Użycie w Projektach

### Pliki WAV
Po wygenerowaniu, każda melodia zostanie zapisana w folderze:
```
mido/melodies/nazwa_melodii/
├── 1.wav
├── 2.wav
├── 3.wav
└── ...
```

### Programowe użycie
```python
from mido import quick_generate, quick_play

# Wygeneruj melodię
quick_generate("tetris")

# Odtwórz melodię
quick_play("nokia")
```

## 🎨 Dostosowanie

### Zmiana parametrów generacji
W `mido/config.py`:
```python
# Szybsze/wolniejsze tempo
DEFAULT_NOTE_DURATION = 0.3  # Szybsze
DEFAULT_NOTE_DURATION = 0.8  # Wolniejsze

# Inne tempo
DEFAULT_BPM = 140  # Szybsze
DEFAULT_BPM = 80   # Wolniejsze

# Inna głośność
DEFAULT_VELOCITY = 127  # Maksymalna
DEFAULT_VELOCITY = 60   # Cichsze
```

### Dodanie własnej melodii
W `mido/config.py` dodaj do słownika `MELODIES`:
```python
'moja_melodia': [
    'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C'
],
```

## 🎪 Rekomendacje Użycia

### 🔥 Dla viralowości:
1. **tetris** - Rozpoznawalny przez każdego gracza
2. **nokia** - Nostalgia lat 2000
3. **mario** - Ikona gier wideo
4. **imperial_march** - Potęga Star Wars

### 🎭 Dla różnych okazji:
- **Urodziny**: `happy_birthday`
- **Boże Narodzenie**: `jingle_bells`, `carol_of_the_bells`, `deck_the_halls`, `we_wish_you`
- **Wesela**: `canon_in_d`
- **Romantyczne**: `titanic`
- **Dziecięce**: `twinkle`
- **Rockowe**: `smoke_on_water`
- **Disco**: `staying_alive`

### 🎮 Dla gier:
- **Akcja**: `mission_impossible`, `imperial_march`
- **Retro**: `tetris`, `mario`, `nokia`
- **Relaks**: `twinkle`, `canon_in_d`
- **Horror**: `pink_panther` (przewrotnie!)

## 💡 Pro Tips

1. **Łącz melodie** - użyj kilku różnych dla różnych zdarzeń w grze
2. **Dostosuj tempo** - zmień `DEFAULT_BPM` dla konkretnego stylu
3. **Użyj w pętli** - każda melodia to sekwencja, którą można zapętlić
4. **Eksperymentuj** - spróbuj różnych instrumentów w `DEFAULT_INSTRUMENT`

## 🎵 Enjoy Your Viral Melodies!
