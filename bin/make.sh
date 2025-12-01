#!/bin/bash
# ------------------------------------------------------------------------------
# make.sh - Build Collage.app (macOS Intel/ARM64) using PyInstaller + pyenc
# macOS (Intel/ARM64)
# ------------------------------------------------------------------------------

set -e

# --- 0. Detect architecture ---
ARCH=$(uname -m)
echo "==> Detected architecture: $ARCH"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- 1. Set exact Python version depending on architecture ---
if [ "$ARCH" = "arm64" ]; then
    # ARM / Apple Silicon → Python 3.12.x (see setup.sh)
    PYTHON_VERSION="$(pyenv install -l | grep -E '^\s*3\.12\.' | tail -1 | tr -d ' ')"
    echo "==> macOS ARM detected → using Python $PYTHON_VERSION (3.12.x)"
else
    # Intel → 3.11.x
    PYTHON_VERSION="3.11.9"
    echo "==> Intel mac detected → using Python $PYTHON_VERSION"
fi

# --- 2. Set pyenv local ---
pyenv local "$PYTHON_VERSION"

# Activate shims so that python/pyinstaller can be found
export PATH="$HOME/.pyenv/shims:$PATH"

echo "Using Python $(python --version)"

# --- 3. Activate virtual environment ---
if [ ! -d "venv" ]; then
    echo "ERROR: virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

# --- 4. Remove old builds ---
rm -rf build dist Collage.spec

# --- 5. PyInstaller build ---
pyinstaller \
    --name "Collage" \
    --windowed \
    --icon "app/resources/app_icon.icns" \
    --add-data "app/resources:resources" \
    app/collage_gui.py

echo "==> Build finished. Check dist/Collage.app"
