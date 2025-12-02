"""
Konfiguracja modułu MIDO Sound Generator.
"""

import os
from pathlib import Path
from typing import Optional


class MidoConfig:
    """Centralna konfiguracja modułu MIDO."""

    # Automatyczne wykrywanie SoundFont
    POSSIBLE_SOUNDFONT_PATHS = [
        "/usr/share/soundfonts/FluidR3_GM.sf2",
        "/usr/share/soundfonts/default.sf2",
        "/usr/share/soundfonts/GeneralUser_GS_1.471.sf2",
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        Path.home() / ".soundfonts" / "FluidR3_GM.sf2",
    ]

    # Parametry generacji MIDI
    DEFAULT_NOTE_DURATION = 0.4  # Krótsze nuty - bez zbędnej ciszy!
    DEFAULT_BPM = 120
    DEFAULT_VELOCITY = 100  # 0-127
    DEFAULT_INSTRUMENT = 0  # Piano

    # Struktura folderów
    OUTPUT_FOLDER = "melodies"

    # Parametry audio
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_BUFFER_SIZE = 512

    # Parametry odtwarzania
    DEFAULT_CHORD_INTERVAL_MS = 500
    DEFAULT_LOOP_COUNT = 4
    PYGAME_WINDOW_SIZE = (200, 200)

    @classmethod
    def find_soundfont(cls) -> Optional[str]:
        """
        Wyszukuje dostępny SoundFont w systemie.

        Returns:
            str: Ścieżka do znalezionego SoundFont lub None
        """
        for path in cls.POSSIBLE_SOUNDFONT_PATHS:
            path_str = str(path)
            if os.path.exists(path_str):
                return path_str
        return None

    @classmethod
    def get_soundfont_path(cls) -> str:
        """
        Pobiera ścieżkę do SoundFont z automatycznym wykrywaniem.

        Returns:
            str: Ścieżka do SoundFont

        Raises:
            FileNotFoundError: Gdy SoundFont nie zostanie znaleziony
        """
        path = cls.find_soundfont()
        if path is None:
            raise FileNotFoundError(
                "SoundFont nie został znaleziony. Zainstaluj fluid-soundfont-gm:\n"
                "  Fedora: sudo dnf install fluid-soundfont-gm\n"
                "  Ubuntu: sudo apt install fluid-soundfont-gm"
            )
        return path

    @classmethod
    def validate_config(cls) -> bool:
        """
        Sprawdza poprawność konfiguracji.

        Returns:
            bool: True jeśli konfiguracja jest poprawna
        """
        try:
            # Sprawdź SoundFont
            cls.get_soundfont_path()

            # Sprawdź zakres parametrów
            assert 0 < cls.DEFAULT_NOTE_DURATION <= 10, "Nieprawidłowa długość nuty"
            assert 60 <= cls.DEFAULT_BPM <= 200, "Nieprawidłowe BPM"
            assert 0 <= cls.DEFAULT_VELOCITY <= 127, "Nieprawidłowa głośność"
            assert 0 <= cls.DEFAULT_INSTRUMENT <= 127, "Nieprawidłowy instrument"

            return True
        except (AssertionError, FileNotFoundError):
            return False


# Mapowanie klawiszy pianina na numery MIDI w tonacji C4
NOTE_MAPPING = {
    "C": 60,  # C4
    "C#": 61,  # C#4/Db4
    "Db": 61,
    "D": 62,  # D4
    "D#": 63,  # D#4/Eb4
    "Eb": 63,
    "E": 64,  # E4
    "F": 65,  # F4
    "F#": 66,  # F#4/Gb4
    "Gb": 66,
    "G": 67,  # G4
    "G#": 68,  # G#4/Ab4
    "Ab": 68,
    "A": 69,  # A4
    "A#": 70,  # A#4/Bb4
    "Bb": 70,  # Bb4 (same as A#)
    "Bb3": 58,  # Bb3 - niższa oktawa dla basów!
    "B": 71,  # B4
}

# Specjalne instrumenty dla konkretnych melodii - NATURALNE BRZMIENIA! 🎵
MELODY_INSTRUMENTS = {
    "imperial_march": 61,  # 🎺 Brass Section - ZŁOWIESZCZOŚĆ!
    "ghost_intro": 18,  # 👻 Rock Organ - Vintage keyboard vibe!
    "mario": 11,  # 🍄 Music Box - Dziecięcy, zabawkowy ale organiczny!
    "nokia": 80,  # 📱 Lead 1 (square) - Nostalgiczny elektroniczny!
    "tetris": 80,  # 🎮 Lead 1 (square) - Retro gaming!
    "jingle_bells": 14,  # 🎄 Tubular Bells - Świąteczny vibe!
    # happy_birthday używa DEFAULT_INSTRUMENT (Piano)
}

