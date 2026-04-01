# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [Unreleased]

### Hinzugefügt
- 📅 **Wochentagauswahl**: Du kannst jetzt auswählen, an welchen Wochentagen die Erinnerung erscheinen soll
- 🔧 Interaktives Konfigurationsskript mit 4 Optionen:
  - Jeden Tag (Montag bis Sonntag)
  - Werktage (Montag bis Freitag)
  - Wochenende (Samstag und Sonntag)
  - Benutzerdefiniert (wähle einzelne Tage)
- 💻 PowerShell-Konfigurationsskript für Windows (`configure.ps1`)
- 📝 JSON-basierte Konfigurationsdatei für bessere Struktur

### Geändert
- ⚙️ Konfigurationsdateiformat von einfachem Text zu JSON
- 📖 README erweitert mit detaillierten Konfigurationsbeispielen
- 🔄 Automatische Migration von alten Konfigurationen zum neuen Format

### Technisch
- Config-Struktur erweitert mit `weekdays` Array
- Wochentag-Validierung in der Hauptschleife
- Logging erweitert um aktive Wochentage

## [1.0.0] - Initial Release

### Hinzugefügt
- 🌙 Vollbild-Banner zur Schlafenszeit
- ⏰ Konfigurierbare Schlafenszeit
- 👤 Personalisierte Nachricht mit Benutzernamen
- 🔄 Background-Service (systemd für Linux)
- 📦 Multi-Platform Support (Linux, macOS, Windows)
- 🚀 GitHub Actions für automatische Builds
- 📝 Vollständige Dokumentation
- 🛠️ Einfaches Installationsskript
