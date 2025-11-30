#!/bin/bash
# ------------------------------------------------------------------------------
# setup.sh
# macOS (Intel/ARM64) - Python 3.11.8, venv, PySide6 + Pillow + PyInstaller/pyenc
# ------------------------------------------------------------------------------

set -e

# --- 1. Projekt-Root bestimmen (bin/ liegt parallel zu app/) ---
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- 2. pyenv sicherstellen ---
if ! command -v pyenv >/dev/null 2>&1; then
  echo "ERROR: pyenv not found. Install pyenv first."
  exit 1
fi

PYTHON_VERSION="3.11.9"   # konkrete Version fix
echo "==> Setting local Python version to $PYTHON_VERSION via pyenv..."
pyenv install -s "$PYTHON_VERSION"
pyenv local "$PYTHON_VERSION"

# --- 3. Alte venv löschen ---
echo "==> Removing old venv..."
rm -rf venv

# --- 4. Neue venv erstellen ---
echo "==> Creating new venv..."
python -m venv venv
source venv/bin/activate

# --- 5. pip, setuptools, wheel upgraden ---
echo "==> Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# --- 6. Notwendige Pakete installieren ---
echo "==> Installing required packages..."
pip install PySide6 pillow pyinstaller pycryptodome

# --- 7. Kontrolle ---
echo "==> Installed packages:"
python -m pip show PySide6
python -m pip show pillow
python -m pip show pyinstaller
python --version

echo "==> Setup complete. You can now run ./bin/make.sh to build the app."
