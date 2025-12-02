.PHONY: help setup-env setup install clean generate play check format

help:  ## Pokazuje pomoc dla modułu MIDO
	@echo "🎵 MIDO Sound Generator - Dostępne komendy:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup-env:  ## Tworzy kompletne mini środowisko MIDO (wirtualne env + zależności)
	@echo "🎵 Tworzenie mini środowiska MIDO..."
	@chmod +x setup_mido_env.sh
	@./setup_mido_env.sh
	@echo "✅ Mini środowisko MIDO gotowe!"

setup:  ## Instaluje zależności modułu MIDO (wymaga aktywnego env)
	@echo "🔧 Instaluję zależności MIDO..."
	pip install -r requirements.txt
	@echo "✅ Zależności MIDO zainstalowane"

install:  ## Instaluje moduł MIDO w trybie development
	pip install -e .

clean:  ## Czyści pliki tymczasowe MIDO
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.mid" -delete  # Usuń tymczasowe pliki MIDI
	@echo "🗑️ Pliki tymczasowe MIDO wyczyszczone"

generate:  ## Generuje melodie WAV z definicji MIDI
	@echo "🎼 Generowanie melodii..."
	python generator.py
	@echo "✅ Melodie wygenerowane w folderze melodies/"

generate-melody:  ## Generuje konkretną melodię (użyj: make generate-melody MELODY=tetris)
	@if [ -z "$(MELODY)" ]; then \
		echo "❌ Podaj nazwę melodii: make generate-melody MELODY=nazwa"; \
		echo "🎵 Dostępne melodie: tetris, nokia, mario, imperial_march, happy_birthday, twinkle, jingle_bells"; \
		exit 1; \
	fi
	@echo "🎼 Generowanie melodii: $(MELODY)"
	python -c "from generator import MelodyGenerator; from config import MELODIES; \
	           gen = MelodyGenerator(); \
	           result = gen.generate_melody('$(MELODY)', MELODIES.get('$(MELODY)', [])); \
	           print('✅ Melodia $(MELODY) wygenerowana!' if result else '❌ Błąd generacji melodii $(MELODY)')"

list-melodies:  ## Pokazuje wszystkie dostępne melodie
	@echo "🎵 Dostępne viralne melodie MIDO:"
	@echo ""
	@echo "🎮 tetris          - Tetris Theme (Korobeiniki) - MEGA VIRAL!"
	@echo "📱 nokia           - Nokia Ringtone - Nostalgiczny HIT!"
	@echo "🎬 imperial_march  - Imperial March (Star Wars) - Epicki!"
	@echo "🍄 mario           - Super Mario Bros - Legendarny!"
	@echo "🎂 happy_birthday  - Happy Birthday - Klasyk!"
	@echo "⭐ twinkle         - Twinkle Twinkle Little Star - Dziecięcy hit!"
	@echo "🎄 jingle_bells    - Jingle Bells - Świąteczny hit!"
	@echo "🕵️ mission_impossible - Mission Impossible - Szpiegowski hit!"
	@echo "🐾 pink_panther    - Pink Panther - Jazzowy hit!"
	@echo "🎼 fur_elise       - Für Elise (Beethoven) - Klasyczny hit!"
	@echo "💍 canon_in_d      - Canon in D (Pachelbel) - Ślubny hit!"
	@echo "🎸 smoke_on_water  - Smoke on the Water (Deep Purple) - Rockowy hit!"
	@echo "🕺 staying_alive   - Staying Alive (Bee Gees) - Disco hit!"
	@echo "🎺 saints          - When the Saints Go Marching In - Jazzowy standard!"
	@echo "💖 titanic         - My Heart Will Go On (Titanic) - Romantyczny hit!"
	@echo "👻 ghost_intro     - Oryginalny ghost intro"
	@echo ""
	@echo "Użycie: make generate-melody MELODY=nazwa_melodii"

viral-hits:  ## Generuje najlepsze viralne hity (tetris, nokia, mario, imperial_march)
	@echo "🔥 Generowanie MEGA VIRALNYCH HITÓW!"
	@echo ""
	@make generate-melody MELODY=tetris
	@make generate-melody MELODY=nokia
	@make generate-melody MELODY=mario
	@make generate-melody MELODY=imperial_march
	@echo ""
	@echo "🎉 VIRALNE HITY GOTOWE! Sprawdź folder melodies/"

play:  ## Odtwarza wygenerowane melodie
	@echo "🔊 Odtwarzanie melodii..."
	python main.py

test-soundfont:  ## Sprawdza dostępność SoundFont
	@echo "🔍 Sprawdzanie SoundFont..."
	@if [ -f "/usr/share/soundfonts/FluidR3_GM.sf2" ]; then \
		echo "✅ SoundFont FluidR3_GM.sf2 dostępny"; \
	elif [ -f "/usr/share/soundfonts/default.sf2" ]; then \
		echo "✅ SoundFont default.sf2 dostępny"; \
	else \
		echo "❌ SoundFont nie znaleziony. Zainstaluj fluidsynth-soundfont:"; \
		echo "   Fedora: sudo dnf install fluid-soundfont-gm"; \
		echo "   Ubuntu: sudo apt install fluid-soundfont-gm"; \
	fi

check:  ## Sprawdza jakość kodu MIDO
	@echo "🔍 Sprawdzanie kodu MIDO..."
	ruff check .
	mypy . --ignore-missing-imports
	@echo "✅ Sprawdzenie zakończone"

format:  ## Formatuje kod MIDO
	@echo "🎨 Formatowanie kodu MIDO..."
	ruff format .
	@echo "✅ Formatowanie zakończone"

info:  ## Pokazuje informacje o module MIDO
	@echo "🎵 MIDO Sound Generator"
	@echo "📁 Lokalizacja: $(PWD)"
	@echo "🐍 Python: $(shell python --version)"
	@echo "📦 Zależności:"
	@pip list | grep -E "(mido|pygame|midi2audio)" || echo "   Brak zainstalowanych zależności"
	@echo "🎼 Dostępne melodie:"
	@ls -la melodies/ 2>/dev/null || echo "   Brak wygenerowanych melodii"

play-melody:  ## Odtwarza konkretną melodię (użyj: make play-melody MELODY=tetris)
	@if [ -z "$(MELODY)" ]; then \
		echo "❌ Podaj nazwę melodii: make play-melody MELODY=nazwa"; \
		echo "🎵 Dostępne melodie: tetris, nokia, mario, imperial_march, happy_birthday"; \
		exit 1; \
	fi
	@if [ ! -d "melodies/$(MELODY)" ]; then \
		echo "📂 Melodia $(MELODY) nie jest wygenerowana. Generuję..."; \
		make generate-melody MELODY=$(MELODY); \
	fi
	@echo "🔊 Odtwarzanie melodii: $(MELODY)"
	python -c "from main import MelodyPlayer; player = MelodyPlayer('$(MELODY)'); player.run()"
