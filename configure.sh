#!/bin/bash

# Configuration script for Go-to-Bed

CONFIG_FILE="$HOME/.go-to-bed.conf"

echo "==================================="
echo "   Go-to-Bed Configuration"
echo "==================================="
echo ""

# Check if config exists and show current settings
if [ -f "$CONFIG_FILE" ]; then
    echo "Current configuration:"
    cat "$CONFIG_FILE"
    echo ""
fi

# Ask for bedtime
echo "Schritt 1: Schlafenszeit festlegen"
echo "-----------------------------------"
echo "Gib deine Schlafenszeit im 24-Stunden-Format ein (HH:MM)"
echo "Beispiele: 22:00, 23:30, 21:15"
read -p "Schlafenszeit: " BEDTIME

# Validate format (basic)
if [[ ! $BEDTIME =~ ^[0-2][0-9]:[0-5][0-9]$ ]]; then
    echo "Fehler: Ungültiges Zeitformat. Bitte verwende HH:MM (z.B. 22:00)"
    exit 1
fi

# Ask for weekdays
echo ""
echo "Schritt 2: Wochentage auswählen"
echo "-----------------------------------"
echo "An welchen Wochentagen soll die Erinnerung angezeigt werden?"
echo ""
echo "Bitte wähle eine Option:"
echo "  1) Jeden Tag (Montag bis Sonntag)"
echo "  2) Werktage (Montag bis Freitag)"
echo "  3) Wochenende (Samstag und Sonntag)"
echo "  4) Benutzerdefiniert"
echo ""
read -p "Deine Auswahl (1-4): " WEEKDAY_CHOICE

case $WEEKDAY_CHOICE in
    1)
        WEEKDAYS='["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'
        echo "✓ Jeden Tag ausgewählt"
        ;;
    2)
        WEEKDAYS='["Mon","Tue","Wed","Thu","Fri"]'
        echo "✓ Werktage ausgewählt"
        ;;
    3)
        WEEKDAYS='["Sat","Sun"]'
        echo "✓ Wochenende ausgewählt"
        ;;
    4)
        echo ""
        echo "Wähle die gewünschten Tage (j/n):"
        SELECTED_DAYS=()
        
        for day_full in "Montag:Mon" "Dienstag:Tue" "Mittwoch:Wed" "Donnerstag:Thu" "Freitag:Fri" "Samstag:Sat" "Sonntag:Sun"; do
            day_name="${day_full%%:*}"
            day_short="${day_full##*:}"
            read -p "  ${day_name}? (j/n): " yn
            if [[ $yn =~ ^[jJyY]$ ]]; then
                SELECTED_DAYS+=("\"$day_short\"")
            fi
        done
        
        if [ ${#SELECTED_DAYS[@]} -eq 0 ]; then
            echo "Fehler: Du musst mindestens einen Tag auswählen!"
            exit 1
        fi
        
        # Join array elements with comma
        WEEKDAYS="[$(IFS=,; echo "${SELECTED_DAYS[*]}")]"
        echo "✓ Benutzerdefinierte Auswahl gespeichert"
        ;;
    *)
        echo "Fehler: Ungültige Auswahl!"
        exit 1
        ;;
esac

# Create JSON config
cat > "$CONFIG_FILE" << EOF
{
  "bedtime": "$BEDTIME",
  "weekdays": $WEEKDAYS
}
EOF

echo ""
echo "==================================="
echo "✓ Konfiguration gespeichert!"
echo "==================================="
echo ""
echo "Deine Einstellungen:"
echo "  Schlafenszeit: $BEDTIME"
echo "  Konfiguration: $CONFIG_FILE"
echo ""
cat "$CONFIG_FILE"
echo ""
echo "Wichtig: Starte den go-to-bed Service neu, damit die Änderungen wirksam werden."
echo ""
echo "Befehle:"
echo "  systemctl --user restart go-to-bed"
echo "  systemctl --user status go-to-bed"

