"""
Moduł obsługi audio dla MIDO Sound Generator.

Klasy do ładowania i odtwarzania dźwięków w grze.
"""

import os
from pathlib import Path
from typing import Optional

import pygame  # type: ignore

try:
    # Try relative imports first (when used as module)
    from .config import MidoConfig  # type: ignore[no-redef]
    from .logger import logger  # type: ignore[no-redef]
except ImportError:
    # Fall back to absolute imports (when used as script)
    from config import MidoConfig  # type: ignore[no-redef]
    from logger import logger  # type: ignore[no-redef]


def load_chords(folder_path: str) -> list[pygame.mixer.Sound]:
    """
    Ładuje wszystkie pliki WAV z danego folderu, sortowane numerycznie.
    Zakłada, że pliki są nazwane jako '1.wav', '2.wav', ..., 'N.wav'.

    Args:
        folder_path: Ścieżka do folderu z akordami

    Returns:
        Lista obiektów pygame.mixer.Sound

    Raises:
        ValueError: Gdy pliki nie są nazwane numerycznie
        FileNotFoundError: Gdy folder nie istnieje
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder {folder_path} nie istnieje")

    logger.audio_load_start(folder_path)

    # Pobierz wszystkie pliki WAV
    chord_files = [f for f in os.listdir(folder_path) if f.endswith(".wav")]

    if not chord_files:
        logger.warning(f"Brak plików WAV w folderze {folder_path}")
        return []

    # Sortuj pliki numerycznie na podstawie nazwy pliku (np. '1.wav', '2.wav', ...)
    try:
        chord_files_sorted = sorted(
            chord_files, key=lambda x: int(os.path.splitext(x)[0])
        )
    except ValueError as e:
        raise ValueError(
            "Wszystkie pliki w folderze muszą być nazwane numerycznie, "
            "np. '1.wav', '2.wav', itd."
        ) from e

    # Załaduj pliki WAV jako obiekty pygame.mixer.Sound
    chords = []
    failed_count = 0

    for file in chord_files_sorted:
        path = os.path.join(folder_path, file)
        try:
            sound = pygame.mixer.Sound(path)
            chords.append(sound)
            logger.debug(f"Załadowano: {path}")
        except pygame.error as e:
            logger.error(f"Nie można załadować pliku {path}", e)
            failed_count += 1

    success_count = len(chords)
    logger.audio_load_complete(success_count)

    if failed_count > 0:
        logger.warning(f"Błędy ładowania: {failed_count} plików")

    return chords


class ChordPlayer:
    """
    Klasa zarządzająca odtwarzaniem akordów w pętli.
    """

    def __init__(self, chords: list[pygame.mixer.Sound]):
        """
        Inicjalizuje ChordPlayer z listą akordów.

        Args:
            chords: Lista obiektów pygame.mixer.Sound
        """
        self.chords = chords
        self.current_index = 0
        self.total = len(chords)
        self.config = MidoConfig()

        if self.total == 0:
            logger.warning("ChordPlayer zainicjalizowany z pustą listą akordów")

    def play_next_chord(self) -> bool:
        """
        Odtwarza kolejny akord z listy i inkrementuje indeks.
        Jeśli osiągnie koniec listy, wraca do początku.

        Returns:
            bool: True jeśli akord został odtworzony
        """
        if self.total == 0:
            logger.warning("Brak akordów do odtworzenia")
            return False

        try:
            current_chord = self.chords[self.current_index]
            current_chord.play()

            logger.debug(f"Odtwarzam akord {self.current_index + 1}/{self.total}")

            self.current_index = (self.current_index + 1) % self.total
            return True

        except (pygame.error, IndexError) as e:
            logger.error(f"Błąd odtwarzania akordu {self.current_index}", e)
            return False

    def play_chord_by_index(self, index: int) -> bool:
        """
        Odtwarza konkretny akord według indeksu.

        Args:
            index: Indeks akordu do odtworzenia (0-based)

        Returns:
            bool: True jeśli akord został odtworzony
        """
        if not 0 <= index < self.total:
            logger.error(
                f"Nieprawidłowy indeks akordu: {index} (dostępne: 0-{self.total-1})"
            )
            return False

        try:
            chord = self.chords[index]
            chord.play()
            logger.debug(f"Odtwarzam akord {index + 1}")
            return True
        except pygame.error as e:
            logger.error(f"Błąd odtwarzania akordu {index}", e)
            return False

    def get_chord_count(self) -> int:
        """
        Zwraca liczbę dostępnych akordów.

        Returns:
            int: Liczba akordów
        """
        return self.total

    def reset_position(self) -> None:
        """Resetuje pozycję odtwarzania do początku."""
        self.current_index = 0
        logger.debug("Pozycja odtwarzania zresetowana")

    def get_current_position(self) -> int:
        """
        Zwraca aktualną pozycję odtwarzania.

        Returns:
            int: Indeks aktualnego akordu
        """
        return self.current_index


class MidoAudioManager:
    """
    Menedżer audio dla modułu MIDO - integracja z systemem audio gry.
    """

    def __init__(self) -> None:
        """Inicjalizuje menedżer audio MIDO."""
        self.config = MidoConfig()
        self.players: dict[str, ChordPlayer] = {}
        self.initialized = False

    def initialize_pygame_mixer(self) -> bool:
        """
        Inicjalizuje pygame mixer z optymalną konfiguracją.

        Returns:
            bool: True jeśli inicjalizacja się powiodła
        """
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=self.config.AUDIO_SAMPLE_RATE,
                    size=-16,  # 16-bit signed
                    channels=2,  # Stereo
                    buffer=self.config.AUDIO_BUFFER_SIZE,
                )
                logger.debug("Pygame mixer zainicjalizowany")

            self.initialized = True
            return True

        except pygame.error as e:
            logger.error("Błąd inicjalizacji pygame mixer", e)
            return False

    def load_melody_set(
        self, melody_name: str, folder_path: Optional[str] = None
    ) -> bool:
        """
        Ładuje zestaw melodii do menedżera.

        Args:
            melody_name: Nazwa melodii
            folder_path: Ścieżka do folderu (auto-wykrywanie jeśli None)

        Returns:
            bool: True jeśli ładowanie się powiodło
        """
        if not self.initialized:
            self.initialize_pygame_mixer()

        if folder_path is None:
            folder_path = os.path.join(self.config.OUTPUT_FOLDER, melody_name)

        try:
            chords = load_chords(folder_path)
            if chords:
                self.players[melody_name] = ChordPlayer(chords)
                logger.debug(
                    f"Załadowano melodię '{melody_name}' z {len(chords)} akordami"
                )
                return True
            else:
                logger.warning(f"Brak akordów w melodii '{melody_name}'")
                return False

        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Błąd ładowania melodii '{melody_name}'", e)
            return False

    def get_player(self, melody_name: str) -> Optional[ChordPlayer]:
        """
        Pobiera player dla konkretnej melodii.

        Args:
            melody_name: Nazwa melodii

        Returns:
            ChordPlayer lub None jeśli nie znaleziono
        """
        return self.players.get(melody_name)

    def play_melody_chord(
        self, melody_name: str, chord_index: Optional[int] = None
    ) -> bool:
        """
        Odtwarza akord z konkretnej melodii.

        Args:
            melody_name: Nazwa melodii
            chord_index: Indeks akordu (None = następny w kolejności)

        Returns:
            bool: True jeśli odtworzenie się powiodło
        """
        player = self.get_player(melody_name)
        if player is None:
            logger.warning(f"Melodia '{melody_name}' nie jest załadowana")
            return False

        if chord_index is not None:
            return player.play_chord_by_index(chord_index)
        else:
            return player.play_next_chord()

    def cleanup(self) -> None:
        """Czyści zasoby menedżera audio."""
        self.players.clear()
        if self.initialized and pygame.mixer.get_init():
            pygame.mixer.quit()
            logger.debug("Menedżer audio MIDO wyczyszczony")


def main() -> None:
    """
    Główna funkcja do odtwarzania melodii z wiersza poleceń.

    Użycie: python audio.py <nazwa_melodii>
    """
    import sys
    import time

    if len(sys.argv) != 2:
        print("❌ Użycie: python audio.py <nazwa_melodii>")
        print("📁 Dostępne melodie:")
        try:
            from config import MELODIES

            for melody in sorted(MELODIES.keys()):
                note_count = len(MELODIES[melody])
                print(f"   🎵 {melody} ({note_count} nut)")
        except ImportError:
            print("   (nie można załadować listy melodii)")
        return

    melody_name = sys.argv[1]

    # Sprawdź czy melodia istnieje
    try:
        from config import MELODIES

        if melody_name not in MELODIES:
            print(f"❌ Melodia '{melody_name}' nie istnieje!")
            print("📁 Dostępne melodie:")
            for melody in sorted(MELODIES.keys()):
                note_count = len(MELODIES[melody])
                print(f"   🎵 {melody} ({note_count} nut)")
            return

        note_count = len(MELODIES[melody_name])
        melody_notes = " → ".join(MELODIES[melody_name])

    except ImportError:
        print("❌ Nie można załadować konfiguracji melodii!")
        return

    # Inicjalizuj pygame i audio manager
    print(f"🎵 Ładowanie melodii: {melody_name} ({note_count} nut)")
    print(f"🎼 Nuty: {melody_notes}")

    try:
        # Inicjalizuj pygame z oknem (potrzebne dla audio)
        pygame.init()
        pygame.display.set_mode((200, 200))  # Małe okno
        pygame.display.set_caption(f"MIDO - {melody_name}")

        audio_manager = MidoAudioManager()

        if not audio_manager.initialize_pygame_mixer():
            print("❌ Błąd inicjalizacji audio!")
            return

        # Załaduj melodię
        if not audio_manager.load_melody_set(melody_name):
            print(f"❌ Nie można załadować melodii '{melody_name}'!")
            return

        player = audio_manager.get_player(melody_name)
        if not player:
            print(f"❌ Nie można utworzyć playera dla '{melody_name}'!")
            return

        print("✅ Melodia załadowana! Rozpoczynam odtwarzanie...")
        print(
            f"🔄 Grając w pętli {MidoConfig.DEFAULT_LOOP_COUNT}x "
            f"z interwałem {MidoConfig.DEFAULT_CHORD_INTERVAL_MS}ms"
        )

        # Odtwarzaj melodię w pętli
        total_chords = player.get_chord_count()
        loop_count = MidoConfig.DEFAULT_LOOP_COUNT
        interval_seconds = MidoConfig.DEFAULT_CHORD_INTERVAL_MS / 1000.0

        for loop in range(loop_count):
            print(f"🎵 Pętla {loop + 1}/{loop_count}")

            for chord_idx in range(total_chords):
                # Odtwórz akord
                success = player.play_chord_by_index(chord_idx)
                if success:
                    current_note = MELODIES[melody_name][chord_idx]
                    print(f"   🎶 {chord_idx + 1:2d}/{total_chords} - {current_note}")
                else:
                    print(f"   ❌ Błąd odtwarzania akordu {chord_idx + 1}")

                # Czekaj na następny akord
                time.sleep(interval_seconds)

            # Przerwa między pętlami
            if loop < loop_count - 1:
                print("   ⏳ Przerwa między pętlami...")
                time.sleep(0.5)

        print(f"✅ Melodia '{melody_name}' zakończona!")

        # Cleanup
        audio_manager.cleanup()
        pygame.quit()

    except KeyboardInterrupt:
        print("\n⏹️  Odtwarzanie przerwane przez użytkownika")
        try:
            audio_manager.cleanup()
            pygame.quit()
        except Exception:
            pass
    except Exception as e:
        print(f"❌ Błąd odtwarzania: {e}")
        try:
            audio_manager.cleanup()
            pygame.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
