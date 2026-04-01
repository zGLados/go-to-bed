# 🌙 Go-to-Bed

Ein einfaches Tool, das dich zu einer bestimmten Uhrzeit daran erinnert, ins Bett zu gehen!

## Features

- 🕐 Konfigurierbare Schlafenszeit
- � **Wochentagauswahl** - Wähle an welchen Tagen die Erinnerung erscheint
- �🖥️ Großer Vollbild-Banner zur Erinnerung
- 👤 Zeigt deinen Benutzernamen in der Nachricht
- 🔄 Läuft im Hintergrund als Service
- 🚀 Einfache Installation mit automatischem Setup
- 📦 Vorkompilierte Binaries für Linux, macOS und Windows

## Installation

### Schnellinstallation (empfohlen)

1. Lade die neueste Version für dein System von den [Releases](../../releases/latest) herunter:
   - **Linux (64-bit)**: `go-to-bed-linux-amd64.tar.gz`
   - **Linux (ARM64)**: `go-to-bed-linux-arm64.tar.gz`
   - **macOS (Intel)**: `go-to-bed-darwin-amd64.tar.gz`
   - **macOS (Apple Silicon)**: `go-to-bed-darwin-arm64.tar.gz`
   - **Windows**: `go-to-bed-windows-amd64.zip`

2. Entpacke das Archiv:
   ```bash
   # Linux/macOS
   tar xzf go-to-bed-*.tar.gz
   cd go-to-bed-*
   
   # Windows
   # Entpacke die ZIP-Datei mit dem Explorer
   ```

3. Führe das Installationsskript aus:
   ```bash
   # Linux/macOS
   ./install.sh
   
   # Windows
   # Siehe Windows-Anleitung unten
   ```

### Linux (systemd)

Das Installationsskript richtet automatisch einen systemd-Service ein:

```bash
./install.sh
```

Der Service läuft dann automatisch im Hintergrund und startet bei jedem Login.

**Service-Befehle:**
```bash
# Status prüfen
systemctl --user status go-to-bed

# Service stoppen
systemctl --user stop go-to-bed

# Service neustarten
systemctl --user restart go-to-bed

# Logs anzeigen
journalctl --user -u go-to-bed -f
```

### macOS

Für macOS kann das Tool als LaunchAgent eingerichtet werden. Eine detaillierte Anleitung folgt in zukünftigen Updates.

Aktuell kann das Tool manuell gestartet werden:
```bash
./go-to-bed-darwin-*
```

### Windows

Für Windows:

1. Entpacke die ZIP-Datei
2. Führe die Konfiguration aus:
   ```powershell
   .\configure.ps1
   ```
3. Starte das Programm:
   ```powershell
   .\go-to-bed-windows-amd64.exe
   ```

**Autostart einrichten:**

Um das Programm automatisch beim Login zu starten:
1. Drücke `Win + R` und gib `shell:startup` ein
2. Erstelle eine Verknüpfung zur `go-to-bed-windows-amd64.exe` in diesem Ordner
3. Beim nächsten Login startet das Programm automatisch

Eine detaillierte Anleitung für Windows-Services folgt in zukünftigen Updates.

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
- Für Linux: `libgl1-mesa-dev` und `xorg-dev`

### Build von Quellcode

1. Repository klonen:
   ```bash
   git clone https://github.com/[dein-username]/go-to-bed.git
   cd go-to-bed
   ```

2. Dependencies installieren:
   ```bash
   make deps
   ```

3. Bauen:
   ```bash
   make build
   ```

4. Für alle Plattformen bauen:
   ```bash
   make build-all
   ```

### Lokal testen

```bash
make run
```

## GitHub Actions

Dieses Projekt nutzt GitHub Actions für automatische Builds:

- Bei jedem Tag-Push (z.B. `v1.0.0`) werden automatisch Binaries für alle Plattformen erstellt
- Die Binaries werden als Release-Assets veröffentlicht
- Jeder kann die neueste Version einfach herunterladen

### Release erstellen

1. Tag erstellen und pushen:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions baut automatisch alle Binaries
3. Ein neues Release wird mit allen Plattform-Paketen erstellt

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Beiträge

Pull Requests sind willkommen! Für größere Änderungen öffne bitte zuerst ein Issue.

## Bekannte Probleme

- macOS: Vollbild-Banner funktioniert möglicherweise nicht perfekt auf allen Versionen
- Windows: Benachrichtigungen erfordern möglicherweise zusätzliche Konfiguration

## Roadmap

- [ ] Bessere macOS Integration (LaunchAgent)
- [ ] Windows Service Support
- [ ] Mehrere Erinnerungszeiten pro Tag
- [ ] Snooze-Funktion
- [ ] Anpassbare Nachrichten
- [ ] GUI für Konfiguration
- [x] Wochentagauswahl

## Support

Bei Problemen oder Fragen öffne bitte ein Issue auf GitHub.

---

Gute Nacht! 🌙💤
