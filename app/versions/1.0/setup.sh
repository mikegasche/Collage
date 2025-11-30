#!/bin/bash
# setup.sh
# macOS, Python venv + PySide6 + PyInstaller setup für Collage

set -e

# --- 1. Alte venv löschen ---
echo "==> Removing old venv..."
rm -rf venv

# --- 2. Neue venv erstellen ---
echo "==> Creating new venv..."
python3 -m venv venv
source venv/bin/activate

# --- 3. Pip, setuptools, wheel upgraden ---
echo "==> Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# --- 4. Pakete installieren ---
echo "==> Installing required packages..."
pip install PySide6 pillow pyinstaller

# --- 5. Kontrolle ---
echo "==> Checking installed packages..."
python -m pip show PySide6
python -m pip show pillow
python -m pip show pyinstaller

echo "==> Setup complete. Now you can run ./make.sh to build the app with PySide6."
