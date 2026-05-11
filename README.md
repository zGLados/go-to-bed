# 🌙 Go-to-Bed v2.0

Eine moderne Windows-Anwendung mit Systemtray-Integration, die dich daran erinnert, rechtzeitig ins Bett zu gehen.

## ✨ Features

- 🖥️ **Systemtray-Integration** - Läuft im Hintergrund, immer bereit
- ⏰ **Flexible Zeitplanung** - Stelle deine Schlafenszeit und aktive Wochentage ein
- 😴 **Snooze-Funktion** - Verschiebe die Erinnerung um einige Minuten
- 📊 **Statistiken** - Verfolge, wie oft du die Erinnerung befolgst
- 🎨 **Moderne UI** - Schönes, intuitives Design
- 🚀 **Autostart** - Automatisch beim Windows-Start (optional)
- 💾 **Persistente Einstellungen** - Deine Konfiguration wird gespeichert

## 📦 Installation

### Voraussetzungen

- Node.js (Version 18 oder höher)
- npm (kommt mit Node.js)

### Schritt 1: Dependencies installieren

```bash
npm install
```

### Schritt 2: Anwendung starten (Entwicklungsmodus)

```bash
npm start
```

### Schritt 3: Installer erstellen

```bash
npm run build:win
```

Der Installer wird im Ordner `dist` erstellt.

## 🎯 Verwendung

### Erste Schritte

1. Starte die Anwendung
2. Das Systemtray-Icon erscheint in der Taskleiste
3. Rechtsklick auf das Icon → "Einstellungen"
4. Stelle deine Schlafenszeit und aktive Wochentage ein
5. Klicke auf "Speichern"

### Funktionen

**Einstellungen:**
- Aktiviere/Deaktiviere Erinnerungen
- Stelle deine Schlafenszeit ein
- Wähle aktive Wochentage (z.B. nur Wochentage)
- Passe die Snooze-Dauer an (1-60 Minuten)

**Erinnerung:**
- Wenn die eingestellte Zeit erreicht ist, erscheint ein Erinnerungsfenster
- **Snooze**: Verschiebe die Erinnerung um X Minuten
- **Okay, ich gehe!**: Bestätige, dass du ins Bett gehst

**Statistiken:**
- Sieh, wie viele Erinnerungen du erhalten hast
- Wie oft du die Erinnerung befolgt hast
- Deine Erfolgsquote
- Letzte Aktivitäten

### Systemtray-Menü

- **Schlafenszeit**: Zeigt deine aktuelle Schlafenszeit
- **Aktiviert/Deaktiviert**: Schalte Erinnerungen ein/aus
- **Einstellungen**: Öffne das Einstellungsfenster
- **Statistiken**: Öffne die Statistik-Ansicht
- **Test Erinnerung**: Teste die Erinnerung manuell
- **Beenden**: Schließe die Anwendung

## 🛠️ Entwicklung

### Projektstruktur

```
go-to-bed/
├── src/
│   ├── main.js         # Haupt-Electron-Prozess
│   ├── config.js       # Konfigurations-Manager
│   ├── settings.html   # Einstellungsfenster
│   ├── settings.js     # Einstellungs-Logik
│   ├── reminder.html   # Erinnerungsfenster
│   ├── reminder.js     # Erinnerungs-Logik
│   ├── stats.html      # Statistik-Fenster
│   ├── stats.js        # Statistik-Logik
│   └── styles.css      # Gemeinsame Styles
├── assets/
│   ├── tray-icon.svg   # Systemtray-Icon (SVG)
│   └── tray-icon.png   # Systemtray-Icon (PNG, 16x16)
├── package.json
└── README.md
```

### Icons erstellen

Das SVG-Icon kann mit Tools wie Inkscape oder online SVG-zu-PNG-Konvertern in ein PNG umgewandelt werden:

1. Öffne `assets/tray-icon.svg` in einem SVG-Editor
2. Exportiere als PNG mit 16x16 Pixeln
3. Speichere als `assets/tray-icon.png`

Für das Installer-Icon (`.ico`) kannst du Tools wie:
- https://convertio.co/de/png-ico/
- https://www.icoconverter.com/

verwenden, um aus dem PNG ein ICO zu erstellen.

### Autostart konfigurieren

Die Anwendung kann so eingestellt werden, dass sie beim Windows-Start automatisch startet:

1. Drücke `Win + R`
2. Gib ein: `shell:startup`
3. Erstelle eine Verknüpfung zur ausführbaren Datei in diesem Ordner

Oder verwende den Installer, der diese Option automatisch anbietet.

## 🔧 Technologien

- **Electron** - Desktop-App-Framework
- **Node.js** - Backend-Logik
- **HTML/CSS/JavaScript** - Frontend
- **electron-builder** - Installer-Erstellung

## 📝 Konfiguration

Die Konfigurationsdateien werden im Benutzerverzeichnis gespeichert:

```
C:\Users\[Username]\AppData\Roaming\go-to-bed\
├── config.json    # Einstellungen
└── stats.json     # Statistiken
```

## 🐛 Fehlerbehebung

**Die Anwendung startet nicht:**
- Stelle sicher, dass Node.js installiert ist
- Führe `npm install` aus, um alle Dependencies zu installieren

**Das Tray-Icon wird nicht angezeigt:**
- Erstelle das Icon aus der SVG-Vorlage (siehe "Icons erstellen")
- Stelle sicher, dass `assets/tray-icon.png` existiert

**Erinnerungen funktionieren nicht:**
- Überprüfe, ob die Erinnerungen aktiviert sind (Systemtray-Menü)
- Stelle sicher, dass der aktuelle Wochentag aktiviert ist
- Die App prüft jede Minute, ob es Zeit ist

## 📄 Lizenz

MIT License - siehe LICENSE-Datei

## 🤝 Beitragen

Feedback und Beiträge sind willkommen! Öffne ein Issue oder Pull Request auf GitHub.

## 🎉 Danke

Danke, dass du Go-to-Bed verwendest! Schlafe gut! 😴🌙
