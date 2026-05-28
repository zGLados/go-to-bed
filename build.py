"""Build script for creating executable."""
import PyInstaller.__main__
import sys
from pathlib import Path

# Check if running on Windows
if sys.platform != 'win32':
    print("=" * 70)
    print("⚠️  WARNING: You are NOT running on Windows!")
    print("=" * 70)
    print(f"Current platform: {sys.platform}")
    print("")
    print("This will create a {}-executable, NOT a Windows .exe!".format(
        "Linux" if sys.platform.startswith('linux') else 
        "macOS" if sys.platform == 'darwin' else sys.platform
    ))
    print("")
    print("To create a Windows .exe, you MUST run this on Windows.")
    print("=" * 70)
    
    response = input("\nDo you want to continue anyway? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Build cancelled.")
        sys.exit(0)
    print("")

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

if sys.platform == 'win32':
    exe_path = script_dir / 'dist' / 'GotoBed.exe'
    print(f"✓ Windows Executable: {exe_path}")
    print("✓ Ready to distribute on Windows!")
else:
    exe_name = 'GotoBed.exe' if sys.platform == 'win32' else 'GotoBed'
    exe_path = script_dir / 'dist' / exe_name
    print(f"⚠️  {sys.platform} executable: {exe_path}")
    print("⚠️  This will NOT run on Windows!")
    print("⚠️  To create Windows .exe, build on Windows!")

print("=" * 60)
