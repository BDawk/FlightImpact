#!/usr/bin/env bash
# Install FlightImpact as a system service on the Pi.
# Idempotent — safe to re-run after a code update.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

PROJECT_ROOT="${1:-/opt/flightimpact}"
USER_NAME="flightimpact"

# Create service user if missing
if ! id "$USER_NAME" &>/dev/null; then
  useradd --system --no-create-home --shell /usr/sbin/nologin \
    --groups video,audio,dialout "$USER_NAME"
fi

# Data + log directories
mkdir -p /var/lib/flightimpact/{clips,radar} /var/log/flightimpact
chown -R "$USER_NAME:$USER_NAME" /var/lib/flightimpact /var/log/flightimpact

# Make sure project files exist
if [[ ! -d "$PROJECT_ROOT/devkit/pi" ]]; then
  echo "Project not found at $PROJECT_ROOT" >&2
  echo "Copy the repo to $PROJECT_ROOT first, then re-run this script." >&2
  exit 1
fi

# Create venv and install
if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
  python3 -m venv "$PROJECT_ROOT/venv"
fi
"$PROJECT_ROOT/venv/bin/pip" install --upgrade pip
"$PROJECT_ROOT/venv/bin/pip" install -e "$PROJECT_ROOT/core"
"$PROJECT_ROOT/venv/bin/pip" install -e "$PROJECT_ROOT/devkit/pi"

# Permissions
chown -R "$USER_NAME:$USER_NAME" "$PROJECT_ROOT"

# Install systemd unit
cp "$PROJECT_ROOT/devkit/pi/systemd/flightimpact-api.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable flightimpact-api
systemctl restart flightimpact-api

echo ""
echo "Service installed and started. Check status with:"
echo "  systemctl status flightimpact-api"
echo "  journalctl -u flightimpact-api -f"
