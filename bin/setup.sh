#!/bin/bash
# ------------------------------------------------------------------------------
# setup.sh
# macOS (Intel/ARM64) - Python env, venv, PySide6 + Pillow + PyInstaller/pyenc
# ------------------------------------------------------------------------------

set -e

# --- 0. Detect architecture ---
ARCH=$(uname -m)
echo "==> Detected architecture: $ARCH"

# --- 1. Determine project root (bin/ is parallel to app/) ---
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- 2. Ensure pyenv is installed ---
if ! command -v pyenv >/dev/null 2>&1; then
  echo "ERROR: pyenv not found. Install pyenv first."
  exit 1
fi

# --- 3. Clean up old ENV variables + patches ---
unset PYTHON_CONFIGURE_OPTS
unset CONFIGURE_OPTS
unset LDFLAGS
unset CPPFLAGS
unset PKG_CONFIG_PATH

# pyenv patch cleanup (if present)
rm -rf ~/.pyenv/patches 2>/dev/null || true

# --- 4. Python version depending on architecture ---
if [ "$ARCH" = "arm64" ]; then
    # ARM / Apple Silicon / macOS 15 → use Python 3.12.x
    PYTHON_VERSION="$(pyenv install -l | grep -E '^\s*3\.12\.' | tail -1 | tr -d ' ')"
    echo "==> macOS ARM detected → using Python $PYTHON_VERSION (3.12.x)"
else
    # Intel → keep previous version
    PYTHON_VERSION="3.11.9"
    echo "==> Intel mac detected → using Python $PYTHON_VERSION"
fi

echo "==> Installing Python $PYTHON_VERSION via pyenv..."
pyenv install -s "$PYTHON_VERSION"
pyenv local "$PYTHON_VERSION"

# Activate shims so that python/pip etc. can be found
export PATH="$HOME/.pyenv/shims:$PATH"

# --- 5. Remove old venv ---
echo "==> Removing old venv..."
rm -rf venv

# --- 6. Create new venv ---
echo "==> Creating new venv..."
python -m venv venv
source venv/bin/activate

# --- 7. Upgrade pip, setuptools, wheel ---
echo '==> Upgrading pip, setuptools, wheel...'
pip install --upgrade pip setuptools wheel

# --- 8. Install required packages ---
echo "==> Installing required packages..."
pip install PySide6 pillow pyinstaller

# --- 9. Check installed packages ---
echo "==> Installed packages:"
python -m pip show PySide6
python -m pip show pillow
python -m pip show pyinstaller
python --version

echo "==> Setup complete. You can now run ./bin/make.sh to build the app."
