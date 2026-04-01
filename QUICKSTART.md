# 🚀 Schnellstart

## Für Windows-Nutzer (Empfohlen)

1. **Download**: Gehe zu [Releases](../../releases/latest) und lade `GoToBed-Setup.exe` herunter

2. **Installieren**: Doppelklick auf die Datei, Installer-Assistent folgen

3. **Fertig!** Der Installer:
   - Installiert das Programm
   - Richtet optional Autostart ein
   - Startet die Konfiguration
   - Du wirst nach deiner Schlafenszeit gefragt 🎉

## Konfiguration ändern

**Windows:**
- Start-Menü → "Go-to-Bed" → "Konfiguration"

Oder über PowerShell:
```powershell
cd "%ProgramFiles%\Go-to-Bed"
.\configure.ps1
```

## Für Entwickler

### Voraussetzungen
```bash
# Windows: Go installieren
# https://golang.org/dl/

# Inno Setup für Installer (optional)
# https://jrsoftware.org/isinfo.php
```

### Projekt aufsetzen
```bash
git clone https://github.com/zGLados/go-to-bed.git
cd go-to-bed
go mod download
go build -o go-to-bed.exe .
```

### Testen
```bash
# Direkt ausführen
go run .

# Mit benutzerdefinierter Zeit (in 1 Minute)
# Bearbeite erst die Config:
# %USERPROFILE%\.go-to-bed.conf
```

### Installer bauen
```bash
# Mit Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Release erstellen
```bash
# Tag erstellen
git tag v1.2.0
git push origin v1.2.0

# GitHub Actions erstellt automatisch den Installer!
```

## Konfiguration ändern

**Windows:**
- Start-Menü → "Go-to-Bed" → "Konfiguration"

Oder über PowerShell:
```powershell
cd "%ProgramFiles%\Go-to-Bed"
.\configure.ps1
```

Das Skript fragt dich:
1. **Schlafenszeit** (z.B. 22:00)
2. **Wochentage** (Jeden Tag, Werktage, Wochenende, oder Benutzerdefiniert)

Oder direkt editieren:
```powershell
# JSON-Format verwenden in: %USERPROFILE%\.go-to-bed.conf
{
  "bedtime": "23:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

## Troubleshooting

### Programm läuft nicht
Task-Manager öffnen (Strg+Shift+Esc) und prüfen, ob `go-to-bed.exe` läuft.

Wenn nicht, starte es manuell:
- Start-Menü → "Go-to-Bed"
- Oder: `%ProgramFiles%\Go-to-Bed\go-to-bed.exe`

### Vollbild funktioniert nicht
Stelle sicher, dass du eine grafische Windows-Umgebung verwendest (kein Server Core).

## Nächste Schritte

- ⭐ Gib dem Projekt einen Star auf GitHub
- 🐛 Gefunden einen Bug? [Öffne ein Issue](../../issues)
- 💡 Feature-Idee? [Öffne eine Discussion](../../discussions)
- 🤝 Möchtest du beitragen? Siehe [CONTRIBUTING.md](CONTRIBUTING.md)
