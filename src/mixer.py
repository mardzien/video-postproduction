"""
PostProductionMixer - Audio mixing for video postproduction.

Adds collision sounds to silent videos based on collision event metadata.
Features:
- Frame-based audio synchronization
- Sequential sound selection (melodic progression)
- Impact intensity-based volume control
- FFmpeg integration for final video+audio merge
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import ffmpeg  # type: ignore[import-untyped]
import numpy as np

from .collision_events import CollisionEvent, RecordingInfo, load_events_from_file
from .midi_renderer import MidiNoteRenderer, MidiRendererError


class PostProductionError(Exception):
    """Exception for postproduction-related errors."""


# Default configuration
DEFAULT_SOUNDS_FOLDER = Path(__file__).parent.parent / "sounds"
DEFAULT_VOLUME = 0.7
DEFAULT_SAMPLE_RATE = 48000


class PostProductionMixer:
    """
    Mixer for adding audio in postproduction based on collision events.
    
    Supports two modes:
    1. WAV mode (legacy): Load pre-generated WAV files from folder
    2. MIDI mode (new): Render notes on-demand from MIDI file
    
    Usage:
        # WAV mode (backward compatible)
        mixer = PostProductionMixer(sounds_folder="sounds/")
        
        # MIDI mode (new)
        mixer = PostProductionMixer(
            midi_file="midi_files/mario.mid",
            midi_instrument=11,
            midi_track=0
        )
        
        output = mixer.process_recording("video.mp4", "events.json")
    """

    def __init__(
        self,
        midi_file: str | Path,
        midi_instrument: int,
        midi_track: int | None = None,
        midi_channel: int | None = None,
        volume: float = DEFAULT_VOLUME,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ) -> None:
        """
        Initialize the mixer - MIDI mode only.
        
        Args:
            midi_file: Path to MIDI file
            midi_instrument: GM instrument 0-127
            midi_track: Track index in MIDI file (None=auto)
            midi_channel: MIDI channel 0-15 (None=all)
            volume: Base volume multiplier (0.0-1.0)
            sample_rate: Audio sample rate (default: 48000 Hz)
        """
        self.volume = volume
        self.sample_rate = sample_rate
        self.mode = "midi"
        
        self.midi_file = Path(midi_file)
        self.midi_instrument = midi_instrument
        self.midi_track = midi_track
        self.midi_channel = midi_channel
        
        if not self.midi_file.exists():
            raise PostProductionError(f"MIDI file not found: {self.midi_file}")
        
        print(f"🎹 PostProductionMixer: MIDI mode")
        print(f"   MIDI file: {self.midi_file}")
        print(f"   Instrument: {midi_instrument}")
        print(f"   Track: {midi_track if midi_track is not None else 'auto'}")
        print(f"   Channel: {midi_channel if midi_channel is not None else 'all'}")
        
        # Initialize MIDI renderer
        try:
            self.renderer = MidiNoteRenderer(sample_rate=self.sample_rate)
            
            # Load notes from MIDI
            self.midi_notes = self.renderer.load_midi_notes(
                self.midi_file,
                track=midi_track,
                channel=midi_channel,
                instrument=midi_instrument,
            )
            
            self.sound_index = 0  # For sequential note selection
            
            print(f"   ✅ Loaded {len(self.midi_notes)} notes from MIDI")
            
        except MidiRendererError as e:
            raise PostProductionError(f"Failed to load MIDI: {e}") from e

    def _select_next_sound(self) -> int:
        """
        Select next MIDI note in sequence for melodic progression.
        
        Returns:
            MIDI note number (0-127)
        """
        if not self.midi_notes:
            raise PostProductionError("No MIDI notes available!")
        
        selected = self.midi_notes[self.sound_index]
        self.sound_index = (self.sound_index + 1) % len(self.midi_notes)
        return selected

    def _load_sound_data(self, note_number: int) -> np.ndarray:
        """
        Render MIDI note to audio data.
        
        Args:
            note_number: MIDI note number (0-127)
            
        Returns:
            Audio data as float32 stereo array
        """
        try:
            sound_data = self.renderer.render_note(
                note=note_number,
                instrument=self.midi_instrument,
                duration=0.4,  # Default duration
            )
            return sound_data
            
        except Exception as e:
            print(f"⚠️ Error rendering MIDI note {note_number}: {e}")
            return self._generate_fallback_beep()

    def _generate_fallback_beep(self) -> np.ndarray:
        """Generate simple beep as fallback when sound loading fails."""
        duration = 0.1
        frequency = 800
        samples = int(duration * self.sample_rate)

        t = np.linspace(0, duration, samples, False)
        beep = np.sin(2 * np.pi * frequency * t) * 0.5

        # Smooth envelope
        envelope = np.ones_like(beep)
        fade = samples // 10
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        beep *= envelope

        return np.column_stack([beep, beep])

    def create_audio_track(
        self,
        events: list[CollisionEvent],
        duration: float,
        output_path: Path | str,
    ) -> str:
        """
        Create audio track from collision events.
        
        Args:
            events: List of collision events with timing info
            duration: Total audio duration in seconds
            output_path: Output WAV file path
            
        Returns:
            Path to created audio file
        """
        output_path = Path(output_path)

        print(f"🎼 Creating audio track: {len(events)} events, {duration:.2f}s")

        # Create empty stereo audio buffer
        total_samples = int(duration * self.sample_rate)
        audio_buffer = np.zeros((total_samples, 2), dtype=np.float32)

        # Reset sound index for consistent melodic progression
        self.sound_index = 0

        # Statistics
        collision_count = 0

        # Add sound for each collision event
        for event in events:
            try:
                sound_file = self._select_next_sound()
                sound_data = self._load_sound_data(sound_file)

                # Calculate position in buffer
                start_sample = int(event.timestamp * self.sample_rate)

                if start_sample >= total_samples:
                    print(f"⚠️ Event outside range: {event.timestamp:.3f}s > {duration:.3f}s")
                    continue

                # Calculate volume based on impact intensity
                event_volume = self.volume * (0.5 + 0.5 * event.impact_intensity)

                # Add sound to buffer
                remaining = total_samples - start_sample
                samples_to_add = min(len(sound_data), remaining)

                if samples_to_add > 0:
                    audio_buffer[start_sample : start_sample + samples_to_add] += (
                        sound_data[:samples_to_add] * event_volume
                    )

                collision_count += 1

            except Exception as e:
                print(f"⚠️ Error adding event at frame {event.frame_number}: {e}")
                continue

        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(audio_buffer))
        if max_amplitude > 1.0:
            audio_buffer = audio_buffer / max_amplitude
            print(f"🔊 Audio normalized (peak: {max_amplitude:.2f})")

        # Save to WAV
        self._save_audio_to_file(audio_buffer, output_path)

        print(f"✅ Audio track created: {collision_count} collision sounds")

        return str(output_path)

    def _save_audio_to_file(self, audio_data: np.ndarray, output_path: Path) -> None:
        """Save audio buffer to WAV file."""
        import scipy.io.wavfile as wavfile

        # Convert float32 [-1, 1] to int16
        audio_int16 = np.clip(audio_data, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        wavfile.write(str(output_path), self.sample_rate, audio_int16)

    def get_video_duration(self, video_path: Path | str) -> float:
        """Get video duration using ffprobe."""
        video_path = Path(video_path)

        if not video_path.exists():
            raise PostProductionError(f"Video file not found: {video_path}")

        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"⚠️ ffprobe failed: {result.stderr}")
                return 10.0  # Fallback

            probe_data = json.loads(result.stdout)
            duration = float(probe_data.get("format", {}).get("duration", 0.0))

            print(f"📏 Video duration: {duration:.3f}s")
            return duration

        except Exception as e:
            print(f"⚠️ Error getting video duration: {e}")
            return 10.0  # Fallback

    def _calculate_frame_based_timestamps(
        self,
        events: list[CollisionEvent],
        video_duration: float,
        total_frames: int,
    ) -> list[CollisionEvent]:
        """
        Recalculate timestamps based on frame numbers for precise sync.
        
        Uses: timestamp = (frame_number / total_frames) * video_duration
        """
        if not events or total_frames <= 0:
            return events

        print(f"🎬 Frame-based synchronization:")
        print(f"   Video duration: {video_duration:.3f}s")
        print(f"   Total frames: {total_frames}")
        print(f"   Effective FPS: {total_frames / video_duration:.2f}")

        synced_events = []
        for event in events:
            new_timestamp = (event.frame_number / total_frames) * video_duration
            synced_events.append(
                CollisionEvent(
                    frame_number=event.frame_number,
                    timestamp=new_timestamp,
                    impact_intensity=event.impact_intensity,
                )
            )

        if synced_events:
            print(f"   First event: frame {events[0].frame_number} → {synced_events[0].timestamp:.3f}s")
            print(f"   Last event: frame {events[-1].frame_number} → {synced_events[-1].timestamp:.3f}s")

        return synced_events

    def combine_video_audio(
        self,
        video_path: Path | str,
        audio_path: Path | str,
        output_path: Path | str,
    ) -> str:
        """
        Combine video with audio using FFmpeg.
        
        If the video has existing audio, it will be mixed with the new audio.
        If the video has no audio, the new audio will be added directly.
        
        Args:
            video_path: Input video file
            audio_path: Audio track file (collision sounds/melodies)
            output_path: Output video file
            
        Returns:
            Path to combined video
        """
        video_path = Path(video_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        print(f"🎬 Combining video with audio...")
        print(f"   Video: {video_path}")
        print(f"   Audio: {audio_path}")
        print(f"   Output: {output_path}")

        if not video_path.exists():
            raise PostProductionError(f"Video file not found: {video_path}")
        if not audio_path.exists():
            raise PostProductionError(f"Audio file not found: {audio_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Check if video has audio stream
            probe = ffmpeg.probe(str(video_path))
            has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
            
            video_input = ffmpeg.input(str(video_path))
            audio_input = ffmpeg.input(str(audio_path))

            if has_audio:
                print("   ℹ️  Video has existing audio - mixing both tracks")
                # Mix original video audio with new audio
                mixed_audio = ffmpeg.filter([video_input.audio, audio_input], 'amix', inputs=2, duration='longest')
                output = ffmpeg.output(
                    video_input.video,
                    mixed_audio,
                    str(output_path),
                    vcodec="libx264",
                    acodec="aac",
                    preset="medium",
                    crf="18",
                    pix_fmt="yuv420p",
                    **{"y": None},  # Overwrite output
                )
            else:
                print("   ℹ️  Video has no audio - adding new audio track")
                # Simple audio replacement (original behavior)
                output = ffmpeg.output(
                    video_input,
                    audio_input,
                    str(output_path),
                    vcodec="libx264",
                    acodec="aac",
                    preset="medium",
                    crf="18",
                    pix_fmt="yuv420p",
                    **{"y": None},  # Overwrite output
                )

            cmd = ffmpeg.compile(output, overwrite_output=True)
            print(f"🔧 FFmpeg: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ FFmpeg error: {result.stderr}")
                raise PostProductionError(f"FFmpeg failed: {result.stderr}")

            print("✅ Video and audio combined successfully!")
            return str(output_path)

        except ffmpeg.Error as e:
            raise PostProductionError(f"FFmpeg error: {e}") from e

    def process_recording(
        self,
        video_file: Path | str,
        events_file: Path | str,
        output_file: Path | str | None = None,
        cleanup_temp_files: bool = False,
    ) -> str:
        """
        Complete postproduction: events -> audio -> final video.
        
        Args:
            video_file: Silent video file
            events_file: JSON file with collision events
            output_file: Output path (auto-generated if None)
            cleanup_temp_files: Whether to delete source files after
            
        Returns:
            Path to final video with audio
        """
        video_file = Path(video_file)
        events_file = Path(events_file)

        # Load collision events
        events, recording_info = load_events_from_file(events_file)

        if not events:
            raise PostProductionError("No collision events found!")

        # Get video duration - prefer JSON metadata (WebM files often have incorrect duration)
        ffprobe_duration = self.get_video_duration(video_file)
        
        if recording_info.duration > 0 and ffprobe_duration < 0.1:
            # WebM with broken duration metadata - use JSON value
            video_duration = recording_info.duration
            print(f"⚠️ Using duration from JSON metadata: {video_duration:.3f}s (ffprobe reported: {ffprobe_duration:.3f}s)")
        else:
            video_duration = ffprobe_duration

        # Frame-based synchronization if we have frame data
        if recording_info.total_frames > 0:
            print("🎬 Using frame-based synchronization (most precise)")
            events = self._calculate_frame_based_timestamps(
                events, video_duration, recording_info.total_frames
            )
        else:
            print("⚠️ No frame metadata, using original timestamps")

        # Calculate audio duration (video + margin for sound tails)
        audio_duration = video_duration + 0.5

        # Generate output path
        if output_file is None:
            base_name = video_file.stem.replace("_video_", "_final_")
            output_file = video_file.parent / f"{base_name}.mp4"
        else:
            output_file = Path(output_file)

        # Create temporary audio file
        temp_audio = video_file.parent / f"temp_audio_{video_file.stem}.wav"

        try:
            # Create audio track
            self.create_audio_track(events, audio_duration, temp_audio)

            # Combine video + audio
            final_video = self.combine_video_audio(video_file, temp_audio, output_file)

            print(f"🎉 Postproduction complete: {final_video}")
            return final_video

        finally:
            # Cleanup temporary audio
            try:
                if temp_audio.exists():
                    temp_audio.unlink()
            except Exception:
                pass

            # Cleanup source files if requested
            if cleanup_temp_files:
                for f in [video_file, events_file]:
                    try:
                        if Path(f).exists():
                            Path(f).unlink()
                            print(f"   🧹 Deleted: {Path(f).name}")
                    except Exception as e:
                        print(f"   ⚠️ Could not delete {Path(f).name}: {e}")

    def cleanup(self) -> None:
        """Cleanup MIDI renderer resources."""
        if hasattr(self, 'renderer'):
            self.renderer.cleanup()
        print("🧹 PostProductionMixer cleaned up")

