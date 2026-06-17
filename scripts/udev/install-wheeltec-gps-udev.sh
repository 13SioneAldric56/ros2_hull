#!/usr/bin/env bash
set -euo pipefail

RULE_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/99-wheeltec-gps.rules"
RULE_DST="/etc/udev/rules.d/99-wheeltec-gps.rules"

sudo cp "$RULE_SRC" "$RULE_DST"
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=tty --action=add

echo "Installed: $RULE_DST"
echo "Expected symlink: /dev/wheeltec_gps -> $(readlink -f /dev/wheeltec_gps 2>/dev/null || echo 'pending replug')"
