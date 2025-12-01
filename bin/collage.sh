#!/bin/sh

# Arbeitsverzeichnis auf Projekt-Root
cd "$(dirname "$0")/.." || exit 1

# Activate venv
source venv/bin/activate

# Run Collage CLI with exact python in venv
python app/collage.py \
  --input "/Users/Mike/Pictures/Familie/Mams/3 AI/A" \
  --width 2560 \
  --height 1440 \
  --bgcolor transparent \
  --output collage.png \
  --max-rotation 1 \
  --overlap-factor 0.05 \
  --rows 2 \
  --iterations 20
