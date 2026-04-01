#!/bin/bash

# Installation script for Go-to-Bed (Linux/systemd)

set -e

INSTALL_DIR="/opt/go-to-bed"
BINARY_NAME="go-to-bed"
SERVICE_NAME="go-to-bed"

echo "==================================="
echo "   Go-to-Bed Installer"
echo "==================================="
echo ""

# Check if running as root for system-wide installation
if [ "$EUID" -eq 0 ]; then 
    echo "Installing system-wide..."
    INSTALL_MODE="system"
    SERVICE_DIR="/etc/systemd/system"
else
    echo "Installing for current user..."
    INSTALL_MODE="user"
    INSTALL_DIR="$HOME/.local/bin"
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
fi

# Copy binary
echo "→ Installing binary to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp "$BINARY_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# Create systemd service file
echo "→ Creating systemd service..."

if [ "$INSTALL_MODE" = "system" ]; then
    cat > "$SERVICE_DIR/$SERVICE_NAME.service" << EOF
[Unit]
Description=Go-to-Bed Reminder Service
After=graphical.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/$BINARY_NAME
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
else
    cat > "$SERVICE_DIR/$SERVICE_NAME.service" << EOF
[Unit]
Description=Go-to-Bed Reminder Service
After=graphical-session.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/$BINARY_NAME
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
fi

# Reload systemd and enable service
echo "→ Enabling service..."
if [ "$INSTALL_MODE" = "system" ]; then
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
else
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME"
    systemctl --user start "$SERVICE_NAME"
fi

# Run configuration
echo ""
echo "✓ Installation complete!"
echo ""
echo "Now let's configure your bedtime..."
echo ""

# Make configure script executable and run it
chmod +x configure.sh
./configure.sh

echo ""
echo "==================================="
echo "   Installation Summary"
echo "==================================="
echo "Service: $SERVICE_NAME"
echo "Status commands:"
if [ "$INSTALL_MODE" = "system" ]; then
    echo "  systemctl status $SERVICE_NAME"
    echo "  systemctl stop $SERVICE_NAME"
    echo "  systemctl restart $SERVICE_NAME"
    echo "  journalctl -u $SERVICE_NAME -f"
else
    echo "  systemctl --user status $SERVICE_NAME"
    echo "  systemctl --user stop $SERVICE_NAME"
    echo "  systemctl --user restart $SERVICE_NAME"
    echo "  journalctl --user -u $SERVICE_NAME -f"
fi
echo ""
echo "Configuration: Run './configure.sh' to change bedtime"
echo "==================================="
