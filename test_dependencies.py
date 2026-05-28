#!/usr/bin/env python3
"""Quick test script to verify installation."""
import sys

print("Testing Go-to-Bed dependencies...")
print("=" * 50)

errors = []

# Test Python version
py_version = sys.version_info
print(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
if py_version < (3, 8):
    errors.append("Python 3.8+ required")
else:
    print("✓ Python version OK")

# Test imports
modules = [
    ('pystray', 'System Tray'),
    ('PIL', 'Pillow (Image handling)'),
    ('plyer', 'Notifications'),
]

for module, name in modules:
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        errors.append(f"{name} not installed (pip install {module.split('.')[0]})")
        print(f"✗ {name} - MISSING")

# tkinter is special (comes with Python)
try:
    import tkinter
    print("✓ tkinter (GUI)")
except ImportError:
    errors.append("tkinter not available (install python3-tk)")
    print("✗ tkinter - MISSING")

print("=" * 50)

if errors:
    print("\n❌ ERRORS FOUND:")
    for error in errors:
        print(f"  - {error}")
    print("\nTo fix, run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✓ All dependencies OK!")
    print("\nYou can now run:")
    print("  python src/main.py")
    sys.exit(0)
