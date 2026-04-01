# Configuration script for Go-to-Bed (PowerShell)

$CONFIG_FILE = "$env:USERPROFILE\.go-to-bed.conf"

Write-Host "==================================="
Write-Host "   Go-to-Bed Configuration"
Write-Host "==================================="
Write-Host ""

# Check if config exists and show current settings
if (Test-Path $CONFIG_FILE) {
    Write-Host "Current configuration:"
    Get-Content $CONFIG_FILE
    Write-Host ""
}

# Ask for bedtime
Write-Host "Schritt 1: Schlafenszeit festlegen"
Write-Host "-----------------------------------"
Write-Host "Gib deine Schlafenszeit im 24-Stunden-Format ein (HH:MM)"
Write-Host "Beispiele: 22:00, 23:30, 21:15"
$BEDTIME = Read-Host "Schlafenszeit"

# Validate format (basic)
if ($BEDTIME -notmatch "^[0-2][0-9]:[0-5][0-9]$") {
    Write-Host "Fehler: Ungültiges Zeitformat. Bitte verwende HH:MM (z.B. 22:00)" -ForegroundColor Red
    exit 1
}

# Ask for weekdays
Write-Host ""
Write-Host "Schritt 2: Wochentage auswählen"
Write-Host "-----------------------------------"
Write-Host "An welchen Wochentagen soll die Erinnerung angezeigt werden?"
Write-Host ""
Write-Host "Bitte wähle eine Option:"
Write-Host "  1) Jeden Tag (Montag bis Sonntag)"
Write-Host "  2) Werktage (Montag bis Freitag)"
Write-Host "  3) Wochenende (Samstag und Sonntag)"
Write-Host "  4) Benutzerdefiniert"
Write-Host ""
$WEEKDAY_CHOICE = Read-Host "Deine Auswahl (1-4)"

switch ($WEEKDAY_CHOICE) {
    "1" {
        $WEEKDAYS = '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'
        Write-Host "✓ Jeden Tag ausgewählt" -ForegroundColor Green
    }
    "2" {
        $WEEKDAYS = '["Mon","Tue","Wed","Thu","Fri"]'
        Write-Host "✓ Werktage ausgewählt" -ForegroundColor Green
    }
    "3" {
        $WEEKDAYS = '["Sat","Sun"]'
        Write-Host "✓ Wochenende ausgewählt" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "Wähle die gewünschten Tage (j/n):"
        $SELECTED_DAYS = @()
        
        $days = @(
            @{Name="Montag"; Short="Mon"},
            @{Name="Dienstag"; Short="Tue"},
            @{Name="Mittwoch"; Short="Wed"},
            @{Name="Donnerstag"; Short="Thu"},
            @{Name="Freitag"; Short="Fri"},
            @{Name="Samstag"; Short="Sat"},
            @{Name="Sonntag"; Short="Sun"}
        )
        
        foreach ($day in $days) {
            $yn = Read-Host "  $($day.Name)? (j/n)"
            if ($yn -match "^[jJyY]$") {
                $SELECTED_DAYS += "`"$($day.Short)`""
            }
        }
        
        if ($SELECTED_DAYS.Count -eq 0) {
            Write-Host "Fehler: Du musst mindestens einen Tag auswählen!" -ForegroundColor Red
            exit 1
        }
        
        $WEEKDAYS = "[" + ($SELECTED_DAYS -join ",") + "]"
        Write-Host "✓ Benutzerdefinierte Auswahl gespeichert" -ForegroundColor Green
    }
    default {
        Write-Host "Fehler: Ungültige Auswahl!" -ForegroundColor Red
        exit 1
    }
}

# Create JSON config
$configContent = @"
{
  "bedtime": "$BEDTIME",
  "weekdays": $WEEKDAYS
}
"@

Set-Content -Path $CONFIG_FILE -Value $configContent

Write-Host ""
Write-Host "==================================="
Write-Host "✓ Konfiguration gespeichert!" -ForegroundColor Green
Write-Host "==================================="
Write-Host ""
Write-Host "Deine Einstellungen:"
Write-Host "  Schlafenszeit: $BEDTIME"
Write-Host "  Konfiguration: $CONFIG_FILE"
Write-Host ""
Get-Content $CONFIG_FILE
Write-Host ""
Write-Host "Wichtig: Starte die go-to-bed Anwendung neu, damit die Änderungen wirksam werden."
