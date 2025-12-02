"""
Generator melodii MIDI dla modułu MIDO Sound Generator.

Konwertuje definicje melodii na pliki MIDI, a następnie na WAV.
"""

import subprocess  # type: ignore
from collections.abc import Sequence
from pathlib import Path
from typing import Optional, Union

from midi2audio import FluidSynth  # type: ignore

import mido  # type: ignore

try:
    # Try relative imports first (when used as module)
    from .config import (
        MELODIES,
        MELODY_DURATIONS,
        MELODY_INSTRUMENTS,
        NOTE_MAPPING,
        MidoConfig,
    )
    from .logger import logger  # type: ignore[no-redef]
except ImportError:
    # Fall back to absolute imports (when used as script)
    from config import (  # type: ignore[no-redef]
        MELODIES,
        MELODY_DURATIONS,
        MELODY_INSTRUMENTS,
        NOTE_MAPPING,
        MidoConfig,
    )
    from logger import logger  # type: ignore[no-redef]


class MelodyGenerator:
    """Generator melodii MIDI z konwersją do WAV."""

    def __init__(self, soundfont_path: Optional[str] = None):
        """
        Inicjalizuje generator melodii.

        Args:
            soundfont_path: Ścieżka do SoundFont (auto-wykrywanie jeśli None)
        """
        self.config = MidoConfig()

        # Wykryj lub użyj podanego SoundFont
        if soundfont_path is None:
            try:
                soundfont_path = self.config.get_soundfont_path()
                logger.soundfont_found(soundfont_path)
            except FileNotFoundError as e:
                logger.soundfont_missing()
                raise e

        self.soundfont_path = soundfont_path
        self.fluidsynth: Optional[FluidSynth] = None

        # Utwórz folder wyjściowy
        Path(self.config.OUTPUT_FOLDER).mkdir(exist_ok=True)

    def _init_fluidsynth(self) -> FluidSynth:
        """Inicjalizuje FluidSynth z lazy loading."""
        if self.fluidsynth is None:
            try:
                self.fluidsynth = FluidSynth(sound_font=self.soundfont_path)
                logger.debug(f"FluidSynth zainicjalizowany z {self.soundfont_path}")
            except Exception as e:
                logger.error("Błąd inicjalizacji FluidSynth", e)
                raise
        return self.fluidsynth

    def generate_melody_midi(
        self,
        notes: Sequence[Optional[int]],
        file_path: Union[str, Path],
        duration_sec: Optional[float] = None,
        velocity: Optional[int] = None,
        bpm: Optional[int] = None,
        instrument: Optional[int] = None,
    ) -> None:
        """
        Tworzy plik MIDI z sekwencji nut - ZOPTYMALIZOWANY DLA KRÓTKICH PLIKÓW.

        Args:
            notes: Lista numerów nut MIDI (None = przerwa)
            file_path: Ścieżka do zapisu pliku MIDI
            duration_sec: Czas trwania każdej nuty
            velocity: Głośność nut (0-127)
            bpm: Tempo w BPM
            instrument: Numer instrumentu GM
        """
        # Użyj wartości domyślnych z konfiguracji
        duration_sec = (
            duration_sec
            if duration_sec is not None
            else self.config.DEFAULT_NOTE_DURATION
        )
        velocity = velocity if velocity is not None else self.config.DEFAULT_VELOCITY
        bpm = bpm if bpm is not None else self.config.DEFAULT_BPM
        instrument = (
            instrument if instrument is not None else self.config.DEFAULT_INSTRUMENT
        )

        # Stwórz plik MIDI z wysoką rozdzielczością dla precyzji
        mid = mido.MidiFile(ticks_per_beat=960)  # type: ignore
        track = mido.MidiTrack()  # type: ignore
        mid.tracks.append(track)

        # Ustawienia tempa i instrumentu
        tempo = mido.bpm2tempo(bpm)  # type: ignore
        track.append(mido.MetaMessage("set_tempo", tempo=tempo))  # type: ignore
        track.append(mido.Message("program_change", program=instrument, time=0))  # type: ignore

        # Oblicz czas w tickach MIDI - krócej dla kompaktowych plików
        ticks_per_note = int(duration_sec * tempo / 1e6 * mid.ticks_per_beat)

        # OPTYMALIZACJA: Dla pojedynczych nut (typowy przypadek) minimalizuj czas
        if len(notes) == 1:
            note = notes[0]
            if note is not None:
                # Pojedyncza nuta - graj od razu bez opóźnienia
                track.append(
                    mido.Message("note_on", note=note, velocity=velocity, time=0)  # type: ignore[attr-defined]
                )  # type: ignore
                # Krótszy czas trwania dla responsywności
                short_duration = max(
                    ticks_per_note // 2, 120
                )  # Min 120 ticks dla słyszalności
                track.append(
                    mido.Message("note_off", note=note, velocity=0, time=short_duration)  # type: ignore[attr-defined]
                )  # type: ignore
                # Minimal end marker
                track.append(mido.Message("note_off", note=0, velocity=0, time=1))  # type: ignore[attr-defined]
            else:
                # Przerwa - bardzo krótka
                track.append(
                    mido.Message(  # type: ignore[attr-defined]
                        "note_off",
                        note=0,
                        velocity=0,
                        time=max(ticks_per_note // 4, 60),
                    )
                )  # type: ignore
        else:
            # Sekwencja nut - optymalizacja dla kolejnych nut
            for _, note in enumerate(notes):
                if note is None:
                    # Przerwa w melodii - minimalna
                    short_pause = max(ticks_per_note // 8, 30)
                    track.append(
                        mido.Message("note_off", note=0, velocity=0, time=short_pause)  # type: ignore[attr-defined]
                    )  # type: ignore
                    continue

                # Note ON - bez opóźnienia między nutami
                note_on_time = 0
                track.append(
                    mido.Message(  # type: ignore[attr-defined]
                        "note_on", note=note, velocity=velocity, time=note_on_time
                    )
                )  # type: ignore

                # Note OFF - pełny czas dla słyszalności w sekwencji
                track.append(
                    mido.Message("note_off", note=note, velocity=0, time=ticks_per_note)  # type: ignore[attr-defined]
                )  # type: ignore

            # Końcowy marker dla sekwencji
            track.append(mido.Message("note_off", note=0, velocity=0, time=1))  # type: ignore

        # Zapisz plik
        mid.save(str(file_path))
        logger.debug(f"Kompaktowy plik MIDI zapisany: {file_path}")

    def generate_single_note(
        self,
        note_name: str,
        output_file: Union[str, Path],
        duration_sec: Optional[float] = None,
        velocity: Optional[int] = None,
        bpm: Optional[int] = None,
        instrument: Optional[int] = None,
    ) -> bool:
        """
        Generuje pojedynczą nutę jako kompaktowy plik WAV.

        Args:
            note_name: Nazwa nuty (np. 'C', 'D#', 'F')
            output_file: Ścieżka do pliku WAV (z zerem wiodącym, np. '01.wav')
            duration_sec: Czas trwania nuty w sekundach
            velocity: Głośność nuty (0-127)
            bpm: Tempo w BPM
            instrument: Numer instrumentu GM

        Returns:
            True jeśli generacja się powiodła
        """
        try:
            # Konwertuj nazwę nuty na numer MIDI
            midi_note = NOTE_MAPPING.get(note_name.strip())
            if midi_note is None:
                logger.error(f"Nieznana nuta: {note_name}")
                return False

            # Przygotuj ścieżki plików
            output_path = Path(output_file)
            midi_path = output_path.with_suffix(".mid")

            logger.debug(f"Generuję nutę {note_name} -> {output_file}")

            # Generuj MIDI
            self.generate_melody_midi(
                [midi_note], midi_path, duration_sec, velocity, bpm, instrument
            )

            # Konwertuj na WAV z optymalizacją
            success = self.convert_midi_to_wav(midi_path, output_path)

            # Usuń tymczasowy plik MIDI
            if midi_path.exists():
                midi_path.unlink()

            if success:
                logger.debug(
                    f"✅ Nuta {note_name} wygenerowana jako kompaktowy {output_file}"
                )
                return True
            else:
                logger.error(f"❌ Błąd konwersji nuty {note_name}")
                return False

        except Exception as e:
            logger.error(f"Błąd generacji nuty {note_name}", e)
            return False

    def generate_melody(self, melody_name: str, notes: list[str]) -> bool:
        """
        Generuje pełną melodię jako zestaw plików WAV.

        Args:
            melody_name: Nazwa melodii
            notes: Lista nazw nut

        Returns:
            bool: True jeśli generacja się powiodła
        """
        output_dir = Path(self.config.OUTPUT_FOLDER) / melody_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # 🎭 SPRAWDŹ SPECJALNY INSTRUMENT DLA MELODII!
        special_instrument = MELODY_INSTRUMENTS.get(melody_name)
        if special_instrument is not None:
            logger.info(
                f"🎺 Używam specjalnego instrumentu {special_instrument} "
                f"dla melodii '{melody_name}'"
            )

        # 🎵 SPRAWDŹ SPECJALNE DŁUGOŚCI NUT DLA MELODII!
        special_durations = MELODY_DURATIONS.get(melody_name)
        if special_durations is not None:
            logger.info(
                f"🎼 Używam specjalnych długości nut dla melodii '{melody_name}' "
                f"(autentyczny rytm!)"
            )
            if len(special_durations) != len(notes):
                logger.warning(
                    f"⚠️ Liczba długości ({len(special_durations)}) "
                    f"nie zgadza się z liczbą nut ({len(notes)})!"
                )

        logger.generation_start(melody_name, len(notes))

        success_count = 0
        for i, note_name in enumerate(notes):
            logger.generation_progress(i, note_name, len(notes))

            # Pobierz specjalną długość dla tej nuty (jeśli istnieje)
            note_duration = None
            if special_durations is not None and i < len(special_durations):
                note_duration = special_durations[i]
                logger.debug(f"🎵 Nuta {i+1} ({note_name}): długość {note_duration}s")

            # Indeksowanie od 1 (zgodnie z istniejącą konwencją)
            # Przekaż specjalny instrument i długość jeśli istnieją
            if self.generate_single_note(
                note_name,
                output_dir / f"{i+1:02d}.wav",
                duration_sec=note_duration,
                instrument=special_instrument,
            ):
                success_count += 1

        if success_count == len(notes):
            logger.generation_complete(melody_name, str(output_dir))
            return True
        else:
            logger.error(
                f"Generacja melodii {melody_name} niepełna: "
                f"{success_count}/{len(notes)}"
            )
            return False

    def generate_all_melodies(
        self, output_folder: Union[str, Path] = "melodies"
    ) -> dict[str, bool]:
        """
        Generuje wszystkie melodie z konfiguracji - ZOPTYMALIZOWANE DLA KRÓTKICH PLIKÓW.

        Args:
            output_folder: Folder na wygenerowane melodie
        """
        output_path = Path(output_folder)

        total = len(MELODIES)
        successful = 0
        successful_names = []

        logger.info(f"🎼 Rozpoczynam generację {total} melodii (wersja kompaktowa)")

        for melody_name, notes_str in MELODIES.items():
            try:
                melody_folder = output_path / melody_name
                melody_folder.mkdir(parents=True, exist_ok=True)

                # Konwertuj nazwy nut na numery MIDI
                midi_notes = [NOTE_MAPPING.get(note.strip()) for note in notes_str]

                # 🎭 SPRAWDŹ SPECJALNY INSTRUMENT DLA MELODII!
                special_instrument = MELODY_INSTRUMENTS.get(melody_name)
                if special_instrument is not None:
                    logger.info(
                        f"🎺 Używam specjalnego instrumentu {special_instrument} "
                        f"dla melodii '{melody_name}'"
                    )

                # 🎵 SPRAWDŹ SPECJALNE DŁUGOŚCI NUT DLA MELODII!
                special_durations = MELODY_DURATIONS.get(melody_name)
                if special_durations is not None:
                    logger.info(
                        f"🎼 Używam specjalnych długości nut dla '{melody_name}' "
                        f"(autentyczny rytm!)"
                    )
                    if len(special_durations) != len(notes_str):
                        logger.warning(
                            f"⚠️ Liczba długości ({len(special_durations)}) "
                            f"nie zgadza się z liczbą nut ({len(notes_str)})!"
                        )

                logger.generation_start(melody_name, len(midi_notes))

                # Generuj każdą nutę jako ODDZIELNY KRÓTKI PLIK
                for i, midi_note in enumerate(midi_notes, 1):
                    if midi_note is None:
                        continue  # Pomiń pauzy

                    # Pobierz specjalną długość dla tej nuty (jeśli istnieje)
                    note_duration = None
                    if special_durations is not None and (i - 1) < len(
                        special_durations
                    ):
                        note_duration = special_durations[
                            i - 1
                        ]  # i-1 bo enumerate zaczyna od 1
                        logger.debug(
                            f"🎵 Nuta {i} ({notes_str[i-1]}): długość {note_duration}s"
                        )

                    # Pliki dla pojedynczych nut - z zerem wiodącym
                    midi_file = melody_folder / f"{i:02d}.mid"
                    wav_file = melody_folder / f"{i:02d}.wav"

                    # Generuj kompaktową nutę Z WŁAŚCIWYM INSTRUMENTEM I DŁUGOŚCIĄ
                    self.generate_melody_midi(
                        [midi_note],
                        midi_file,
                        duration_sec=note_duration,
                        instrument=special_instrument,
                    )

                    # Konwertuj z optymalizacją długości
                    if self.convert_midi_to_wav(midi_file, wav_file):
                        logger.generation_progress(
                            i - 1, notes_str[i - 1], len(notes_str)
                        )
                    else:
                        logger.error(
                            f"Błąd konwersji nuty {i:02d} w melodii {melody_name}"
                        )

                successful += 1
                successful_names.append(melody_name)
                logger.generation_complete(melody_name, str(melody_folder))

            except Exception as e:
                logger.error(f"Błąd generacji melodii {melody_name}", e)

        logger.info(
            f"🎼 Generacja zakończona: {successful}/{total} melodii wygenerowanych"
        )
        if successful_names:
            logger.info(f"✅ Melodie wygenerowane: {', '.join(successful_names)}")

        # Zwróć wyniki dla każdej melodii
        results = {}
        for melody_name in MELODIES.keys():
            results[melody_name] = melody_name in successful_names
        return results

    def cleanup(self) -> None:
        """Czyści zasoby generatora."""
        if self.fluidsynth:
            # FluidSynth nie ma metody cleanup, ale Python GC to obsłuży
            self.fluidsynth = None
            logger.debug("Generator wyczyszczony")

    def convert_midi_to_wav(
        self,
        midi_path: Union[str, Path],
        wav_path: Union[str, Path],
        sample_rate: int = 44100,
    ) -> bool:
        """
        Konwertuje plik MIDI na WAV z minimalną długością - BEZ ZBĘDNEJ CISZY.

        Args:
            midi_path: Ścieżka do pliku MIDI
            wav_path: Ścieżka do zapisu pliku WAV
            sample_rate: Częstotliwość próbkowania

        Returns:
            True jeśli konwersja się powiodła
        """
        try:
            # Sprawdź dostępność SoundFont
            soundfont_path = str(self.config.get_soundfont_path())
            if not Path(soundfont_path).exists():
                print(f"❌ Nie znaleziono SoundFont: {soundfont_path}")
                return False

            print(f"🎵 Konwersja: {midi_path} -> {wav_path}")

            # OPTYMALIZACJA: Skrócona konwersja z minimalnym gain i bez zbędnego reverbu
            cmd = [
                "fluidsynth",
                "-ni",  # Bez interfejsu
                "-g",
                "0.8",  # Niższy gain dla krótszego fade-out
                "-r",
                str(sample_rate),  # Sample rate
                "-F",
                str(wav_path),  # Output WAV
                str(soundfont_path),  # SoundFont
                str(midi_path),  # Input MIDI
            ]

            # Uruchom FluidSynth z timeout dla krótkich plików
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # Krótki timeout dla pojedynczych nut
            )

            if result.returncode == 0:
                # DODATKOWA OPTYMALIZACJA: Przytnij ciszę z końca pliku WAV
                self._trim_wav_silence(wav_path)

                print(f"✅ Kompaktowy WAV: {wav_path}")
                return True
            else:
                print(f"❌ Błąd FluidSynth: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout podczas konwersji: {midi_path}")
            return False
        except Exception as e:
            print(f"❌ Błąd konwersji: {e}")
            return False

    def _trim_wav_silence(self, wav_path: Union[str, Path]) -> None:
        """
        Przycina ciszę z końca pliku WAV - KLUCZ DO KRÓTKICH PLIKÓW!

        Args:
            wav_path: Ścieżka do pliku WAV
        """
        try:
            import wave

            import numpy as np

            with wave.open(str(wav_path), "rb") as wav_file:
                frames = wav_file.readframes(-1)
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                nchannels = wav_file.getnchannels()

            # Konwertuj na numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                return  # Nieobsługiwany format

            audio_data = np.frombuffer(frames, dtype=dtype)

            # Znajdź ostatni moment z dźwiękiem (próg ciszy)
            if nchannels == 2:
                audio_data = audio_data.reshape(-1, 2)
                # Stereo - sprawdź max z obu kanałów
                max_values = np.max(np.abs(audio_data), axis=1)
            else:
                max_values = np.abs(audio_data)

            # Próg ciszy - bardzo niski dla precyzji
            silence_threshold = np.max(max_values) * 0.01  # 1% maksymalnej amplitudy

            # Znajdź ostatni indeks z dźwiękiem
            sound_indices = np.where(max_values > silence_threshold)[0]
            if len(sound_indices) == 0:
                return  # Cały plik to cisza

            last_sound_index = sound_indices[-1]

            # Dodaj małą "poduszkę" po ostatnim dźwięku (0.1 sekundy)
            padding_samples = int(0.1 * framerate)
            trim_index = min(last_sound_index + padding_samples, len(max_values))

            # Przytnij audio
            if nchannels == 2:
                trimmed_audio = audio_data[:trim_index].flatten()
            else:
                trimmed_audio = audio_data[:trim_index]

            # Zapisz przyciętą wersję
            with wave.open(str(wav_path), "wb") as wav_file:
                wav_file.setnchannels(nchannels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(framerate)
                wav_file.writeframes(trimmed_audio.tobytes())

            print(f"🔧 Przyciętó ciszę z {wav_path} (zapisano {trim_index} sampli)")

        except ImportError:
            print("📦 numpy niedostępne - pomijam przycinanie ciszy")
        except Exception as e:
            print(f"⚠️ Błąd przycinania ciszy: {e}")


def main() -> None:
    """Główna funkcja generująca melodie."""
    try:
        # Sprawdź konfigurację
        if not MidoConfig.validate_config():
            logger.error("Nieprawidłowa konfiguracja modułu MIDO")
            return

        # Utwórz generator
        generator = MelodyGenerator()

        # Wygeneruj wszystkie melodie
        results = generator.generate_all_melodies()

        # Podsumowanie
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]

        if successful:
            logger.info(f"✅ Melodie wygenerowane: {', '.join(successful)}")

        if failed:
            logger.error(f"❌ Błędy generacji: {', '.join(failed)}")

        # Cleanup
        generator.cleanup()

    except Exception as e:
        logger.error("Krytyczny błąd generatora", e)
        raise


if __name__ == "__main__":
    main()
