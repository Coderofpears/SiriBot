#!/usr/bin/env python3
"""
SiriBot Windows Build Script
Creates a distributable .exe for Windows using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


VERSION = "1.0.0-beta.1"
APP_NAME = "SiriBot"


def get_app_icon():
    """Get app icon - Windows uses .ico"""
    return "resources/icon.ico"


def install_deps():
    """Install required dependencies"""
    print("Installing dependencies...")
    deps = ["pyinstaller", "pillow"]
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, "-m", "pip", "install"] + deps)


def build_spec():
    """Create PyInstaller spec file"""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py', 'siribot/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config/config.example.yaml', 'config'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'aiohttp',
        'anthropic',
        'click',
        'pydantic',
        'rich',
        'sqlite3',
        'yaml',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{get_app_icon()}',
    version='version_info.txt',
)
"""
    Path("siribot.spec").write_text(spec_content)


def build_exe():
    """Build the Windows executable"""
    print(f"Building {APP_NAME}.exe...")

    # Clean build directory
    Path("build/windows").mkdir(parents=True, exist_ok=True)

    # Build with PyInstaller
    subprocess.run(
        [
            "pyinstaller",
            "siribot.spec",
            "--name",
            APP_NAME,
            "--onefile",
            "--windowed",
            "--icon",
            get_app_icon(),
            "--distpath",
            "build/windows",
            "--workpath",
            "build/windows/build",
            "--specpath",
            "build/windows",
        ],
        check=False,
    )

    # Copy additional files
    exe_path = Path("build/windows") / f"{APP_NAME}.exe"
    if exe_path.exists():
        print(f"✓ Created: {exe_path}")
        return True
    return False


def create_installer():
    """Create installer using Inno Setup (if available)"""
    print("Checking for Inno Setup...")
    if shutil.which("iscc"):
        print("Creating installer...")
        # Inno Setup script would go here
    else:
        print("Inno Setup not found, skipping installer")


def main():
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║           SiriBot Windows Builder v{VERSION}              ║")
    print(f"╚═══════════════���══════════════════════════════════════╝")

    os.chdir(Path(__file__).parent.parent)

    try:
        install_deps()
        build_spec()
        if build_exe():
            create_installer()
            print(f"\n✓ Build complete: build/windows/{APP_NAME}.exe")
        else:
            print("\n✗ Build failed")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
