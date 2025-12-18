#!/bin/bash
# Batch process all recordings with rotating templates
# Usage: ./batch_process_shorts.sh

set -e

RECORDINGS_DIR="recordings"
VENV_PYTHON="venv/bin/python"

# Templates to rotate through (for variety in sounds)
TEMPLATES=("christmas" "mario_challenge" "epic_imperial" "basic_minimal")

# Common text theme - "3 seconds before freezing"
TEXTS=(
    "⏱️ 3 seconds before ❄️\nWill it escape?"
    "⏰ Each ball has 3s ❄️\nBefore freezing!"
    "🕐 3 seconds left! ❄️\nCan you escape?"
    "⏱️ Freezing in 3s! ❄️\nWill you make it?"
)

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🎬 Batch Processing YouTube Shorts"
echo "=================================="
echo ""

# Find all .webm files
WEBM_FILES=($(ls -1 ${RECORDINGS_DIR}/*.webm 2>/dev/null || true))
TOTAL=${#WEBM_FILES[@]}

if [ $TOTAL -eq 0 ]; then
    echo "❌ No .webm files found in ${RECORDINGS_DIR}/"
    exit 1
fi

echo "📊 Found ${TOTAL} videos to process"
echo ""

PROCESSED=0
FAILED=0

for i in "${!WEBM_FILES[@]}"; do
    VIDEO="${WEBM_FILES[$i]}"
    BASENAME=$(basename "$VIDEO" .webm)
    
    # Rotate through templates for variety
    TEMPLATE_IDX=$((i % ${#TEMPLATES[@]}))
    TEMPLATE="${TEMPLATES[$TEMPLATE_IDX]}"
    
    # Rotate through text variations
    TEXT_IDX=$((i % ${#TEXTS[@]}))
    TEXT="${TEXTS[$TEXT_IDX]}"
    
    echo -e "${BLUE}[$(($i + 1))/${TOTAL}]${NC} Processing: ${BASENAME}"
    echo "   📋 Template: ${TEMPLATE}"
    echo "   📝 Text: $(echo -e "$TEXT" | head -1)..."
    
    # Run shorts command
    if $VENV_PYTHON -m src.cli shorts \
        --input "$VIDEO" \
        --template "$TEMPLATE" \
        --text "$TEXT" \
        --auto-number \
        2>&1 | grep -E "(Processing|Template|Audio|Overlay|complete|Error)" || true; then
        
        echo -e "   ${GREEN}✅ Success${NC}"
        PROCESSED=$((PROCESSED + 1))
    else
        echo -e "   ${YELLOW}⚠️ Failed${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
done

echo "=================================="
echo "🎉 Batch processing complete!"
echo "   ✅ Processed: ${PROCESSED}"
echo "   ⚠️  Failed: ${FAILED}"
echo "   📁 Output: final_recordings/"
echo ""

