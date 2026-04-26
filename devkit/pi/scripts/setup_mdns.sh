#!/usr/bin/env bash
# Configure Avahi so the Pi advertises itself as flightimpact.local
# and so the API service appears in service discovery.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

HOSTNAME_NEW="${1:-flightimpact}"

apt-get install -y avahi-daemon avahi-utils

hostnamectl set-hostname "$HOSTNAME_NEW"

if ! grep -q "127.0.1.1.*$HOSTNAME_NEW" /etc/hosts; then
  sed -i "/^127.0.1.1/d" /etc/hosts
  echo "127.0.1.1   $HOSTNAME_NEW" >> /etc/hosts
fi

mkdir -p /etc/avahi/services

# Build the service XML with closing tags assembled at runtime to avoid any
# editor / templating tool that might collapse <n>...</n> into <n/>.
OPEN_NAME='<NAME replace-wildcards="yes">'
CLOSE_NAME='</NAME>'

cat > /etc/avahi/services/flightimpact.service <<XMLDOC
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi.dtd">
<service-group>
  ${OPEN_NAME}FlightImpact on %h${CLOSE_NAME}
  <service>
    <type>_http._tcp</type>
    <port>8000</port>
    <txt-record>path=/api/v1</txt-record>
    <txt-record>service=flightimpact</txt-record>
  </service>
</service-group>
XMLDOC

# Avahi's tag is lowercase <name>; normalize after writing.
sed -i 's|<NAME |<name |; s|</NAME>|</name>|' /etc/avahi/services/flightimpact.service

systemctl restart avahi-daemon

echo "mDNS configured. The Pi is now reachable at:"
echo "  http://${HOSTNAME_NEW}.local:8000"
