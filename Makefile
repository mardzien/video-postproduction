# Video Postproduction Makefile
# =============================
#
# Usage:
#   make audio INPUT=video.mp4
#   make overlay INPUT=video.mp4 TEXT="Level 3"
#   make postprocess INPUT=video.mp4 TEXT="Level 3"
#
# With custom sounds:
#   make audio INPUT=video.mp4 SOUNDS_DIR=mido/melodies/mario/

SHELL := /bin/bash

# Virtual environment
VENV_DIR := venv
VENV_BIN := $(VENV_DIR)/bin
PY := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip

# Directories
RECORDINGS := recordings
FINAL := final_recordings
SOUNDS := sounds

# Default values
INPUT ?=
TEXT ?=
OUTPUT ?=
SOUNDS_DIR ?= $(SOUNDS)
VOLUME ?= 0.7
CLEANUP ?=

# Mido defaults
MELODY ?= imperial_march

# ============================================================================
# SETUP
# ============================================================================

.PHONY: env
env: $(VENV_DIR)/.created

$(VENV_DIR)/.created:
	@echo "🔧 Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $@

.PHONY: install
install: env
	@echo "✅ Environment ready"

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ============================================================================
# POSTPRODUCTION COMMANDS
# ============================================================================

.PHONY: audio
audio: env
	@if [ -z "$(INPUT)" ]; then echo "❌ ERROR: INPUT required. Usage: make audio INPUT=video.mp4"; exit 1; fi
	$(PY) -m src.cli audio \
		--input "$(INPUT)" \
		$(if $(OUTPUT),--output "$(OUTPUT)",) \
		--sounds-dir "$(SOUNDS_DIR)" \
		--volume $(VOLUME) \
		$(if $(CLEANUP),--cleanup,)

.PHONY: overlay
overlay: env
	@if [ -z "$(INPUT)" ]; then echo "❌ ERROR: INPUT required. Usage: make overlay INPUT=video.mp4 TEXT=\"Hello\""; exit 1; fi
	@if [ -z "$(TEXT)" ]; then echo "❌ ERROR: TEXT required. Usage: make overlay INPUT=video.mp4 TEXT=\"Hello\""; exit 1; fi
	$(PY) -m src.cli overlay \
		--input "$(INPUT)" \
		--text "$(TEXT)" \
		$(if $(OUTPUT),--output "$(OUTPUT)",)

.PHONY: postprocess
postprocess: env
	@if [ -z "$(INPUT)" ]; then echo "❌ ERROR: INPUT required. Usage: make postprocess INPUT=video.mp4 TEXT=\"Hello\""; exit 1; fi
	@if [ -z "$(TEXT)" ]; then echo "❌ ERROR: TEXT required. Usage: make postprocess INPUT=video.mp4 TEXT=\"Hello\""; exit 1; fi
	$(PY) -m src.cli full \
		--input "$(INPUT)" \
		--text "$(TEXT)" \
		$(if $(OUTPUT),--output "$(OUTPUT)",) \
		--sounds-dir "$(SOUNDS_DIR)" \
		--volume $(VOLUME) \
		$(if $(CLEANUP),--cleanup,)

# Alias for postprocess
.PHONY: full
full: postprocess

# ============================================================================
# MIDO - MELODY GENERATION
# ============================================================================

.PHONY: mido-env
mido-env:
	@if [ ! -d "mido/mido_env" ]; then \
		echo "🔧 Setting up mido environment..."; \
		cd mido && bash setup_mido_env.sh; \
	fi

.PHONY: generate-melody
generate-melody: mido-env
	@echo "🎵 Generating melody: $(MELODY)"
	cd mido && ./mido_env/bin/python main.py --melody $(MELODY)

.PHONY: list-melodies
list-melodies:
	@echo "🎵 Available melodies:"
	@ls -1 mido/melodies/ 2>/dev/null || echo "   (no melodies generated yet)"

# ============================================================================
# BATCH PROCESSING
# ============================================================================

.PHONY: batch-audio
batch-audio: env
	@echo "🎬 Processing all videos in $(RECORDINGS)/"
	@for f in $(RECORDINGS)/*_video_*.mp4; do \
		if [ -f "$$f" ]; then \
			echo "→ $$f"; \
			$(PY) -m src.cli audio --input "$$f" --sounds-dir "$(SOUNDS_DIR)"; \
		fi \
	done

.PHONY: batch-overlay
batch-overlay: env
	@if [ -z "$(TEXT)" ]; then echo "❌ ERROR: TEXT required."; exit 1; fi
	@echo "🎬 Adding overlay to all videos in $(FINAL)/"
	@for f in $(FINAL)/*_final_*.mp4; do \
		if [ -f "$$f" ]; then \
			echo "→ $$f"; \
			$(PY) -m src.cli overlay --input "$$f" --text "$(TEXT)"; \
		fi \
	done

# ============================================================================
# UTILITIES
# ============================================================================

.PHONY: help
help:
	@echo "Video Postproduction"
	@echo "===================="
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Create virtual environment and install deps"
	@echo "  make clean           - Remove venv and cache files"
	@echo ""
	@echo "Postproduction:"
	@echo "  make audio INPUT=video.mp4 [SOUNDS_DIR=sounds/]"
	@echo "                       - Mix collision audio into video"
	@echo ""
	@echo "  make overlay INPUT=video.mp4 TEXT=\"Hello\""
	@echo "                       - Add text overlay to video"
	@echo ""
	@echo "  make postprocess INPUT=video.mp4 TEXT=\"Hello\" [SOUNDS_DIR=sounds/]"
	@echo "                       - Full postproduction (audio + overlay)"
	@echo ""
	@echo "Mido (melody generator):"
	@echo "  make generate-melody MELODY=imperial_march"
	@echo "                       - Generate melody WAV files"
	@echo "  make list-melodies   - Show available melodies"
	@echo ""
	@echo "Batch:"
	@echo "  make batch-audio     - Process all videos in recordings/"
	@echo "  make batch-overlay TEXT=\"Hello\""
	@echo "                       - Add overlay to all in final_recordings/"
	@echo ""
	@echo "Options:"
	@echo "  INPUT=path           - Input video file or glob pattern"
	@echo "  OUTPUT=path          - Output file path"
	@echo "  TEXT=\"text\"          - Overlay text (supports emoji)"
	@echo "  SOUNDS_DIR=path      - Directory with WAV sounds"
	@echo "  VOLUME=0.7           - Audio volume (0.0-1.0)"
	@echo "  CLEANUP=1            - Delete source files after"

.DEFAULT_GOAL := help

