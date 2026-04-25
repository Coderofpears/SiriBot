#!/bin/bash
# SiriBot Unified Build Script - Builds for all platforms
# Usage: ./setup/build.sh [--platform macos|windows|linux|all]

set -e

VERSION="1.0.0-beta.1"
PLATFORM="${1:-all}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              SiriBot Build System v${VERSION}                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create build directory
mkdir -p build

build_macos() {
    echo "[macOS] Building DMG..."
    ./setup/build_macos_dmg.sh
    echo "[macOS] ✓ DMG created"
}

build_windows() {
    echo "[Windows] Building EXE..."
    python3 ./setup/build_windows.py
    echo "[Windows] ✓ EXE created"
}

build_linux() {
    echo "[Linux] Building packages..."
    python3 ./setup/build_linux.py
    echo "[Linux] ✓ Packages created"
}

case "$PLATFORM" in
    macos)
        build_macos
        ;;
    windows)
        build_windows
        ;;
    linux)
        build_linux
        ;;
    all)
        build_macos
        build_windows
        build_linux
        ;;
    *)
        echo "Usage: $0 [macos|windows|linux|all]"
        exit 1
        ;;
esac

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               Build Complete!                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Output files in: build/"
ls -la build/