"""
MIDO Sound Generator - Moduł generowania dźwięków MIDI dla Ball Game.

Ten pakiet zawiera narzędzia do:
- Generowania melodii z definicji MIDI
- Konwersji MIDI na pliki WAV
- Integracji z systemem postprodukcji video
"""

__version__ = "2.0.0"
__author__ = "Ball Game Team"

# Główne API modułu - tylko MIDI generation (bez pygame)
from .config import MELODIES, NOTE_MAPPING, MidoConfig
from .generator import MelodyGenerator
from .generator import main as generate_melodies
from .logger import MidoLogger, logger

# Publiczne API
__all__ = [
    # Generacja melodii
    "MelodyGenerator",
    "generate_melodies",
    # Konfiguracja
    "MidoConfig",
    "NOTE_MAPPING",
    "MELODIES",
    # Logowanie
    "logger",
    "MidoLogger",
]


# Quick generation helper
def quick_generate(melody_name: str = "ghost_intro") -> bool:
    """
    Szybka generacja pojedynczej melodii.

    Args:
        melody_name: Nazwa melodii do wygenerowania

    Returns:
        bool: True jeśli generacja się powiodła
    """
    try:
        generator = MelodyGenerator()
        if melody_name in MELODIES:
            return generator.generate_melody(melody_name, MELODIES[melody_name])
        else:
            logger.error(f"Nieznana melodia: {melody_name}")
            return False
    except Exception as e:
        logger.error("Błąd szybkiej generacji", e)
        return False


# Sprawdzenie konfiguracji przy imporcie
def _check_config() -> None:
    """Sprawdza konfigurację modułu przy imporcie."""
    try:
        if MidoConfig.validate_config():
            logger.debug("✅ Konfiguracja MIDO poprawna")
        else:
            logger.warning("⚠️ Problemy z konfiguracją MIDO")
    except Exception:
        # Nie przerywaj importu z powodu błędów konfiguracji
        pass


# Wykonaj sprawdzenie przy imporcie (opcjonalne)
# _check_config()
