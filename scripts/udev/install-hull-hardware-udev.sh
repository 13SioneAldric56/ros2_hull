#!/usr/bin/env bash
set -euo pipefail

RULE_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/99-hull-hardware.rules"
RULE_DST="/etc/udev/rules.d/99-hull-hardware.rules"

sudo cp "$RULE_SRC" "$RULE_DST"
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty --action=add

echo "Installed: $RULE_DST"
echo "Optional symlinks:"
echo "  /dev/hull_gps   (GPS,   ttyACM0)"
echo "  /dev/hull_esp32 (ESP32, ttyUSB0, GX frames)"
