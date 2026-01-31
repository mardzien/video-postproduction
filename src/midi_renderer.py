"""
MIDI Note Renderer for on-demand audio generation.

Renders individual notes from MIDI files on-the-fly using FluidSynth,
with in-memory caching for performance.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional
import sys

import numpy as np
import scipy.io.wavfile as wavfile

try:
    # When used as module
    from mido_generator.generator import MelodyGenerator
    from mido_generator.midi_import import _extract_note_events, _collect_track_stats, _select_default_track
except ImportError:
    # When used standalone
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from mido_generator.generator import MelodyGenerator
    from mido_generator.midi_import import _extract_note_events, _collect_track_stats, _select_default_track

# Import external mido library (MIDI parsing)
import mido as mido_lib  # type: ignore


class MidiRendererError(Exception):
    """Exception for MIDI rendering errors."""


class MidiNoteRenderer:
    """
    Renders individual notes from MIDI files on-demand.
    
    Features:
    - Extracts notes from MIDI files using mido
    - Renders single notes to audio arrays using FluidSynth
    - In-memory caching for performance (cache key: note, instrument, duration)
    - Backward compatible with existing WAV-based workflow
    
    Usage:
        renderer = MidiNoteRenderer()
        notes = renderer.load_midi_notes("song.mid", instrument=19)
        audio = renderer.render_note(60, instrument=19, duration=0.4)
    """

    def __init__(self, soundfont_path: str | None = None, sample_rate: int = 48000):
        """
        Initialize MIDI renderer.
        
        Args:
            soundfont_path: Path to SoundFont file (auto-detect if None)
            sample_rate: Audio sample rate for rendering
        """
        self.generator = MelodyGenerator(soundfont_path)
        self.sample_rate = sample_rate
        self.note_cache: dict[tuple[int, int, float], np.ndarray] = {}
        
        print(f"🎹 MidiNoteRenderer initialized")
        print(f"   SoundFont: {self.generator.soundfont_path}")
        print(f"   Sample rate: {self.sample_rate} Hz")

    def load_midi_notes(
        self,
        midi_path: str | Path,
        track: int | None = None,
        channel: int | None = None,
        instrument: int | None = None,
        start_sec: float = 0.0,
        end_sec: float | None = None,
        chord_policy: str = "highest",
        max_notes: int | None = 120,
    ) -> list[int]:
        """
        Extract MIDI note numbers from file.
        
        Args:
            midi_path: Path to MIDI file
            track: Track index (None = auto-select best track)
            channel: MIDI channel 0-15 (None = all non-drum channels)
            instrument: GM instrument 0-127 (stored for reference)
            start_sec: Start time in seconds
            end_sec: End time in seconds (None = entire file)
            chord_policy: How to handle chords ("highest", "arpeggiate", "skip")
            max_notes: Maximum notes to extract (safety limit)
            
        Returns:
            List of MIDI note numbers (60 = Middle C)
            
        Raises:
            MidiRendererError: If MIDI file invalid or no notes found
        """
        midi_path = Path(midi_path)
        
        if not midi_path.exists():
            raise MidiRendererError(f"MIDI file not found: {midi_path}")
        
        try:
            mid = mido_lib.MidiFile(str(midi_path))
            stats = _collect_track_stats(mid)
            
            # Auto-select track if not specified
            chosen_track = track if track is not None else _select_default_track(stats)
            chosen_track_stats = next(s for s in stats if s.track_index == chosen_track)
            
            print(f"🎼 Loading MIDI notes from: {midi_path.name}")
            print(f"   Track: {chosen_track} ({chosen_track_stats.name or 'unnamed'})")
            print(f"   Channel: {channel if channel is not None else 'auto'}")
            print(f"   Instrument: {instrument if instrument is not None else 'default'}")
            
            # Extract note events
            events = _extract_note_events(
                mid=mid,
                track_index=chosen_track,
                channel=channel,
                start_sec=start_sec,
                end_sec=end_sec,
                chord_policy=chord_policy,
                max_notes=max_notes,
            )
            
            if not events:
                raise MidiRendererError(
                    f"No note events found in track {chosen_track}. "
                    f"Try a different track or channel."
                )
            
            # Extract just the note numbers
            notes = [event.note for event in events]
            
            print(f"   ✅ Extracted {len(notes)} notes (range: {min(notes)}-{max(notes)})")
            
            return notes
            
        except Exception as e:
            # Handle any MIDI parsing errors
            if "MIDI" in str(type(e).__name__) or "midi" in str(e).lower():
                raise MidiRendererError(f"Invalid MIDI file {midi_path}: {e}") from e
            raise MidiRendererError(f"Error loading MIDI notes: {e}") from e

    def render_note(
        self,
        note: int,
        instrument: int = 0,
        duration: float = 0.4,
        velocity: int = 100,
    ) -> np.ndarray:
        """
        Render single note to audio array (with caching).
        
        Args:
            note: MIDI note number (60 = Middle C, range 0-127)
            instrument: GM instrument (0-127)
            duration: Note duration in seconds
            velocity: Note velocity (0-127, affects volume)
            
        Returns:
            Audio array as float32 stereo [-1, 1], shape (samples, 2)
            
        Raises:
            MidiRendererError: If rendering fails
        """
        # Check cache first
        cache_key = (note, instrument, duration)
        if cache_key in self.note_cache:
            return self.note_cache[cache_key]
        
        # Render note using generator
        try:
            with tempfile.TemporaryDirectory(prefix="midi_render_") as tmpdir:
                tmpdir_path = Path(tmpdir)
                midi_file = tmpdir_path / "note.mid"
                wav_file = tmpdir_path / "note.wav"
                
                # Generate MIDI file for single note
                self.generator.generate_melody_midi(
                    notes=[note],
                    file_path=midi_file,
                    duration_sec=duration,
                    velocity=velocity,
                    instrument=instrument,
                )
                
                # Convert to WAV
                success = self.generator.convert_midi_to_wav(
                    midi_file, wav_file, sample_rate=self.sample_rate
                )
                
                if not success:
                    raise MidiRendererError(f"Failed to convert note {note} to WAV")
                
                # Load WAV as numpy array
                sample_rate, audio_data = wavfile.read(str(wav_file))
                
                # Convert to float32 [-1, 1]
                if audio_data.dtype == np.int16:
                    audio_float = audio_data.astype(np.float32) / 32768.0
                elif audio_data.dtype == np.int32:
                    audio_float = audio_data.astype(np.float32) / 2147483648.0
                elif audio_data.dtype == np.uint8:
                    audio_float = (audio_data.astype(np.float32) - 128) / 128.0
                else:
                    audio_float = audio_data.astype(np.float32)
                
                # Ensure stereo
                if audio_float.ndim == 1:
                    audio_float = np.column_stack([audio_float, audio_float])
                
                # Cache for reuse
                self.note_cache[cache_key] = audio_float
                
                return audio_float
                
        except Exception as e:
            raise MidiRendererError(f"Error rendering note {note}: {e}") from e

    def get_cache_stats(self) -> dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache info (size, entries, memory_mb)
        """
        total_bytes = sum(arr.nbytes for arr in self.note_cache.values())
        return {
            "entries": len(self.note_cache),
            "memory_mb": total_bytes / (1024 * 1024),
        }

    def clear_cache(self) -> None:
        """Clear the note rendering cache."""
        cache_size = len(self.note_cache)
        self.note_cache.clear()
        print(f"🧹 Cleared cache ({cache_size} entries)")

    def pre_render_notes(
        self,
        notes: list[int],
        instrument: int = 0,
        duration: float = 0.4,
    ) -> None:
        """
        Pre-render all notes in a melody to populate cache.
        
        Useful for ensuring smooth playback by rendering all notes upfront.
        
        Args:
            notes: List of MIDI note numbers
            instrument: GM instrument
            duration: Note duration in seconds
        """
        unique_notes = set(notes)
        print(f"🎵 Pre-rendering {len(unique_notes)} unique notes...")
        
        for i, note in enumerate(unique_notes, 1):
            self.render_note(note, instrument, duration)
            if i % 10 == 0 or i == len(unique_notes):
                print(f"   Progress: {i}/{len(unique_notes)}")
        
        cache_stats = self.get_cache_stats()
        print(f"✅ Pre-rendering complete")
        print(f"   Cache: {cache_stats['entries']} entries, {cache_stats['memory_mb']:.2f} MB")

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.clear_cache()
        if hasattr(self.generator, 'cleanup'):
            self.generator.cleanup()


# Example usage / testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python midi_renderer.py <midi_file> [instrument]")
        sys.exit(1)
    
    midi_file = sys.argv[1]
    instrument = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    try:
        renderer = MidiNoteRenderer()
        
        # Load notes from MIDI
        notes = renderer.load_midi_notes(midi_file, instrument=instrument)
        
        print(f"\n🎼 Loaded {len(notes)} notes")
        print(f"   Notes: {notes[:10]}{'...' if len(notes) > 10 else ''}")
        
        # Render first note as demo
        if notes:
            print(f"\n🎵 Rendering first note ({notes[0]}) with instrument {instrument}...")
            audio = renderer.render_note(notes[0], instrument=instrument)
            print(f"   Audio shape: {audio.shape}")
            print(f"   Duration: {len(audio) / 48000:.3f}s")
            
            # Cache stats
            stats = renderer.get_cache_stats()
            print(f"\n📊 Cache stats:")
            print(f"   Entries: {stats['entries']}")
            print(f"   Memory: {stats['memory_mb']:.2f} MB")
        
        renderer.cleanup()
        print("\n✅ Done!")
        
    except MidiRendererError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
