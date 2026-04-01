# 🌙 Go-to-Bed

Ein einfaches Tool, das dich zu einer bestimmten Uhrzeit daran erinnert, ins Bett zu gehen!

**Windows-Installer verfügbar!** - Ein-Klick Installation mit automatischem Autostart 🚀

## Features

- 🕐 Konfigurierbare Schlafenszeit
- � **Wochentagauswahl** - Wähle an welchen Tagen die Erinnerung erscheint
- �🖥️ Großer Vollbild-Banner zur Erinnerung
- 👤 Zeigt deinen Benutzernamen in der Nachricht
- 🔄 Läuft im Hintergrund als Service
- 🚀 **Windows: Ein-Klick Installer** - Automatischer Autostart und Konfiguration
- 📦 Einfache Installation

## Installation

### Windows (Empfohlen) 🎯

**Ein-Klick Installation:**

1. Lade `GoToBed-Setup.exe` von den [Releases](../../releases/latest) herunter
2. Doppelklick auf die heruntergeladene Datei
3. Folge dem Installationsassistenten:
   - ✅ **"Automatisch beim Windows-Start ausführen"** wird empfohlen
   - Der Installer konfiguriert automatisch den Autostart
   - Nach der Installation wirst du nach deiner Schlafenszeit gefragt
4. **Fertig!** Das Programm läuft jetzt im Hintergrund

**Features des Installers:**
- ✨ Automatische Installation in `Programme\Go-to-Bed`
- 🚀 Optionaler Autostart beim Windows-Start
- ⚙️ Geführte Konfiguration während der Installation
- 🗑️ Saubere Deinstallation über Windows-Systemsteuerung

**Konfiguration ändern:**
- Start-Menü → "Go-to-Bed" → "Konfiguration"
- Oder führe aus: `%ProgramFiles%\Go-to-Bed\configure.ps1`

---

### Linux & macOS (Aktuell nicht verfügbar)

Die Entwicklung konzentriert sich momentan auf Windows. Linux und macOS Versionen sind geplant.

**Hinweis:** Frühere Versionen unterstützten Linux. Wenn du Linux benötigst, schau dir ältere Releases an oder baue selbst von Source.

## Konfiguration

### Schlafenszeit und Wochentage einstellen

Nach der Installation wirst du automatisch gefragt:
1. **Wann** deine Schlafenszeit sein soll (z.B. 22:00)
2. **An welchen Wochentagen** die Erinnerung erscheinen soll

Um die Einstellungen später zu ändern, führe aus:

```bash
./configure.sh
```

Das Konfigurationsskript bietet folgende Optionen:
- **Jeden Tag** (Montag bis Sonntag) - für regelmäßige Schlafenszeiten
- **Werktage** (Montag bis Freitag) - nur an Arbeitstagen
- **Wochenende** (Samstag und Sonntag) - längere Nächte am Wochenende
- **Benutzerdefiniert** - wähle einzelne Tage aus

### Manuelle Konfiguration

Die Konfigurationsdatei befindet sich unter:
```
~/.go-to-bed.conf
```

Sie ist im JSON-Format und kann auch direkt bearbeitet werden:

```json
{
  "bedtime": "22:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

**Wochentage:**
- `Mon` = Montag
- `Tue` = Dienstag
- `Wed` = Mittwoch
- `Thu` = Donnerstag
- `Fri` = Freitag
- `Sat` = Samstag
- `Sun` = Sonntag

**Beispiele:**

Nur am Wochenende später ins Bett:
```json
{
  "bedtime": "01:00",
  "weekdays": ["Sat", "Sun"]
}
```

Werktags 22 Uhr, am Wochenende keine Erinnerung:
```json
{
  "bedtime": "22:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

## Verwendung

Nachdem der Service installiert und konfiguriert ist, läuft er automatisch im Hintergrund.

Zur konfigurierten Schlafenszeit **an den ausgewählten Wochentagen** erscheint:
1. Eine System-Benachrichtigung
2. Ein großer Vollbild-Banner mit deinem Benutzernamen

Der Banner zeigt:
```
🌙 [Dein Name], es ist Zeit ins Bett zu gehen! 🌙
Gute Nacht! 😴
```

Du kannst den Banner mit dem Button "OK, ich gehe jetzt ins Bett" schließen, oder er verschwindet automatisch nach 2 Minuten.

**Hinweis:** An Tagen, die nicht in deiner Konfiguration ausgewählt sind, erscheint keine Erinnerung.

## Entwicklung

### Voraussetzungen

- Go 1.21 oder höher
- **Für Windows:** Wird automatisch durch Go build tools unterstützt

### Build von Quellcode

1. Repository klonen:
   ```bash
   git clone https://github.com/zGLados/go-to-bed.git
   cd go-to-bed
   ```

2. Dependencies installieren:
   ```bash
   go mod download
   ```

3. **Windows** bauen:
   ```bash
   # Standard build (mit Konsolenfenster)
   go build -o go-to-bed.exe .
   
   # Background build (ohne Konsolenfenster)
   go build -ldflags "-H windowsgui" -o go-to-bed.exe .
   ```

4. **Installer** bauen (Windows mit Inno Setup):
   ```bash
   # Inno Setup installieren: https://jrsoftware.org/isinfo.php
   # Dann:
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

### Lokal testen

```bash
go run .
```

## GitHub Actions

Dieses Projekt nutzt GitHub Actions für automatische Installer-Builds:

- Bei jedem Tag-Push (z.B. `v1.2.0`) wird automatisch ein Windows-Installer erstellt
- Der Installer wird als Release-Asset veröffentlicht
- Jeder kann die neueste Version einfach herunterladen

### Release erstellen

1. Tag erstellen und pushen:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

2. GitHub Actions baut automatisch den Installer
3. Ein neues Release wird mit `GoToBed-Setup.exe` erstellt

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Beiträge

Pull Requests sind willkommen! Für größere Änderungen öffne bitte zuerst ein Issue.

## Bekannte Probleme

- **Erste Ausführung:** Windows Defender SmartScreen könnte eine Warnung anzeigen (klicke auf "Weitere Informationen" → "Trotzdem ausführen")
- **Konfiguration:** PowerShell Execution Policy muss Skripte erlauben (wird automatisch mit `-ExecutionPolicy Bypass` umgangen)

## Roadmap

- [x] **Windows Installer (.exe)** - Ein-Klick Installation ✅
- [ ] **Linux .deb/.rpm Pakete** - System-Package-Manager Integration
- [ ] **macOS App Bundle (.app)** - Installierbare App mit Installationsskript
- [ ] System-Tray-Icon für Windows
- [ ] Mehrere Erinnerungszeiten pro Tag
- [ ] Snooze-Funktion
- [ ] Anpassbare Nachrichten
- [ ] GUI für Konfiguration
- [x] Wochentagauswahl ✅

## Support

Bei Problemen oder Fragen öffne bitte ein Issue auf GitHub.

---

Gute Nacht! 🌙💤
