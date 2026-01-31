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
    # Niższa oktawa (3)
    "E3": 52,
    "F#3": 54,
    "G3": 55,
    "G#3": 56,
    "A3": 57,
    "Bb3": 58,
    "B3": 59,
    # Wyższa oktawa (5)
    "C5": 72,
    "C#5": 73, "Db5": 73,
    "D5": 74,
    "D#5": 75, "Eb5": 75,
    "E5": 76,
    "F5": 77,
    "F#5": 78, "Gb5": 78,
    "G5": 79,
    "G#5": 80, "Ab5": 80,
    "A5": 81,
    "A#5": 82, "Bb5": 82,
    "B5": 83,
    # Oktawa 6
    "C6": 84,
    "D6": 86,
}

# Specjalne instrumenty dla konkretnych melodii - NATURALNE BRZMIENIA! 🎵
MELODY_INSTRUMENTS = {
    "imperial_march": 61,  # 🎺 Brass Section - ZŁOWIESZCZOŚĆ!
    "ghost_intro": 18,  # 👻 Rock Organ - Vintage keyboard vibe!
    "mario": 11,  # 🍄 Music Box - Dziecięcy, zabawkowy ale organiczny!
    "nokia": 80,  # 📱 Lead 1 (square) - Nostalgiczny elektroniczny!
    "tetris": 80,  # 🎮 Lead 1 (square) - Retro gaming!
    "tokyo_drift": 81,  # 🏎️ Lead 2 (Sawtooth) - Agresywny synth drift!
    "megalovania": 30,  # 🎸 Overdriven Guitar - Epicka moc!
    "megalovania_piano": 0,  # 🎹 Piano
    "megalovania_music_box": 11,  # 🎵 Music Box
    "megalovania_edm": 81,  # 🎧 Lead 2 (Sawtooth)
    "megalovania_guitar": 30,  # 🎸 Distortion Guitar
    "megalovania_organ": 19,  # 🎹 Church Organ
    "megalovania_violin": 40,  # 🎻 Violin
    "gravity_falls": 78,  # 😗 Whistle - Prawdziwe gwizdanie (78)!
    "jingle_bells": 14,  # 🎄 Tubular Bells - Świąteczny vibe!
    "carol_of_the_bells": 14,  # 🔔 Tubular Bells - Świąteczny klasyk!
    "deck_the_halls": 14,  # 🎄 Tubular Bells - Radosna kolęda!
    "we_wish_you": 14,  # 🎅 Tubular Bells - Życzenia!
    "feliz_navidad": 56,  # 🎺 Trumpet - Latynoski klimat!
    "avicii_levels": 81,  # 🎧 Lead 2 (Sawtooth) - EDM vibe!
    # happy_birthday używa DEFAULT_INSTRUMENT (Piano)
}

