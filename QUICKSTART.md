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
# Windows: Install Go
# https://golang.org/dl/

# Inno Setup for installer (optional)
# https://jrsoftware.org/isinfo.php
```

### Setup Project
```bash
git clone https://github.com/zGLados/go-to-bed.git
cd go-to-bed
go mod download
go build -o go-to-bed.exe .
```

### Test
```bash
# Run directly
go run .

# With custom time (edit config first):
# %USERPROFILE%\.go-to-bed.conf
```

### Build Installer
```bash
# With Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Create Release
```bash
# Create tag
git tag v1.3.0
git push origin v1.3.0

# GitHub Actions builds the installer automatically!
```

## Troubleshooting

### Program not running
Open Task Manager (Ctrl+Shift+Esc) and check if `go-to-bed.exe` is running.

If not, start it manually:
- Start Menu → "Go-to-Bed"
- Or: `%ProgramFiles%\Go-to-Bed\go-to-bed.exe`

### Fullscreen not working
Make sure you're using a graphical Windows environment (not Server Core).

### Change time
Run the configuration script:
- Start Menu → "Go-to-Bed" → "Configuration"
- Restart not required (watches config file)

## Next Steps

- ⭐ Star the project on GitHub
- 🐛 Found a bug? [Open an issue](../../issues)
- 💡 Feature idea? [Open a discussion](../../discussions)
- 🤝 Want to contribute? See the README
