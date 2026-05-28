"""Build script for creating executable."""
import PyInstaller.__main__
import sys
from pathlib import Path

# Get the directory of this script
script_dir = Path(__file__).parent
src_dir = script_dir / 'src'
icon_path = script_dir / 'assets' / 'icon.ico'

# PyInstaller arguments
args = [
    str(src_dir / 'main.py'),  # Main script
    '--name=GotoBed',  # Name of executable
    '--onefile',  # Create single executable
    '--windowed',  # No console window
    '--clean',  # Clean cache
    f'--distpath={script_dir / "dist"}',  # Output directory
    f'--workpath={script_dir / "build"}',  # Work directory
    f'--specpath={script_dir}',  # Spec file directory
]

# Add icon if it exists
if icon_path.exists():
    args.append(f'--icon={icon_path}')
else:
    print(f"Warning: Icon not found at {icon_path}")

# Additional options for better compatibility
args.extend([
    '--add-data=src:src',  # Include source for reference
    '--hidden-import=PIL._tkinter_finder',  # Fix PIL/tkinter issues
])

print("=" * 60)
print("Building Go-to-Bed executable...")
print("=" * 60)
print(f"Source: {src_dir}")
print(f"Output: {script_dir / 'dist'}")
if icon_path.exists():
    print(f"Icon: {icon_path}")
print("=" * 60)

# Run PyInstaller
PyInstaller.__main__.run(args)

print("=" * 60)
print("✓ Build complete!")
print(f"Executable: {script_dir / 'dist' / 'GotoBed.exe'}")
print("=" * 60)