# Specjalne długości nut dla konkretnych melodii - AUTENTYCZNY RYTM! 🎵
MELODY_DURATIONS = {
    "avicii_levels": [
        # C# (long) - 1.0s
        1.0, 
        # C# B G# (fast)
        0.2, 0.2, 0.2,
        # F# E F# G# (syncopated)
        0.3, 0.3, 0.3, 0.3,
        # C# (middle long)
        0.8,
        # C# B G# (fast)
        0.2, 0.2, 0.2,
        # F# E (ending)
        0.4, 0.8
    ],
    "carol_of_the_bells": [
        # Ostinato 4x (G#-F#-G#-E) - rytm 3/4 (ćwierć, ósemka, ósemka, ćwierć)
        0.4, 0.2, 0.2, 0.4,
        0.4, 0.2, 0.2, 0.4,
        0.4, 0.2, 0.2, 0.4,
        0.4, 0.2, 0.2, 0.4,
        # Zakończenie (Długie nuty)
        0.8, 0.8, 0.8, 0.8,
        1.2,
    ],
    "deck_the_halls": [
        # C Bb A G F G A F (Deck the halls)
        0.5, 0.2, 0.35, 0.35, 0.35, 0.2, 0.35, 0.5,
        # G A Bb G A G F E F (Fa la la la la, la la la la)
        0.25, 0.25, 0.35, 0.25, 0.25, 0.25, 0.25, 0.25, 0.8,
    ],
    "jingle_bells": [
        # Pierwsze przejście (klasyczne) - powtarzane frazy
        0.4, 0.4, 0.8, 0.4, 0.4, 0.8,
        0.4, 0.4, 0.4, 0.4, 0.8,
        0.4, 0.4, 0.4, 0.4,
        0.4, 0.4, 0.4, 0.4,
        0.4, 0.4, 0.4, 0.4, 0.6,
        # Drugie przejście
        0.4, 0.4, 0.8, 0.4, 0.4, 0.8,
        0.4, 0.4, 0.4, 0.4, 0.8,
        0.4, 0.4, 0.4, 0.4,
        0.4, 0.4, 0.4, 0.4,
        0.4, 0.4, 0.4, 0.4, 1,
    ],
    "we_wish_you": [
        # G C C D C B A A (We wish you a merry Christmas)
        0.4, 0.4, 0.2, 0.2, 0.4, 0.4, 0.4, 0.4,
        # A D D E D C B G (We wish you a merry Christmas)
        0.4, 0.4, 0.2, 0.2, 0.4, 0.4, 0.4, 0.8,
        # G E E F E D C B (Good tidings we bring)
        0.4, 0.4, 0.2, 0.2, 0.4, 0.4, 0.4, 0.4,
        # G G A D B C (And a happy new year)
        0.4, 0.4, 0.4, 0.4, 0.4, 0.8,
    ],
    "imperial_march": [
        # Pierwsza część - główny motyw (powtórzony 2x)
        0.8, 0.8, 0.8, 0.3, 0.5, 0.8, 0.3, 0.5, 1.2,
        0.8, 0.8, 0.8, 0.3, 0.5, 0.8, 0.3, 0.5, 1.2,
        # Druga część - odpowiedź (powtórzona 2x)
        0.8, 0.8, 0.8, 0.3, 0.5, 0.6, 0.3, 0.5, 1.2,
        0.8, 0.8, 0.8, 0.3, 0.5, 0.6, 0.3, 0.5, 1.2,
        # Kulminacja - powrót głównego motywu
        0.8, 0.8, 0.8, 0.3, 0.5, 0.8, 0.3, 0.5, 2.0,
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
    "tokyo_drift": [
        # 🏎️ Charakterystyczny Teriyaki Boyz riff - agresywny synth!
        # Główny riff (powtórzony 3x dla intensywności)
        0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 0.8,
        0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 0.8,
        0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 0.3, 0.15, 1.2,
        # Build-up z opadaniem
        0.4, 0.2, 0.4, 0.2, 0.4, 0.4, 0.6,
    ],
    "megalovania": [
        # Intro riff: D D D5 A Ab G F D F G
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        # Część 2 (C): C C D5 A Ab G F D F G
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        # Część 3 (B): B B D5 A Ab G F D F G
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        # Część 4 (Bb): Bb Bb D5 A Ab G F D F G
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_piano": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_music_box": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_edm": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_guitar": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_organ": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "megalovania_violin": [
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
        0.15, 0.15, 0.3, 0.45, 0.4, 0.35, 0.35, 0.15, 0.15, 0.15,
    ],
    "gravity_falls": [
        # Phrase 1: D E F A G A C D (szybkie arpeggio w górę)
        0.2, 0.2, 0.2, 0.4, 0.2, 0.2, 0.2, 0.8,
        # Phrase 2: E F E C D (odpowiedź)
        0.2, 0.2, 0.2, 0.2, 1.0,
    ],
    "feliz_navidad": [
        # G C B C A (Fe-liz Na-vi-dad)
        0.2, 0.4, 0.2, 0.2, 0.8,
        # G D C D B (Fe-liz Na-vi-dad)
        0.2, 0.4, 0.2, 0.2, 0.8,
        # G C B C A (Fe-liz Na-vi-dad)
        0.2, 0.4, 0.2, 0.2, 0.8,
        # F F G F E D C (Pros-pe-ro A-ño y Fe-li-ci-dad)
        0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.8,
    ],
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
    # 🎬 IMPERIAL MARCH (Star Wars) - Epicki i rozszerzony!
    "imperial_march": [
        # Pierwsza część - główny motyw (powtórzony 2x)
        "G", "G", "G", "Eb", "Bb", "G", "Eb", "Bb", "G",
        "G", "G", "G", "Eb", "Bb", "G", "Eb", "Bb", "G",
        # Druga część - odpowiedź (powtórzona 2x)
        "D", "D", "D", "Eb", "Bb", "F#", "Eb", "Bb", "G",
        "D", "D", "D", "Eb", "Bb", "F#", "Eb", "Bb", "G",
        # Kulminacja - powrót głównego motywu z wyższą dynamiką
        "G", "G", "G", "Eb", "Bb", "G", "Eb", "Bb", "G",
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
        "D", "D", "E", "D", "G",
        "E", "E", "E",
        "E", "E", "E",
        "E", "G", "C", "D", "E", 
        "F", "F", "F", "F",
        "F", "E", "E", "E",
        "G", "G", "F", "D", "C",
    ],
    # 🔔 CAROL OF THE BELLS (Shchedryk) - Wersja 5. oktawa (dzwonkowa)
    "carol_of_the_bells": [
        # Ostinato 4x (charakterystyczny motyw opadający)
        "G#5", "F#5", "G#5", "E5",
        "G#5", "F#5", "G#5", "E5",
        "G#5", "F#5", "G#5", "E5",
        "G#5", "F#5", "G#5", "E5",
        # Rozwinięcie proste (Ding Dong)
        "B5", "G#5", "B5", "G#5",
        # Zakończenie
        "E5",
    ],
    # 🎄 DECK THE HALLS - Kompletna fraza w F-dur (17 nut)
    "deck_the_halls": [
        # C Bb A G F G A F (Deck the halls with boughs of holly)
        "C5", "Bb", "A", "G", "F", "G", "A", "F",
        # G A Bb G A G F E F (Fa la la la la, la la la la)
        "G", "A", "Bb", "G", "A", "G", "F", "E", "F"
    ],
    # 🎅 WE WISH YOU A MERRY CHRISTMAS - Poprawiona melodia
    "we_wish_you": [
        # G C C D C B A A (We wish you a merry Christmas)
        "G", "C5", "C5", "D5", "C5", "B", "A", "A",
        # A D D E D C B G (We wish you a merry Christmas)
        "A", "D5", "D5", "E5", "D5", "C5", "B", "G",
        # G E E F E D C B (Good tidings we bring)
        "G", "E5", "E5", "F5", "E5", "D5", "C5", "B",
        # G G A D B C (And a happy new year)
        "G", "G", "A", "D5", "B", "C5"
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
    # 🏎️ TOKYO DRIFT - Oryginalny Teriyaki Boyz riff!
    "tokyo_drift": [
        # Główny riff - agresywny synth (powtórzony 3x)
        "F#", "F#", "F#", "F#", "F#", "F#", "F#", "F#", "D",
        "F#", "F#", "F#", "F#", "F#", "F#", "F#", "F#", "D",
        "F#", "F#", "F#", "F#", "F#", "F#", "F#", "F#", "D",
        # Build-up z opadaniem - charakterystyczne zakończenie
        "B", "Bb", "Ab", "Gb", "F#", "Eb", "D",
    ],
    # 💀 MEGALOVANIA (Undertale) - Pełny cykl 4-taktowy!
    "megalovania": [
        # Część 1 (D)
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        # Część 2 (C)
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        # Część 3 (B)
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        # Część 4 (Bb)
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_piano": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_music_box": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_edm": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_guitar": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_organ": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    "megalovania_violin": [
        "D", "D", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "C", "C", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "B", "B", "D5", "A", "Ab", "G", "F", "D", "F", "G",
        "Bb", "Bb", "D5", "A", "Ab", "G", "F", "D", "F", "G",
    ],
    # 🌲 GRAVITY FALLS - Główny motyw gwizdany
    "gravity_falls": [
        # Fraza 1 (wznosząca)
        "D5", "E5", "F5", "A5", "G5", "A5", "C6", "D6",
        # Fraza 2 (opadająca)
        "E5", "F5", "E5", "C5", "D5"
    ],
    # 🎄 FELIZ NAVIDAD - Latynoski klasyk!
    "feliz_navidad": [
        # Phrase 1: Fe-liz Na-vi-dad
        "G", "C5", "B", "C5", "A",
        # Phrase 2: Fe-liz Na-vi-dad
        "G", "D5", "C5", "D5", "B",
        # Phrase 3: Fe-liz Na-vi-dad
        "G", "C5", "B", "C5", "A",
        # Phrase 4: Pros-pe-ro A-ño y Fe-li-ci-dad
        "F", "F", "G", "F", "E", "D", "C",
    ],
    # 🎧 AVICII - LEVELS (Classic EDM Hook)
    "avicii_levels": [
        "C#", 
        "C#", "B3", "G#3",
        "F#3", "E3", "F#3", "G#3",
        "C#",
        "C#", "B3", "G#3",
        "F#3", "E3"
    ],
}
