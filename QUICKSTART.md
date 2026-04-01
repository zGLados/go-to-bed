# 🚀 Schnellstart

## Für Nutzer (Empfohlen)

1. **Download**: Gehe zu [Releases](../../releases/latest) und lade die Datei für dein System herunter

2. **Entpacken**:
   ```bash
   tar xzf go-to-bed-linux-amd64.tar.gz
   cd go-to-bed-linux-amd64
   ```

3. **Installieren**:
   ```bash
   ./install.sh
   ```

4. **Fertig!** Der Service läuft jetzt im Hintergrund 🎉

## Für Entwickler

### Voraussetzungen
```bash
# Ubuntu/Debian
sudo apt-get install golang-go libgl1-mesa-dev xorg-dev

# macOS
brew install go
```

### Projekt aufsetzen
```bash
git clone https://github.com/[dein-username]/go-to-bed.git
cd go-to-bed
make deps
make build
```

### Testen
```bash
# Direkt ausführen (testet nur einmal)
make run

# Oder mit custom Bedtime für sofortigen Test (in 1 Minute)
CURRENT_TIME=$(date -d '+1 minute' +%H:%M)
cat > ~/.go-to-bed.conf << EOF
{
  "bedtime": "$CURRENT_TIME",
  "weekdays": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
}
EOF
make run
```

### Release erstellen
```bash
# Tag erstellen
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions erstellt automatisch alle Binaries!
```

## Konfiguration ändern

```bash
./configure.sh
```

Das Skript fragt dich:
1. **Schlafenszeit** (z.B. 22:00)
2. **Wochentage** (Jeden Tag, Werktage, Wochenende, oder Benutzerdefiniert)

Oder direkt editieren:
```bash
# JSON-Format verwenden
cat > ~/.go-to-bed.conf << EOF
{
  "bedtime": "23:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
EOF

systemctl --user restart go-to-bed
```

## Troubleshooting

### Service läuft nicht
```bash
systemctl --user status go-to-bed
journalctl --user -u go-to-bed -n 50
```

### Vollbild funktioniert nicht
Stelle sicher, dass du in einer grafischen Umgebung arbeitest (X11/Wayland).

### Uhrzeit ändern
```bash
./configure.sh
systemctl --user restart go-to-bed
```

## Nächste Schritte

- ⭐ Gib dem Projekt einen Star auf GitHub
- 🐛 Gefunden einen Bug? [Öffne ein Issue](../../issues)
- 💡 Feature-Idee? [Öffne eine Discussion](../../discussions)
- 🤝 Möchtest du beitragen? Siehe [CONTRIBUTING.md](CONTRIBUTING.md)
