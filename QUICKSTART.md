# 🚀 Quickstart

## For Windows Users (Recommended)

1. **Download**: Go to [Releases](../../releases/latest) and download `GoToBed-Setup.exe`

2. **Install**: Double-click the file and follow the wizard

3. **Done!** The installer will:
   - Install the program
   - Ask you to configure your bedtime and active days
   - Optionally set up autostart
   - You're all set! 🎉

## Change Configuration

**Windows:**
- Start Menu → "Go-to-Bed" → "Configuration"

Or via PowerShell:
```powershell
cd "%ProgramFiles%\Go-to-Bed"
.\configure.ps1
```

The script will ask you:
1. **Bedtime** (e.g., 22:00)
2. **Weekdays** (Every day, Weekdays, Weekend, or Custom)

Or edit directly:
```powershell
# JSON format in: %USERPROFILE%\.go-to-bed.conf
{
  "bedtime": "23:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

## For Developers

### Prerequisites
```bash
# Windows: PowerShell 5.1+ (included)
# Inno Setup for installer (optional)
# https://jrsoftware.org/isinfo.php
```

### Setup Project
```powershell
git clone https://github.com/zGLados/go-to-bed.git
cd go-to-bed
# No dependencies to install! PowerShell scripts run directly
```

### Test
```powershell
# Run directly (with console output)
.\GoToBed.ps1

# Run hidden (background mode)
.\Start-GoToBed.vbs

# Test banner
.\Show-Banner.ps1 -Username "YourName"
```

### Build Installer
```powershell
# With Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Create Release
```powershell
# Create tag
git tag v2.0.0
git push origin v2.0.0

# GitHub Actions builds the installer automatically in ~30 seconds!
```

## Troubleshooting

### Program not running
Open Task Manager (Ctrl+Shift+Esc) and check for:
- `powershell.exe` running GoToBed.ps1
- `wscript.exe` running Start-GoToBed.vbs

If not running, start it manually:
- Start Menu → "Go-to-Bed"  
- Or: `%ProgramFiles%\Go-to-Bed\Start-GoToBed.vbs`

### Console window appears
Use the VBS launcher instead:
```powershell
.\Start-GoToBed.vbs  # Hides console
```

### Banner not showing
Check PowerShell execution policy:
```powershell
Get-ExecutionPolicy
# Should be RemoteSigned or Unrestricted
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Change time
Configuration updates are picked up automatically (no restart needed):
- Start Menu → "Go-to-Bed" → "Configuration"
- Or edit: `%USERPROFILE%\.go-to-bed.conf`

## Next Steps

- ⭐ Star the project on GitHub
- 🐛 Found a bug? [Open an issue](../../issues)
- 💡 Feature idea? [Open a discussion](../../discussions)
- 🤝 Want to contribute? See the README