# Specjalne długości nut dla konkretnych melodii - AUTENTYCZNY RYTM! 🎵
MELODY_DURATIONS = {
    "imperial_march": [
        # G G G Eb Bb G Eb Bb G (pierwsza część)
        0.8,
        0.8,
        0.8,
        0.3,
        0.5,
        0.8,
        0.3,
        0.5,
        1.2,  # Długie G na początku i końcu
        # D D D Eb Bb F# Eb Bb G (druga część)
        0.8,
        0.8,
        0.8,
        0.3,
        0.5,
        0.6,
        0.3,
        0.5,
        1.2,  # Podobny wzorzec
    ],
    "mario": [
        # Pierwsza część - główny motyw (7 nut)
        0.15,
        0.15,
        0.25,  # E E E (krótkie staccato)
        0.15,  # C
        0.25,  # E
        0.5,  # G (akcent!)
        0.8,  # G niska (długa pauza)
        # Druga część - C G E A B Bb A (7 nut)
        0.5,  # C
        0.4,  # G
        0.4,  # E
        0.3,  # A
        0.3,  # B
        0.2,  # Bb (półton!)
        0.5,  # A
        # Trzecia część - melodia G E G A F G E C D B (10 nut)
        0.3,  # G
        0.3,  # E
        0.3,  # G
        0.4,  # A
        0.3,  # F
        0.3,  # G
        0.3,  # E
        0.3,  # C
        0.3,  # D
        0.5,  # B
        # Czwarta część - powtórzenie C G E A B Bb A (7 nut)
        0.5,  # C
        0.4,  # G
        0.4,  # E
        0.3,  # A
        0.3,  # B
        0.2,  # Bb
        0.5,  # A
        # Piąta część - zakończenie G E G A F G E C D B (10 nut)
        0.3,  # G
        0.3,  # E
        0.3,  # G
        0.4,  # A
        0.3,  # F
        0.3,  # G
        0.3,  # E
        0.3,  # C
        0.3,  # D
        0.6,  # B (długie zakończenie!)
    ],
    "ghost_intro": [
        # Funk'owy bassline lat 80. - rytmiczny groove!
        0.3,
        0.3,
        0.4,
        0.3,
        0.35,
        0.5,  # C C E C D Bb (główny motyw)
        0.3,
        0.3,
        0.3,
        0.3,
        0.4,
        0.3,  # C C C C Bb C (powtórzenie)
        0.3,
        0.3,
        0.4,
        0.3,
        0.35,
        0.5,  # C C E C D Bb
        0.3,
        0.3,
        0.3,
        0.3,
        0.4,
        0.35,
        0.5,  # C C C C Bb D C (zakończenie)
    ],
    # Inne melodie używają DEFAULT_NOTE_DURATION
}

# Definicje melodii - TYLKO NAJLEPSZE! 🎵
MELODIES = {
    # 👻 GHOSTBUSTERS INTRO - Funky lat 80!
    "ghost_intro": [
        "C",
        "C",
        "E",
        "C",
        "D",
        "Bb3",  # Niższa oktawa dla basu!
        "C",
        "C",
        "C",
        "C",
        "Bb3",  # Niższa oktawa dla basu!
        "C",
        "C",
        "C",
        "E",
        "C",
        "D",
        "Bb3",  # Niższa oktawa dla basu!
        "C",
        "C",
        "C",
        "C",
        "Bb3",  # Niższa oktawa dla basu!
        "D",
        "C",
    ],
    # 🎬 IMPERIAL MARCH (Star Wars) - Epicki!
    "imperial_march": [
        "G",
        "G",
        "G",
        "Eb",
        "Bb",
        "G",
        "Eb",
        "Bb",
        "G",
        "D",
        "D",
        "D",
        "Eb",
        "Bb",
        "F#",
        "Eb",
        "Bb",
        "G",
    ],
    # 🍄 SUPER MARIO BROS - Legendarny!
    "mario": [
        # Pierwsza część - główny motyw (kultowe intro!)
        "E",
        "E",
        "E",
        "C",
        "E",
        "G",  # E E E C E G
        "G",  # Niska G (pauza/przestrzeń)
        # Druga część
        "C",
        "G",
        "E",  # C G E
        "A",
        "B",
        "Bb",
        "A",  # A B Bb A
        # Trzecia część - melodia kontynuacja
        "G",
        "E",
        "G",
        "A",
        "F",
        "G",  # G E G A F G
        "E",
        "C",
        "D",
        "B",  # E C D B
        # Czwarta część - rozwinięcie
        "C",
        "G",
        "E",  # C G E (powtórzenie motywu)
        "A",
        "B",
        "Bb",
        "A",  # A B Bb A
        "G",
        "E",
        "G",
        "A",
        "F",
        "G",  # G E G A F G
        "E",
        "C",
        "D",
        "B",  # E C D B (zakończenie)
    ],
    # 📱 NOKIA RINGTONE - Nostalgiczny mega hit!
    "nokia": [
        "E", "D", "F#", "G#",
        "C#", "B", "D", "E",
        "B", "A", "C#", "E",
        "A"
    ],
    # 🎮 TETRIS (Korobeiniki) - Gaming klasyk!
    "tetris": [
        "E", "B", "C", "D",
        "C", "B", "A",
        "A", "C", "E",
        "D", "C", "B",
        "B", "C", "D",
        "E", "C", "A", "A"
    ],
    # 🎂 HAPPY BIRTHDAY - Uniwersalny hit!
    "happy_birthday": [
        "C", "C", "D", "C", "F", "E",
        "C", "C", "D", "C", "G", "F",
        "C", "C", "C", "A", "F", "E", "D",
        "Bb", "Bb", "A", "F", "G", "F"
    ],
    # 🎄 JINGLE BELLS - Świąteczny energiczny!
    "jingle_bells": [
        "E", "E", "E",
        "E", "E", "E",
        "E", "G", "C", "D", "E",
        "F", "F", "F", "F",
        "F", "E", "E", "E",
        "D", "D", "E", "D", "G"
    ],
    # ⭐ TWINKLE TWINKLE LITTLE STAR - Dziecięcy hit!
    "twinkle": [
        "C",
        "C",
        "G",
        "G",
        "A",
        "A",
        "G",
        "F",
        "F",
        "E",
        "E",
        "D",
        "D",
        "C",
        "G",
        "G",
        "F",
        "F",
        "E",
        "E",
        "D",
        "G",
        "G",
        "F",
        "F",
        "E",
        "E",
        "D",
    ],
}
