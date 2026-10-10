"""Build GotoBed.exe with PyInstaller.

Usage: python build.py
Run on Windows (or let GitHub Actions do it) to get a Windows .exe;
PyInstaller always builds for the OS it runs on.
"""
import os
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
ASSETS = ROOT / 'assets'
NAME = 'GotoBed'


def main() -> None:
    if sys.platform != 'win32':
        print(f"WARNING: building on {sys.platform} creates a {sys.platform} executable, NOT a Windows .exe.")

    PyInstaller.__main__.run([
        str(SRC / 'main.py'),
        f'--name={NAME}',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        f'--paths={SRC}',
        f'--icon={ASSETS / "icon.ico"}',
        f'--add-data={ASSETS}{os.pathsep}assets',
        '--hidden-import=pystray._win32',
        '--hidden-import=PIL._tkinter_finder',
        f'--distpath={ROOT / "dist"}',
        f'--workpath={ROOT / "build"}',
        f'--specpath={ROOT / "build"}',
    ])

    exe = ROOT / 'dist' / (NAME + ('.exe' if sys.platform == 'win32' else ''))
    if not exe.exists():
        sys.exit(f"Build failed: {exe} not found")
    print(f"Build complete: {exe} ({exe.stat().st_size / 1e6:.1f} MB)")


if __name__ == '__main__':
    main()
