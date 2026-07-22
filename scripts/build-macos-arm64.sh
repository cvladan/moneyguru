#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
PYTHON=${PYTHON:-"$PROJECT_ROOT/.venv/bin/python"}

cd "$PROJECT_ROOT"

if [ "$(uname -m)" != "arm64" ]; then
    echo "This package must be built on Apple Silicon." >&2
    exit 1
fi

if [ ! -x "$PYTHON" ]; then
    echo "Python is not executable: $PYTHON" >&2
    exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required to locate the native build dependencies." >&2
    exit 1
fi

BREW_PREFIX=$(brew --prefix)
export PATH="$BREW_PREFIX/opt/gettext/bin:$BREW_PREFIX/bin:/usr/bin:/bin:$PATH"
export PKG_CONFIG_PATH="$(brew --prefix sqlite)/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
export PYINSTALLER_CONFIG_DIR="$PROJECT_ROOT/build/pyinstaller-cache"

for command_name in codesign ditto file make msgfmt pkg-config shasum; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Required command not found: $command_name" >&2
        exit 1
    fi
done

"$PYTHON" - <<'PY'
import platform
import sys

import PyInstaller
import PyQt5

if platform.machine() != "arm64":
    raise SystemExit("The build Python must be arm64.")
if sys.version_info[:2] != (3, 12):
    raise SystemExit("The package must be built with Python 3.12.")
PY

make clean
make PYTHON="$PYTHON"
"$PYTHON" -m PyInstaller --noconfirm --clean moneyGuru.spec

APP_PATH="$PROJECT_ROOT/dist/moneyGuru.app"
APP_EXECUTABLE="$APP_PATH/Contents/MacOS/moneyGuru"
VERSION=$("$PYTHON" -c 'from core import __version__; print(__version__)')
ARCHIVE_PATH="$PROJECT_ROOT/dist/moneyGuru-$VERSION-arm64.zip"

if [ ! -x "$APP_EXECUTABLE" ]; then
    echo "The application executable was not created." >&2
    exit 1
fi

NON_ARM64_FILES=$(find "$APP_PATH" -type f -exec file {} + | awk '/Mach-O/ && $0 !~ /arm64/ { print }')
if [ -n "$NON_ARM64_FILES" ]; then
    echo "The application contains non-arm64 Mach-O files:" >&2
    echo "$NON_ARM64_FILES" >&2
    exit 1
fi

codesign --verify --deep --strict "$APP_PATH"

SMOKE_LOG="$PROJECT_ROOT/build/macos-arm64-smoke.log"
QT_QPA_PLATFORM=offscreen "$APP_EXECUTABLE" >"$SMOKE_LOG" 2>&1 &
SMOKE_PID=$!
sleep 5
if ! kill -0 "$SMOKE_PID" 2>/dev/null; then
    wait "$SMOKE_PID" || true
    echo "The packaged application exited during the launch test." >&2
    sed -n '1,160p' "$SMOKE_LOG" >&2
    exit 1
fi
kill "$SMOKE_PID"
wait "$SMOKE_PID" 2>/dev/null || true

ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ARCHIVE_PATH"

echo "Package created: $ARCHIVE_PATH"
shasum -a 256 "$ARCHIVE_PATH"
