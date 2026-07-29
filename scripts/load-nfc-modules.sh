#!/bin/sh
# Load mainline NFC stack modules (names may vary slightly by tree).
set -e
for m in nfc nci st-nci st-nci_i2c; do
	modprobe "$m" 2>/dev/null || insmod "/lib/modules/$(uname -r)/extra/nfc/${m}.ko" 2>/dev/null || true
done
lsmod | grep -E 'nfc|nci|st_nci' || true
ls -l /sys/class/nfc 2>/dev/null || echo "no /sys/class/nfc yet (DT/modules?)"
