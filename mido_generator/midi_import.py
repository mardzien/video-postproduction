"""
MIDI -> WAV notes importer for MIDO Sound Generator.

Exports a chosen MIDI track/channel into a folder of sequential WAV files:
  melodies/<name>/01.wav, 02.wav, ...

This is useful when you already have a MIDI file (e.g. a riff) and you want to
use it as a "melody pack" in the postproduction pipeline (sequential samples).
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Iterable, Optional
import sys
import importlib.util

# Import external mido library (for MIDI parsing) - no conflict now!
import mido as mido_lib  # type: ignore

try:
    # When used as module: python -m mido_generator.midi_import ...
    from .generator import MelodyGenerator  # type: ignore[no-redef]
except ImportError:
    # When used as script from within mido_generator/: python midi_import.py ...
    from generator import MelodyGenerator  # type: ignore[no-redef]


DEFAULT_TEMPO = 500_000  # microseconds per beat (120 BPM)


@dataclass(frozen=True)
class TrackStats:
    track_index: int
    name: Optional[str]
    note_on_count: int
    polyphonic_note_on_count: int
    programs: tuple[int, ...]
    channels: tuple[int, ...]
    note_min: Optional[int]
    note_max: Optional[int]


@dataclass(frozen=True)
class NoteEvent:
    start_sec: float
    duration_sec: float
    note: int
    channel: int


def _iter_track_messages_with_abs_time_sec(
    mid: mido_lib.MidiFile, track_index: int
) -> Iterable[tuple[float, mido_lib.Message]]:
    """
    Yield (abs_time_sec, msg) for messages in a single track, handling tempo
    changes within the track.
    """
    tempo = DEFAULT_TEMPO
    abs_sec = 0.0

    for msg in mid.tracks[track_index]:
        # msg.time is delta time in ticks for track messages
        if msg.time:
            abs_sec += mido_lib.tick2second(msg.time, mid.ticks_per_beat, tempo)
        yield abs_sec, msg
        if msg.type == "set_tempo":
            tempo = msg.tempo


def _collect_track_stats(mid: mido_lib.MidiFile) -> list[TrackStats]:
    stats: list[TrackStats] = []

    for ti, track in enumerate(mid.tracks):
        name: Optional[str] = None
        programs_set: set[int] = set()
        channels_set: set[int] = set()

        note_on_count = 0
        polyphonic_note_on_count = 0
        note_min: Optional[int] = None
        note_max: Optional[int] = None

        # Track-level polyphony approximation: count note_on that occur while any
        # note is already active (per channel, excluding drums).
        active_notes: DefaultDict[int, set[int]] = defaultdict(set)

        for _, msg in _iter_track_messages_with_abs_time_sec(mid, ti):
            if msg.type == "track_name" and name is None:
                name = msg.name

            if msg.type == "program_change":
                programs_set.add(int(msg.program))
                channels_set.add(int(getattr(msg, "channel", 0)))

            if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                ch = int(getattr(msg, "channel", 0))
                channels_set.add(ch)
                # Skip drums by default for stats (channel 9 = 10th channel)
                if ch == 9:
                    continue

                note_on_count += 1

                # Polyphony heuristic
                if active_notes[ch]:
                    polyphonic_note_on_count += 1
                active_notes[ch].add(int(msg.note))

                note = int(msg.note)
                note_min = note if note_min is None else min(note_min, note)
                note_max = note if note_max is None else max(note_max, note)

            if msg.type in {"note_off", "note_on"} and (
                msg.type == "note_off" or getattr(msg, "velocity", 0) == 0
            ):
                ch = int(getattr(msg, "channel", 0))
                if ch == 9:
                    continue
                note = int(getattr(msg, "note", -1))
                if note in active_notes[ch]:
                    active_notes[ch].remove(note)

        stats.append(
            TrackStats(
                track_index=ti,
                name=name,
                note_on_count=note_on_count,
                polyphonic_note_on_count=polyphonic_note_on_count,
                programs=tuple(sorted(programs_set)),
                channels=tuple(sorted(channels_set)),
                note_min=note_min,
                note_max=note_max,
            )
        )

    return stats


def _select_default_track(stats: list[TrackStats]) -> int:
    """
    Pick the "best" track: highest note_on_count, with a small penalty for
    polyphony (we usually want a monophonic melody line).
    """
    best_ti = 0
    best_score = -1.0
    for s in stats:
        score = float(s.note_on_count) - 0.25 * float(s.polyphonic_note_on_count)
        if score > best_score:
            best_score = score
            best_ti = s.track_index
    return best_ti


def _extract_note_events(
    mid: mido_lib.MidiFile,
    track_index: int,
    channel: Optional[int],
    start_sec: float,
    end_sec: Optional[float],
    chord_policy: str,
    max_notes: Optional[int],
) -> list[NoteEvent]:
    """
    Extract (start, duration, midi_note) events from a track.

    - channel: if set, only that channel is used (drums excluded regardless)
    - chord_policy:
        - "arpeggiate": keep all notes sorted by pitch when starting at same time
        - "highest": keep only the highest note for each start time bucket
        - "skip": skip start times with multiple simultaneous notes
    """
    # Active notes: key = (channel, note) -> list of start_sec (stack)
    active: DefaultDict[tuple[int, int], list[float]] = defaultdict(list)

    raw_events: list[NoteEvent] = []

    # Collect note_on/off with absolute timestamps
    for abs_t, msg in _iter_track_messages_with_abs_time_sec(mid, track_index):
        if abs_t < start_sec:
            continue
        if end_sec is not None and abs_t > end_sec:
            break

        if msg.type not in {"note_on", "note_off"}:
            continue

        ch = int(getattr(msg, "channel", 0))
        if ch == 9:
            continue  # drums
        if channel is not None and ch != channel:
            continue

        note = int(getattr(msg, "note", -1))

        # note_on with velocity 0 is effectively note_off
        is_note_on = msg.type == "note_on" and getattr(msg, "velocity", 0) > 0
        is_note_off = msg.type == "note_off" or (
            msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
        )

        key = (ch, note)
        if is_note_on:
            active[key].append(abs_t)
        elif is_note_off:
            if not active[key]:
                continue
            start_t = active[key].pop(0)
            if abs_t <= start_t:
                continue
            raw_events.append(
                NoteEvent(
                    start_sec=start_t,
                    duration_sec=abs_t - start_t,
                    note=note,
                    channel=ch,
                )
            )

    # Group by start time (rounded to ms) to handle chords
    grouped: DefaultDict[int, list[NoteEvent]] = defaultdict(list)
    for ev in raw_events:
        bucket_ms = int(round(ev.start_sec * 1000.0))
        grouped[bucket_ms].append(ev)

    out_events: list[NoteEvent] = []
    for bucket_ms in sorted(grouped.keys()):
        evs = grouped[bucket_ms]
        if len(evs) == 1:
            out_events.append(evs[0])
            continue

        if chord_policy == "arpeggiate":
            out_events.extend(sorted(evs, key=lambda e: e.note))
        elif chord_policy == "highest":
            out_events.append(max(evs, key=lambda e: e.note))
        elif chord_policy == "skip":
            continue
        else:
            raise ValueError(f"Unknown chord_policy: {chord_policy}")

        if max_notes is not None and len(out_events) >= max_notes:
            out_events = out_events[:max_notes]
            break

    # Sort final events by time (then pitch), apply max_notes again
    out_events.sort(key=lambda e: (e.start_sec, e.note))
    if max_notes is not None:
        out_events = out_events[:max_notes]

    return out_events


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _parse_csv_int_list(value: str) -> list[int]:
    try:
        parts = [p.strip() for p in value.split(",")]
        return [int(p) for p in parts if p]
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid integer list: {value!r} (expected e.g. '0,1')"
        ) from e


def _track_has_tempo(track: mido_lib.MidiTrack) -> bool:
    return any(msg.type == "set_tempo" for msg in track)


def _build_midi_subset(mid: mido_lib.MidiFile, track_indices: list[int]) -> mido_lib.MidiFile:
    if not track_indices:
        raise ValueError("track_indices cannot be empty")

    selected: set[int] = set(track_indices)
    if any(ti < 0 or ti >= len(mid.tracks) for ti in selected):
        raise ValueError(
            f"Invalid track index in {sorted(selected)} (tracks: 0..{len(mid.tracks)-1})"
        )

    # Ensure we keep tempo information: if none of the selected tracks has tempo,
    # add the first tempo track (commonly track 0).
    if not any(_track_has_tempo(mid.tracks[ti]) for ti in selected):
        for ti, tr in enumerate(mid.tracks):
            if _track_has_tempo(tr):
                selected.add(ti)
                break

    out_mid = mido_lib.MidiFile(type=1, ticks_per_beat=mid.ticks_per_beat)

    for ti in sorted(selected):
        out_track = mido_lib.MidiTrack()
        out_track.extend(mid.tracks[ti])
        out_mid.tracks.append(out_track)

    return out_mid


def _render_midi_to_wav(
    midi_path: Path,
    wav_path: Path,
    soundfont_path: str,
    sample_rate: int,
    gain: float,
    timeout_sec: int,
) -> None:
    cmd = [
        "fluidsynth",
        "-ni",
        "-g",
        str(gain),
        "-r",
        str(sample_rate),
        "-F",
        str(wav_path),
        str(soundfont_path),
        str(midi_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "FluidSynth failed")


def cmd_mixdown(args: argparse.Namespace) -> int:
    midi_path = Path(args.midi).resolve()
    output_wav = Path(args.output).resolve()

    if output_wav.exists() and not args.overwrite:
        raise SystemExit(
            f"❌ Output WAV already exists: {output_wav}\n"
            "   Use --overwrite to replace."
        )

    output_wav.parent.mkdir(parents=True, exist_ok=True)

    mid = mido_lib.MidiFile(str(midi_path))
    subset = _build_midi_subset(mid, args.tracks)

    # Save subset MIDI to a temp file
    with tempfile.NamedTemporaryFile(prefix="mido_mixdown_", suffix=".mid", delete=False) as f:
        tmp_midi_path = Path(f.name)
    subset.save(str(tmp_midi_path))

    # Determine timeout based on MIDI length
    midi_seconds = float(getattr(subset, "length", 0.0) or 0.0)
    timeout_sec = (
        int(args.timeout_sec)
        if args.timeout_sec is not None
        else max(30, int(midi_seconds * 3.0) + 10)
    )

    gen = MelodyGenerator(soundfont_path=args.soundfont)
    soundfont = gen.soundfont_path

    print("🎚️ MIDI mixdown -> WAV")
    print(f"  input:  {midi_path}")
    print(f"  tracks: {args.tracks}")
    print(f"  output: {output_wav}")
    print(f"  sf2:    {soundfont}")
    print(f"  timeout:{timeout_sec}s")

    try:
        _render_midi_to_wav(
            midi_path=tmp_midi_path,
            wav_path=output_wav,
            soundfont_path=soundfont,
            sample_rate=int(args.sample_rate),
            gain=float(args.gain),
            timeout_sec=timeout_sec,
        )

        if args.trim_silence:
            # Reuse the same trimming logic as in generator.py
            gen._trim_wav_silence(output_wav)  # type: ignore[attr-defined]

        print(f"✅ Mixdown ready: {output_wav}")
        return 0

    finally:
        if args.keep_midi:
            print(f"🧾 Temp MIDI kept: {tmp_midi_path}")
        else:
            tmp_midi_path.unlink(missing_ok=True)


def export_midi_as_wav_notes(
    midi_path: Path,
    name: str,
    output_root: Path,
    track_index: Optional[int],
    channel: Optional[int],
    instrument: Optional[int],
    duration_mode: str,
    fixed_duration: float,
    min_duration: float,
    max_duration: float,
    start_sec: float,
    end_sec: Optional[float],
    chord_policy: str,
    max_notes: Optional[int],
    overwrite: bool,
) -> Path:
    mid = mido_lib.MidiFile(str(midi_path))
    stats = _collect_track_stats(mid)

    chosen_track = track_index if track_index is not None else _select_default_track(stats)
    chosen_track_stats = next(s for s in stats if s.track_index == chosen_track)

    chosen_instrument = instrument
    if chosen_instrument is None:
        # If the track has program changes, pick the first one, otherwise None
        chosen_instrument = chosen_track_stats.programs[0] if chosen_track_stats.programs else None

    print("🎼 MIDI import")
    print(f"  file: {midi_path}")
    print(f"  name: {name}")
    print(f"  track: {chosen_track} ({chosen_track_stats.name or 'unnamed'})")
    print(f"  channel: {channel if channel is not None else 'auto'}")
    print(f"  instrument: {chosen_instrument if chosen_instrument is not None else 'default'}")
    print(f"  duration_mode: {duration_mode}")

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
        raise SystemExit("❌ No note events found (try a different track/channel).")

    out_dir = output_root / name
    if out_dir.exists() and any(out_dir.glob("*.wav")) and not overwrite:
        raise SystemExit(
            f"❌ Output folder already contains WAV files: {out_dir}\n"
            "   Use --overwrite to replace."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    generator = MelodyGenerator()

    ok = 0
    for i, ev in enumerate(events, start=1):
        if duration_mode == "midi":
            dur = _clamp(ev.duration_sec, min_duration, max_duration)
        elif duration_mode == "fixed":
            dur = fixed_duration
        else:
            raise ValueError(f"Unknown duration_mode: {duration_mode}")

        midi_file = out_dir / f"{i:02d}.mid"
        wav_file = out_dir / f"{i:02d}.wav"

        # Generate single-note MIDI and convert to WAV (trim silence inside)
        generator.generate_melody_midi(
            notes=[ev.note],
            file_path=midi_file,
            duration_sec=dur,
            instrument=chosen_instrument,
        )
        if generator.convert_midi_to_wav(midi_file, wav_file):
            ok += 1

    print(f"✅ Generated {ok}/{len(events)} WAV notes in: {out_dir}")
    return out_dir


def cmd_analyze(args: argparse.Namespace) -> int:
    mid = mido_lib.MidiFile(str(Path(args.midi)))
    stats = _collect_track_stats(mid)
    default_track = _select_default_track(stats)

    print(f"file: {args.midi}")
    print(f"type: {mid.type} tracks: {len(mid.tracks)} ticks_per_beat: {mid.ticks_per_beat}")
    print("")
    print("Tracks:")
    for s in stats:
        flag = " <==" if s.track_index == default_track else ""
        rng = (
            f"{s.note_min}-{s.note_max}"
            if s.note_min is not None and s.note_max is not None
            else "-"
        )
        print(
            f"  {s.track_index:02d}: "
            f"name={s.name!r} "
            f"notes={s.note_on_count} "
            f"poly={s.polyphonic_note_on_count} "
            f"programs={list(s.programs)} "
            f"channels={list(s.channels)} "
            f"range={rng}{flag}"
        )
    print("")
    print("Tip:")
    print("  Use --track N and optionally --channel CH (0-15, drums=9) when importing.")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root).resolve()
    export_midi_as_wav_notes(
        midi_path=Path(args.midi).resolve(),
        name=args.name,
        output_root=output_root,
        track_index=args.track,
        channel=args.channel,
        instrument=args.instrument,
        duration_mode=args.duration_mode,
        fixed_duration=args.fixed_duration,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        start_sec=args.start_sec,
        end_sec=args.end_sec,
        chord_policy=args.chord_policy,
        max_notes=args.max_notes,
        overwrite=args.overwrite,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MIDI tools for MIDO: analyze, import note packs, and render mixdowns."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_an = sub.add_parser("analyze", help="Show track/channel statistics for a MIDI file")
    p_an.add_argument("--midi", required=True, help="Path to .mid file")
    p_an.set_defaults(func=cmd_analyze)

    p_imp = sub.add_parser("import", help="Export MIDI notes to melodies/<name> as WAV files")
    p_imp.add_argument("--midi", required=True, help="Path to .mid file")
    p_imp.add_argument("--name", required=True, help="Output melody pack name (folder name)")
    p_imp.add_argument(
        "--output-root",
        default=str(Path(__file__).resolve().parent / "melodies"),
        help="Root output folder (default: mido/melodies)",
    )
    p_imp.add_argument(
        "--track",
        type=int,
        default=None,
        help="Track index to import (default: auto best track)",
    )
    p_imp.add_argument(
        "--channel",
        type=int,
        default=None,
        help="MIDI channel 0-15 to import (default: all non-drum channels)",
    )
    p_imp.add_argument(
        "--instrument",
        type=int,
        default=None,
        help="GM instrument program (0-127). Default: first program in track or generator default.",
    )
    p_imp.add_argument(
        "--duration-mode",
        choices=["midi", "fixed"],
        default="midi",
        help="How to set per-note duration in generated WAV files",
    )
    p_imp.add_argument(
        "--fixed-duration",
        type=float,
        default=0.25,
        help="Used when --duration-mode=fixed (seconds)",
    )
    p_imp.add_argument(
        "--min-duration",
        type=float,
        default=0.08,
        help="Clamp MIDI durations to at least this many seconds",
    )
    p_imp.add_argument(
        "--max-duration",
        type=float,
        default=1.20,
        help="Clamp MIDI durations to at most this many seconds",
    )
    p_imp.add_argument(
        "--start-sec",
        type=float,
        default=0.0,
        help="Start importing from this timestamp (seconds)",
    )
    p_imp.add_argument(
        "--end-sec",
        type=float,
        default=None,
        help="Stop importing after this timestamp (seconds)",
    )
    p_imp.add_argument(
        "--chord-policy",
        choices=["arpeggiate", "highest", "skip"],
        default="highest",
        help="How to handle multiple notes starting at the same time",
    )
    p_imp.add_argument(
        "--max-notes",
        type=int,
        default=120,
        help="Limit exported notes (safety for long MIDIs)",
    )
    p_imp.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing melody folder (if it already has WAVs)",
    )
    p_imp.set_defaults(func=cmd_import)

    p_mix = sub.add_parser(
        "mixdown",
        help="Render selected MIDI tracks into a single WAV file (2+ tracks mixed together)",
    )
    p_mix.add_argument("--midi", required=True, help="Path to .mid file")
    p_mix.add_argument(
        "--tracks",
        required=True,
        type=_parse_csv_int_list,
        help="Comma-separated track indices to include, e.g. '0,1'",
    )
    p_mix.add_argument("--output", required=True, help="Output WAV path")
    p_mix.add_argument(
        "--soundfont",
        default=None,
        help="Path to SoundFont .sf2 (default: auto-detect like generator.py)",
    )
    p_mix.add_argument("--sample-rate", type=int, default=44100, help="WAV sample rate")
    p_mix.add_argument("--gain", type=float, default=0.8, help="FluidSynth gain")
    p_mix.add_argument(
        "--timeout-sec",
        type=int,
        default=None,
        help="Conversion timeout (seconds). Default: auto based on MIDI length.",
    )
    p_mix.add_argument(
        "--trim-silence",
        action="store_true",
        help="Trim trailing silence (uses generator.py trimming logic)",
    )
    p_mix.add_argument(
        "--keep-midi",
        action="store_true",
        help="Keep the temporary subset MIDI used for rendering",
    )
    p_mix.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output WAV if it already exists",
    )
    p_mix.set_defaults(func=cmd_mixdown)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())


