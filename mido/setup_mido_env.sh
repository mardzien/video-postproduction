#!/bin/bash

# 🎵 MIDO Sound Generator - Setup Environment Script
# Automatyczne tworzenie mini środowiska dla modułu MIDO

set -e  # Przerwij przy błędzie

echo "🎵 MIDO Sound Generator - Setup Mini Environment"
echo "=================================================="

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Funkcja do logowania
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Sprawdź czy jesteśmy w folderze mido
if [ ! -f "requirements.txt" ] || [ ! -f "generator.py" ]; then
    log_error "Uruchom skrypt z folderu mido!"
    exit 1
fi

log_info "Sprawdzanie wymagań systemowych..."

# Sprawdź Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 nie jest zainstalowany!"
    exit 1
fi
log_success "Python3 dostępny: $(python3 --version)"

# Sprawdź pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 nie jest zainstalowany!"
    exit 1
fi
log_success "pip3 dostępny"

# Sprawdź FluidSynth
if ! command -v fluidsynth &> /dev/null; then
    log_warning "FluidSynth nie znaleziony w PATH"
    log_info "Instalacja na Fedora: sudo dnf install fluidsynth fluid-soundfont-gm"
    log_info "Instalacja na Ubuntu: sudo apt install fluidsynth fluid-soundfont-gm"
else
    log_success "FluidSynth dostępny: $(fluidsynth --version | head -1)"
fi

# Sprawdź SoundFont
SOUNDFONT_PATHS=(
    "/usr/share/soundfonts/FluidR3_GM.sf2"
    "/usr/share/soundfonts/default.sf2"
    "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls"
)

SOUNDFONT_FOUND=false
for sf_path in "${SOUNDFONT_PATHS[@]}"; do
    if [ -f "$sf_path" ]; then
        log_success "SoundFont znaleziony: $sf_path"
        SOUNDFONT_FOUND=true
        break
    fi
done

if [ "$SOUNDFONT_FOUND" = false ]; then
    log_warning "SoundFont nie znaleziony!"
    log_info "Zainstaluj SoundFont poleceniem:"
    log_info "  Fedora: sudo dnf install fluid-soundfont-gm"
    log_info "  Ubuntu: sudo apt install fluid-soundfont-gm"
fi

echo ""
log_info "Tworzenie wirtualnego środowiska MIDO..."

# Utwórz wirtualne środowisko
if [ -d "mido_env" ]; then
    log_warning "Środowisko mido_env już istnieje - usuwam stare"
    rm -rf mido_env
fi

python3 -m venv mido_env
log_success "Wirtualne środowisko utworzone: mido_env/"

# Aktywuj środowisko
source mido_env/bin/activate
log_success "Środowisko aktywowane"

# Zaktualizuj pip
log_info "Aktualizacja pip..."
pip install --upgrade pip

# Zainstaluj zależności
log_info "Instalacja zależności MIDO..."
pip install -r requirements.txt
log_success "Zależności zainstalowane"

# Zainstaluj moduł w trybie development
log_info "Instalacja modułu MIDO w trybie development..."
pip install -e .
log_success "Moduł MIDO zainstalowany"

# Sprawdź instalację
log_info "Sprawdzanie instalacji..."
python -c "import mido; print('✅ mido:', mido.__version__)" 2>/dev/null || log_warning "mido nie działa"
python -c "import pygame; print('✅ pygame:', pygame.version.ver)" 2>/dev/null || log_warning "pygame nie działa"
python -c "import midi2audio; print('✅ midi2audio: OK')" 2>/dev/null || log_warning "midi2audio nie działa"
python -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>/dev/null || log_warning "numpy nie działa"

# Utwórz foldery
mkdir -p melodies
mkdir -p logs
log_success "Foldery robocze utworzone"

echo ""
echo -e "${PURPLE}🎵 MIDO Sound Generator - Setup Complete! 🎵${NC}"
echo "=============================================="
echo ""
echo "📁 Wirtualne środowisko: mido_env/"
echo "🎼 Folder melodii: melodies/"
echo "📊 Logi: logs/"
echo ""
echo "🚀 Aktywacja środowiska:"
echo "   source mido_env/bin/activate"
echo ""
echo "🎵 Dostępne komendy:"
echo "   make help           - pomoc"
echo "   make generate       - generuj wszystkie melodie"
echo "   make list-melodies  - pokaż dostępne melodie"
echo "   make viral-hits     - generuj top viralne hity"
echo "   make play           - odtwórz melodie"
echo ""
echo "🎯 Szybki start:"
echo "   source mido_env/bin/activate"
echo "   make viral-hits"
echo "   make play"
echo ""
log_success "Setup zakończony! Gotowe do generowania muzyki! 🎶"
