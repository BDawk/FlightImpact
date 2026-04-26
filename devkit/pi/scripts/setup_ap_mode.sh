#!/usr/bin/env bash
# Set up the Raspberry Pi 5 as a Wi-Fi access point so a phone can connect
# directly with no router involved. Uses NetworkManager (default on Pi OS Bookworm).
#
# Usage:  sudo ./setup_ap_mode.sh [SSID] [PASSPHRASE]
# Default SSID: FlightImpact-XXXX (XXXX = last 4 of MAC)
# Default pass: flightimpact
#
# To revert:  sudo nmcli connection delete flightimpact-ap

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

# Derive a unique SSID suffix from the wlan0 MAC
MAC_SUFFIX=$(cat /sys/class/net/wlan0/address 2>/dev/null | tr -d ':' | tail -c5 | tr 'a-f' 'A-F' || echo "0000")
SSID="${1:-FlightImpact-${MAC_SUFFIX}}"
PASS="${2:-flightimpact}"

if [[ ${#PASS} -lt 8 ]]; then
  echo "Passphrase must be at least 8 characters." >&2
  exit 1
fi

echo "Setting up access point:"
echo "  SSID: $SSID"
echo "  IP:   192.168.4.1"

# Remove any existing connection with the same name
nmcli connection delete flightimpact-ap 2>/dev/null || true

# Create the AP connection
nmcli connection add \
  type wifi \
  ifname wlan0 \
  con-name flightimpact-ap \
  autoconnect yes \
  ssid "$SSID" \
  mode ap \
  ipv4.method shared \
  ipv4.addresses 192.168.4.1/24 \
  ipv6.method disabled \
  802-11-wireless.band bg \
  802-11-wireless.channel 6 \
  802-11-wireless-security.key-mgmt wpa-psk \
  802-11-wireless-security.psk "$PASS"

# Activate it now
nmcli connection up flightimpact-ap

echo ""
echo "AP active. Connect your phone to:"
echo "  SSID: $SSID"
echo "  Pass: $PASS"
echo ""
echo "Then open: http://flightimpact.local:8000  (API)"
echo "          or http://192.168.4.1:8000"
