# Firmware: what the Linux NFC stack needs (and what it does not)

**Do not commit or redistribute ST21NFCD firmware blobs** (`st21nfc_fw.bin`
or similar) in this repository.

## Facts (checked 2026-11-11 against mainline 067c5c24 / next-20261110)

- `drivers/nfc/st-nci` has no firmware download path. It does not implement
  the `fw_download` NCI op and never calls `request_firmware()`. (Other NFC
  drivers do, e.g. `nxp-nci/firmware.c` and `s3fwrn5`.)
- The staged raw-NCI series (`upstream/st21nfcd-v5/`) does not add one
  either.
- Tag reads in the series cover letters (NTAG 215, Type 2, MIFARE Classic
  1K, ISO15693) ran with the firmware already on the controller. The host
  did not load anything.

So **basic reader mode on Linux needs no firmware file on the host**.

## When a firmware file matters

The Android stack (ST NFC HAL) can update the controller firmware from a
file in the vendor image. Linux has no equivalent today. Doing it would
need either:

1. a `fw_download` op in st-nci that speaks ST's update protocol (needs
   public documentation or a clean-room protocol description), or
2. a userspace updater that talks over `/dev/i2c-*` while st-nci is
   unbound.

Both are future work. Neither is needed for bring-up.

## If you need the file for comparison or a future updater

Get it yourself from your own device or image. Do not redistribute it:

- From a Fairphone 5 running stock Android with root: look under the
  vendor partition for the ST NFC firmware and config files, for example
  `adb shell su -c 'ls -l /vendor/firmware /vendor/etc | grep -i -E "st21|nfc"'`.
  The exact path depends on the build, so search rather than assume.
  Copy out only what you need for local analysis.
- Check the `vendor` partition of the matching official Fairphone OTA/factory
  image for the same build.

Nura's `firmware-fairphone-fp5` (from https://github.com/FairBlobs/FP5-firmware)
and the BengalOS firmware packages did not ship NFC firmware as of
2026-11-11. They do not need to for the Linux path above.
