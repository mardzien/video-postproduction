"""
System logowania dla modułu MIDO Sound Generator.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class MidoLogger:
    """Specjalizowany logger dla modułu MIDO."""

    def __init__(self, name: str = "MIDO", level: int = logging.INFO):
        """
        Inicjalizuje logger MIDO.

        Args:
            name: Nazwa loggera
            level: Poziom logowania
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Usuń istniejące handlery
        self.logger.handlers.clear()

        # Stwórz kolorowy formatter
        formatter = self._create_formatter()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (opcjonalny)
        self._setup_file_logging()

    def _create_formatter(self) -> logging.Formatter:
        """Tworzy kolorowy formatter dla logów."""

        class ColoredFormatter(logging.Formatter):
            """Formatter z kolorowaniem dla różnych poziomów."""

            COLORS = {
                "DEBUG": "\033[36m",  # Cyan
                "INFO": "\033[32m",  # Green
                "WARNING": "\033[33m",  # Yellow
                "ERROR": "\033[31m",  # Red
                "CRITICAL": "\033[35m",  # Magenta
            }
            RESET = "\033[0m"

            def format(self, record: logging.LogRecord) -> str:
                color = self.COLORS.get(record.levelname, "")
                record.levelname = f"{color}{record.levelname}{self.RESET}"
                return super().format(record)

        return ColoredFormatter("🎵 %(levelname)s [%(name)s] %(message)s")

    def _setup_file_logging(self) -> None:
        """Konfiguruje logowanie do pliku."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_dir / "mido.log")
        file_handler.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def generation_start(self, melody_name: str, note_count: int) -> None:
        """Loguje rozpoczęcie generowania melodii."""
        self.logger.info(
            f"🎼 Rozpoczynam generowanie melodii '{melody_name}' ({note_count} nut)"
        )

    def generation_progress(self, note_index: int, note_name: str, total: int) -> None:
        """Loguje postęp generowania."""
        progress = (note_index + 1) / total * 100
        self.logger.info(
            f"🎵 Generuję nutę {note_index + 1}/{total} ({progress:.1f}%): {note_name}"
        )

    def generation_complete(self, melody_name: str, output_path: str) -> None:
        """Loguje zakończenie generowania."""
        self.logger.info(f"✅ Melodia '{melody_name}' wygenerowana do: {output_path}")

    def soundfont_found(self, path: str) -> None:
        """Loguje znalezienie SoundFont."""
        self.logger.info(f"🔊 SoundFont znaleziony: {path}")

    def soundfont_missing(self) -> None:
        """Loguje brak SoundFont."""
        self.logger.error("❌ SoundFont nie znaleziony! Sprawdź instalację.")

    def audio_load_start(self, folder_path: str) -> None:
        """Loguje rozpoczęcie ładowania audio."""
        self.logger.info(f"📂 Ładuję dźwięki z: {folder_path}")

    def audio_load_complete(self, count: int) -> None:
        """Loguje zakończenie ładowania audio."""
        self.logger.info(f"✅ Załadowano {count} plików audio")

    def playback_start(self, chord_count: int, loops: int) -> None:
        """Loguje rozpoczęcie odtwarzania."""
        self.logger.info(
            f"▶️ Rozpoczynam odtwarzanie {chord_count} akordów ({loops} pętli)"
        )

    def playback_chord(self, index: int, loop: int, total_loops: int) -> None:
        """Loguje odtwarzanie akordu."""
        self.logger.debug(f"🎶 Odtwarzam akord {index} (pętla {loop}/{total_loops})")

    def playback_complete(self) -> None:
        """Loguje zakończenie odtwarzania."""
        self.logger.info("🏁 Odtwarzanie zakończone")

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Loguje błąd."""
        if exception:
            self.logger.error(f"❌ {message}: {exception}")
        else:
            self.logger.error(f"❌ {message}")

    def warning(self, message: str) -> None:
        """Loguje ostrzeżenie."""
        self.logger.warning(f"⚠️ {message}")

    def debug(self, message: str) -> None:
        """Loguje informację debug."""
        self.logger.debug(f"🔧 {message}")

    def info(self, message: str) -> None:
        """Loguje informację ogólną."""
        self.logger.info(message)


# Globalny logger dla modułu
logger = MidoLogger()
