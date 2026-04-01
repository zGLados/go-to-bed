package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/user"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"github.com/go-toast/toast"
)

const (
	defaultBedtime = "22:00"
	checkInterval  = 30 * time.Second
)

type Config struct {
	Bedtime  string   `json:"bedtime"`
	Weekdays []string `json:"weekdays"` // Mon, Tue, Wed, Thu, Fri, Sat, Sun
}

func main() {
	// Load configuration
	config := loadConfig()

	// Get current user
	currentUser, err := user.Current()
	if err != nil {
		log.Fatalf("Could not get current user: %v", err)
	}

	log.Printf("Go-to-Bed service started for user: %s", currentUser.Username)
	log.Printf("Bedtime set to: %s", config.Bedtime)
	log.Printf("Active weekdays: %s", strings.Join(config.Weekdays, ", "))

	// Run in background and check time periodically
	ticker := time.NewTicker(checkInterval)
	defer ticker.Stop()

	// Check immediately on start
	checkAndNotify(config, currentUser.Username)

	// Then check periodically
	for range ticker.C {
		checkAndNotify(config, currentUser.Username)
	}
}

func checkAndNotify(config Config, username string) {
	now := time.Now()
	
	// Check if today is an enabled weekday
	currentWeekday := now.Weekday().String()[:3] // Mon, Tue, Wed, etc.
	weekdayEnabled := false
	for _, day := range config.Weekdays {
		if strings.EqualFold(day, currentWeekday) {
			weekdayEnabled = true
			break
		}
	}
	
	if !weekdayEnabled {
		return
	}
	
	bedtime, err := time.Parse("15:04", config.Bedtime)
	if err != nil {
		log.Printf("Error parsing bedtime: %v", err)
		return
	}

	// Set bedtime to today's date
	bedtime = time.Date(now.Year(), now.Month(), now.Day(), 
		bedtime.Hour(), bedtime.Minute(), 0, 0, now.Location())

	// Check if current time matches bedtime (within a 1-minute window)
	diff := now.Sub(bedtime)
	if diff >= 0 && diff < checkInterval {
		log.Printf("Bedtime reached! Showing banner for %s on %s", username, currentWeekday)
		showBanner(username)
	}
}

func showBanner(username string) {
	// First show a system notification
	showSystemNotification(username)
	
	// Then show fullscreen banner
	showFullscreenBanner(username)
}

func showSystemNotification(username string) {
	notification := toast.Notification{
		AppID:   "Go-to-Bed",
		Title:   "Schlafenszeit!",
		Message: fmt.Sprintf("%s, es ist Zeit ins Bett zu gehen!", username),
	}
	err := notification.Push()
	if err != nil {
		log.Printf("Error showing notification: %v", err)
	}
}

func showFullscreenBanner(username string) {
	myApp := app.New()
	myWindow := myApp.NewWindow("Go to Bed!")

	// Create the message
	message := fmt.Sprintf("🌙 %s, es ist Zeit ins Bett zu gehen! 🌙", username)
	
	// Create large text labels
	title := canvas.NewText(message, nil)
	title.TextSize = 48
	title.Alignment = fyne.TextAlignCenter
	
	subtitle := canvas.NewText("Gute Nacht! 😴", nil)
	subtitle.TextSize = 36
	subtitle.Alignment = fyne.TextAlignCenter
	
	// Create dismiss button
	dismissButton := widget.NewButton("OK, ich gehe jetzt ins Bett", func() {
		myWindow.Close()
	})
	dismissButton.Importance = widget.HighImportance

	// Create container with content
	content := container.NewVBox(
		widget.NewLabel(""),
		widget.NewLabel(""),
		title,
		widget.NewLabel(""),
		subtitle,
		widget.NewLabel(""),
		widget.NewLabel(""),
		dismissButton,
	)

	myWindow.SetContent(content)
	myWindow.SetFullScreen(true)
	myWindow.CenterOnScreen()
	
	// Automatically close after 2 minutes if not dismissed
	go func() {
		time.Sleep(2 * time.Minute)
		myWindow.Close()
	}()

	myWindow.ShowAndRun()
}

func loadConfig() Config {
	// Default configuration (every day at 22:00)
	defaultConfig := Config{
		Bedtime:  defaultBedtime,
		Weekdays: []string{"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"},
	}
	
	// Try to load from config file
	configPath := getConfigPath()
	
	if !fileExists(configPath) {
		log.Printf("No config file found, using defaults")
		return defaultConfig
	}
	
	// Read config file
	data, err := os.ReadFile(configPath)
	if err != nil {
		log.Printf("Error reading config file: %v, using defaults", err)
		return defaultConfig
	}
	
	// Try to parse as JSON first
	var config Config
	if err := json.Unmarshal(data, &config); err == nil {
		// Validate config
		if config.Bedtime == "" {
			config.Bedtime = defaultBedtime
		}
		if len(config.Weekdays) == 0 {
			config.Weekdays = defaultConfig.Weekdays
		}
		log.Printf("Loaded config from JSON: %s on %s", config.Bedtime, strings.Join(config.Weekdays, ", "))
		return config
	}
	
	// Fallback: Try to parse as old format (simple time string)
	bedtime := strings.TrimSpace(string(data))
	if bedtime != "" {
		log.Printf("Loaded config from legacy format, converting to new format")
		config = Config{
			Bedtime:  bedtime,
			Weekdays: defaultConfig.Weekdays,
		}
		// Save in new format
		saveConfig(config)
		return config
	}
	
	log.Printf("Could not parse config file, using defaults")
	return defaultConfig
}

func saveConfig(config Config) error {
	configPath := getConfigPath()
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("error marshaling config: %w", err)
	}
	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return fmt.Errorf("error writing config: %w", err)
	}
	return nil
}

func getConfigPath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return ".go-to-bed.conf"
	}
	return fmt.Sprintf("%s/.go-to-bed.conf", home)
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
