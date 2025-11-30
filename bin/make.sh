#!/bin/bash
# make.sh - Build Collage.app (macOS Intel/ARM64) using PyInstaller + pyenc

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- 1. Set exact Python version ---
pyenv local 3.11.8
echo "Using Python $(python --version)"

# --- 2. Activate virtual environment ---
source venv/bin/activate

# --- 3. Remove old builds ---
rm -rf build dist Collage.spec

# --- 4. Optional: encrypt source with pyenc ---
# pyenc encrypt --in app --out build/encrypted_app

# --- 5. PyInstaller build ---
pyinstaller \
    --name "Collage" \
    --windowed \
    --icon "app/resources/app_icon.icns" \
    --add-data "app/resources:resources" \
    app/collage_gui.py

echo "==> Build finished. Check dist/Collage.app"
