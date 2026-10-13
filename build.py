"""Build GotoBed.exe with PyInstaller.

Usage: python build.py [--dist DIR]
Run on Windows (or let GitHub Actions do it) to get a Windows .exe;
PyInstaller always builds for the OS it runs on.
"""
import argparse
import os
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
ASSETS = ROOT / 'assets'
NAME = 'GotoBed'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', default=str(ROOT / 'dist'), help='output folder (default: dist)')
    dist = Path(parser.parse_args().dist).resolve()

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
        f'--distpath={dist}',
        f'--workpath={ROOT / "build"}',
        f'--specpath={ROOT / "build"}',
    ])

    exe = dist / (NAME + ('.exe' if sys.platform == 'win32' else ''))
    if not exe.exists():
        sys.exit(f"Build failed: {exe} not found")
    print(f"Build complete: {exe} ({exe.stat().st_size / 1e6:.1f} MB)")


if __name__ == '__main__':
    main()
