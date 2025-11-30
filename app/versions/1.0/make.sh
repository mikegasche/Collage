#!/bin/bash
# make.sh - build Collage.app with PySide6

set -e

# --- Activate virtual environment ---
source venv/bin/activate

# --- Remove old builds ---
rm -rf build dist Collage.spec

# --- PyInstaller Build ---
pyinstaller \
    --name "Collage" \
    --windowed \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    collage_gui.py

echo "==> Build finished. Check dist/Collage.app"
