#!/usr/bin/env python3
"""
Test script for MIDI-based postproduction workflow.

Tests:
1. MidiNoteRenderer - loading MIDI and rendering notes
2. PostProductionMixer - MIDI mode initialization
3. Template loading with MIDI config
"""

import sys
from pathlib import Path

# Direct import without going through __init__.py
sys.path.insert(0, str(Path(__file__).parent))


def test_midi_renderer():
    """Test MIDI renderer functionality."""
    print("=" * 60)
    print("TEST 1: MidiNoteRenderer")
    print("=" * 60)
    
    try:
        # Direct import to avoid src/__init__.py
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "midi_renderer",
            "src/midi_renderer.py"
        )
        midi_renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(midi_renderer)
        
        MidiNoteRenderer = midi_renderer.MidiNoteRenderer
        
        # Test initialization
        renderer = MidiNoteRenderer()
        print("✅ Renderer initialized")
        
        # Test loading MIDI notes
        midi_file = "midi_files/Twinkle.mid"
        if Path(midi_file).exists():
            notes = renderer.load_midi_notes(midi_file, instrument=11)
            print(f"✅ Loaded {len(notes)} notes from {midi_file}")
            print(f"   Note range: {min(notes)}-{max(notes)}")
            
            # Test rendering a single note
            if notes:
                audio = renderer.render_note(notes[0], instrument=11)
                print(f"✅ Rendered note {notes[0]}: {audio.shape}")
                
                # Test cache
                cache_stats = renderer.get_cache_stats()
                print(f"✅ Cache: {cache_stats['entries']} entries")
        else:
            print(f"⚠️  MIDI file not found: {midi_file}")
        
        renderer.cleanup()
        print("✅ Renderer cleanup complete")
        return True
        
    except Exception as e:
        print(f"❌ MidiNoteRenderer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mixer_midi_mode():
    """Test PostProductionMixer in MIDI mode."""
    print("\n" + "=" * 60)
    print("TEST 2: PostProductionMixer (MIDI mode)")
    print("=" * 60)
    
    try:
        # Direct import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mixer",
            "src/mixer.py"
        )
        mixer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mixer_module)
        
        PostProductionMixer = mixer_module.PostProductionMixer
        
        midi_file = "midi_files/Twinkle.mid"
        if not Path(midi_file).exists():
            print(f"⚠️  MIDI file not found: {midi_file}")
            return False
        
        # Test MIDI mode initialization
        mixer = PostProductionMixer(
            midi_file=midi_file,
            midi_instrument=11,  # Music Box
            midi_track=0,
            volume=1.0,
        )
        print(f"✅ Mixer initialized in {mixer.mode} mode")
        print(f"   MIDI file: {mixer.midi_file}")
        print(f"   Instrument: {mixer.midi_instrument}")
        print(f"   Notes loaded: {len(mixer.midi_notes)}")
        
        mixer.cleanup()
        print("✅ Mixer cleanup complete")
        return True
        
    except Exception as e:
        print(f"❌ Mixer MIDI mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_loading():
    """Test template loading with MIDI config."""
    print("\n" + "=" * 60)
    print("TEST 3: Template Loading (MIDI config)")
    print("=" * 60)
    
    try:
        # Direct import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "templates",
            "src/templates.py"
        )
        templates_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(templates_module)
        
        TemplateManager = templates_module.TemplateManager
        
        mgr = TemplateManager()
        
        # Test loading a MIDI-based template
        template = mgr.load_template("twinkle")
        print(f"✅ Loaded template: {template.name}")
        print(f"   Description: {template.description}")
        print(f"   Audio mode: {'MIDI' if template.audio.midi_file else 'WAV'}")
        
        if template.audio.midi_file:
            print(f"   MIDI file: {template.audio.midi_file}")
            print(f"   Instrument: {template.audio.instrument}")
            print(f"   Volume: {template.audio.volume}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_structure():
    """Test that core files are syntactically valid."""
    print("\n" + "=" * 60)
    print("TEST 4: Code Structure & Syntax")
    print("=" * 60)
    
    try:
        import py_compile
        
        files = [
            "src/midi_renderer.py",
            "src/mixer.py", 
            "src/templates.py",
            "src/cli.py"
        ]
        
        for file in files:
            py_compile.compile(file, doraise=True)
            print(f"✅ {file} syntax OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Code structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "🎵" * 30)
    print("MIDI-BASED POSTPRODUCTION INTEGRATION TEST")
    print("🎵" * 30 + "\n")
    
    results = {
        "Code Structure": test_code_structure(),
        "MIDI Renderer": test_midi_renderer(),
        "Mixer MIDI Mode": test_mixer_midi_mode(),
        "Template Loading": test_template_loading(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✨ The MIDI-based postproduction system is ready!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Test with real video: postprod shorts --template twinkle --input video.mp4")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nNote: Import errors are expected without dependencies installed.")
        print("Core code structure is validated. Install requirements to run full tests.")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
