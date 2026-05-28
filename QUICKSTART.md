# 🚀 Quick Start Guide

**⚠️ Important: This app is designed for Windows. Building the .exe must be done on Windows!**

## For Development on Linux

You can edit the code on Linux, but to test and build the .exe, you need Windows.

```bash
# Edit code on Linux
git clone <repo>
cd go-to-bed

# To test on Linux (requires GTK3 system packages - not recommended):
# sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

## On Windows: Build & Run

### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 2. Testen (Windows only)
```bash
python src/main.py
```

### 3. Als .exe erstellen (Windows only)
```bash
python build.py
```
Die .exe findest du dann in `dist/GotoBed.exe`

---

## Quick Start (English)

**⚠️ Windows Required:** This is a Windows application. Build on Windows!

### 1. Install Dependencies (Windows)
```bash
pip install -r requirements.txt
```

### 2. Test Installation (Windows)
```bash
python test_dependencies.py
```

### 3. Run the App (Windows)
```bash
python src/main.py
```

### 4. Build Executable (Windows)
```bash
python build.py
```
Find the .exe in `dist/GotoBed.exe`

---

## Erste Schritte nach dem Start

1. **Beim ersten Start** öffnet sich automatisch das Einstellungsfenster
2. **Tray Icon** erscheint in der Taskleiste (🌙 Mond-Symbol)
3. **Rechtsklick** auf das Icon für Menü
4. **Test Reminder** zum Testen der Erinnerung

## Tipps

- **Vorwarnung**: 15-30 Minuten empfohlen
- **Wochentage**: Wähle nur Arbeitstage für bessere Compliance
- **Snooze**: 10 Minuten ist ein guter Standard
- **Autostart**: Aktivieren, damit du es nicht vergisst!

## Fehlersuche

### App startet nicht
```bash auf Windows
```bash
python test_dependencies.py
```

### Build schlägt fehl
```bash
pip install --upgrade pyinstaller
python build.py
```

### Linux Development
Code kann auf Linux bearbeitet werden, aber zum Testen/Builden muss Windows verwendet werden.
System Tray funktioniert auf Linux nur mit zusätzlichen GTK3-Paketen (nicht offiziell supported).
---

Viel Erfolg! 😴🌙
