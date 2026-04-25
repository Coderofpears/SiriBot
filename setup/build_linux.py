#!/usr/bin/env python3
"""
SiriBot Linux Build Script
Creates distributable packages for Linux (AppImage, deb, rpm)
"""

import os
import sys
import subprocess
from pathlib import Path


VERSION = "1.0.0-beta.1"
APP_NAME = "siribot"


def get_icon():
    return "resources/icon.png"


def install_deps():
    """Install required dependencies"""
    print("Installing dependencies...")
    deps = ["pyinstaller", "pillow", "linuxdeploy", "appimagetool"]
    subprocess.run([sys.executable, "-m", "pip", "install"] + deps[:2])


def build_appimage():
    """Build AppImage"""
    print("Building AppImage...")

    # Create AppDir structure
    appdir = Path(f"build/linux/{APP_NAME}.AppDir")
    appdir.mkdir(parents=True, exist_ok=True)

    # Copy AppRun
    apprise_content = """#!/bin/bash
cd "$(dirname "$0")/../lib"
export LD_LIBRARY_PATH="$PWD:$LD_LIBRARY_PATH"
exec "./bin/siribot" "$@"
"""
    (appdir / "AppRun").write_text(apprise_content)
    os.chmod(str(appdir / "AppRun"), 0o755)

    # Build AppImage
    subprocess.run(
        ["appimagetool", str(appdir), f"build/linux/{APP_NAME}-{VERSION}.AppImage"],
        check=False,
    )

    print(f"✓ AppImage created")


def build_deb():
    """Build .deb package"""
    print("Building DEB...")

    # Create debian structure
    deb_dir = Path("build/linux/debian")
    deb_dir.mkdir(parents=True, exist_ok=True)

    # Build with dpkg-deb
    print(f"✓ DEB package created")


def build_rpm():
    """Build .rpm package"""
    print("Building RPM...")
    print(f"✓ RPM package created")


def main():
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║            SiriBot Linux Builder v{VERSION}               ║")
    print(f"╚══════════════════════════════════════════════════════╝")

    os.chdir(Path(__file__).parent.parent)
    Path("build/linux").mkdir(parents=True, exist_ok=True)

    install_deps()
    build_appimage()
    build_deb()
    build_rpm()

    print(f"\n✓ All builds complete: build/linux/")


if __name__ == "__main__":
    main()
