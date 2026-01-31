"""
Główny player melodii dla modułu MIDO Sound Generator.

Standalone aplikacja do testowania wygenerowanych melodii.
"""

from typing import Optional

import pygame  # type: ignore

try:
    # Try relative imports first (when used as module)
    from .audio import ChordPlayer, MidoAudioManager  # type: ignore[no-redef]
    from .config import MidoConfig  # type: ignore[no-redef]
    from .logger import logger  # type: ignore[no-redef]
except ImportError:
    # Fall back to absolute imports (when used as script)
    from audio import ChordPlayer, MidoAudioManager  # type: ignore[no-redef]
    from config import MidoConfig  # type: ignore[no-redef]
    from logger import logger  # type: ignore[no-redef]


class MelodyPlayer:
    """
    Główny player melodii MIDO z interfejsem graficznym.
    """

    def __init__(self, melody_name: str = "ghost_intro"):
        """
        Inicjalizuje player melodii.

        Args:
            melody_name: Nazwa melodii do odtworzenia
        """
        self.config = MidoConfig()
        self.melody_name = melody_name
        self.audio_manager = MidoAudioManager()
        self.player: Optional[ChordPlayer] = None
        self.screen: Optional[pygame.Surface] = None
        self.clock = pygame.time.Clock()

        # Parametry odtwarzania
        self.current_loop = 0
        self.max_loops = self.config.DEFAULT_LOOP_COUNT
        self.chord_interval_ms = self.config.DEFAULT_CHORD_INTERVAL_MS
        self.chord_play_event = pygame.USEREVENT + 1

        self.running = False

    def initialize(self) -> bool:
        """
        Inicjalizuje pygame i ładuje melodię.

        Returns:
            bool: True jeśli inicjalizacja się powiodła
        """
        try:
            # Inicjalizuj pygame
            pygame.init()

            # Inicjalizuj menedżer audio
            if not self.audio_manager.initialize_pygame_mixer():
                return False

            # Utwórz okno (minimalne, potrzebne dla pętli pygame)
            window_size = self.config.PYGAME_WINDOW_SIZE
            self.screen = pygame.display.set_mode(window_size)
            pygame.display.set_caption(f"MIDO Player - {self.melody_name}")

            # Załaduj melodię
            melody_folder = f"melodies/{self.melody_name}"
            if not self.audio_manager.load_melody_set(self.melody_name, melody_folder):
                logger.error(f"Nie można załadować melodii '{self.melody_name}'")
                return False

            self.player = self.audio_manager.get_player(self.melody_name)
            if self.player is None:
                logger.error("Błąd inicjalizacji playera")
                return False

            # Skonfiguruj timer
            pygame.time.set_timer(self.chord_play_event, self.chord_interval_ms)

            chord_count = self.player.get_chord_count()
            logger.playback_start(chord_count, self.max_loops)

            return True

        except Exception as e:
            logger.error("Błąd inicjalizacji playera", e)
            return False

    def handle_events(self) -> bool:
        """
        Obsługuje wydarzenia pygame.

        Returns:
            bool: True jeśli aplikacja powinna kontynuować
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.debug("Zamykanie aplikacji przez użytkownika")
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.debug("Zamykanie aplikacji przez ESC")
                    return False
                elif event.key == pygame.K_SPACE:
                    logger.debug("Pauza/restart przez spację")
                    self.restart_playback()
                elif event.key == pygame.K_RIGHT:
                    logger.debug("Przyspieszenie odtwarzania")
                    self.change_tempo(0.8)  # Szybciej
                elif event.key == pygame.K_LEFT:
                    logger.debug("Spowolnienie odtwarzania")
                    self.change_tempo(1.2)  # Wolniej

            elif event.type == self.chord_play_event:
                if not self.play_next_chord():
                    logger.playback_complete()
                    return False

        return True

    def play_next_chord(self) -> bool:
        """
        Odtwarza kolejny akord i zarządza pętlami.

        Returns:
            bool: True jeśli odtwarzanie powinno kontynuować
        """
        if self.player is None:
            return False

        # Sprawdź limit pętli
        if self.current_loop >= self.max_loops:
            return False

        # Odtwórz akord
        current_pos = self.player.get_current_position()
        total_chords = self.player.get_chord_count()

        success = self.player.play_next_chord()
        if not success:
            return False

        logger.playback_chord(current_pos, self.current_loop + 1, self.max_loops)

        # Sprawdź czy skończyła się sekwencja
        new_pos = self.player.get_current_position()
        if new_pos == 0 and current_pos == total_chords - 1:
            # Zakończono pełną pętlę
            self.current_loop += 1
            logger.debug(f"Zakończono pętlę {self.current_loop}/{self.max_loops}")

        return True

    def restart_playback(self) -> None:
        """Restartuje odtwarzanie od początku."""
        if self.player:
            self.player.reset_position()
            self.current_loop = 0
            logger.debug("Odtwarzanie zrestartowane")

    def change_tempo(self, factor: float) -> None:
        """
        Zmienia tempo odtwarzania.

        Args:
            factor: Mnożnik tempa (>1 = wolniej, <1 = szybciej)
        """
        new_interval = int(self.chord_interval_ms * factor)
        new_interval = max(100, min(2000, new_interval))  # Ograniczenia

        if new_interval != self.chord_interval_ms:
            self.chord_interval_ms = new_interval
            pygame.time.set_timer(self.chord_play_event, self.chord_interval_ms)
            logger.debug(f"Tempo zmienione na {self.chord_interval_ms}ms")

    def render(self) -> None:
        """Renderuje prostą wizualizację."""
        if self.screen is None:
            return

        # Czyść ekran
        self.screen.fill((20, 20, 40))  # Ciemny niebieski

        # Proste info
        if self.player:
            current_pos = self.player.get_current_position()
            total = self.player.get_chord_count()
            progress = current_pos / max(1, total)

            # Pasek postępu
            bar_width = 180
            bar_height = 20
            bar_x = 10
            bar_y = 10

            # Tło paska
            pygame.draw.rect(
                self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height)
            )

            # Postęp
            progress_width = int(bar_width * progress)
            pygame.draw.rect(
                self.screen, (100, 200, 100), (bar_x, bar_y, progress_width, bar_height)
            )

        pygame.display.flip()

    def run(self) -> bool:
        """
        Główna pętla aplikacji.

        Returns:
            bool: True jeśli aplikacja zakończyła się poprawnie
        """
        if not self.initialize():
            return False

        self.running = True

        try:
            while self.running:
                # Obsłuż wydarzenia
                if not self.handle_events():
                    break

                # Renderuj
                self.render()

                # Kontroluj FPS
                self.clock.tick(60)

            logger.playback_complete()
            return True

        except Exception as e:
            logger.error("Błąd w głównej pętli", e)
            return False

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Czyści zasoby aplikacji."""
        if self.audio_manager:
            self.audio_manager.cleanup()

        pygame.quit()
        logger.debug("Player wyczyszczony")


def main() -> None:
    """Główna funkcja uruchamiająca player."""
    try:
        # Sprawdź konfigurację
        if not MidoConfig.validate_config():
            logger.error("Nieprawidłowa konfiguracja modułu MIDO")
            return

        # Uruchom player
        player = MelodyPlayer("ghost_intro")
        success = player.run()

        if success:
            logger.info("🎵 Player zakończony pomyślnie")
        else:
            logger.error("❌ Player zakończony z błędami")

    except KeyboardInterrupt:
        logger.info("🛑 Player przerwany przez użytkownika")
    except Exception as e:
        logger.error("Krytyczny błąd playera", e)
        raise


if __name__ == "__main__":
    main()
