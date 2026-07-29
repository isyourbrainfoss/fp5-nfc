# Fairphone 5 — NFC (ST21NFCD)

Linux bring-up notes for the **ST21NFCD** NFC controller on Fairphone 5
(Qualcomm SM7325 / sc7280): device tree, Kconfig, and electrical checks.

Status: **experimental**. Tag discovery (ISO15693) was proven with raw NCI
and with mainline **st-nci** once DT + modules are present. Not an official
Fairphone or distribution package.

## Hardware

| Item | Value |
|------|--------|
| Controller | ST21NFCD |
| Bus | I2C @ `0x08` (SoC `a84000` → typically i2c-9) |
| Reset | TLMM GPIO **38** (must idle **high**) |
| IRQ | TLMM GPIO **41** |
| Clkreq | TLMM GPIO 39 (optional / not required for basic DT) |
| Mainline compatible | `st,st21nfcb-i2c` (`drivers/nfc/st-nci`) |

## Repository layout

```
dt/         Board DT fragment + example patch
kconfig/    Kernel config fragment for st-nci I2C
scripts/    I2C presence probe, raw NCI tag smoke, module load helper
```

## Kernel integration

1. Enable options in `kconfig/nfc.config` (or equivalent).
2. Merge `dt/st21nfc.dtsi` into the board DTS (correct `&i2cN` phandle).
3. Build NFC modules + DTB; boot with the new DT.

Firmware blobs (`st21nfc_fw.bin`, etc.) are **not** redistributed here. Obtain
them from a Fairphone Android vendor image or your distro’s firmware package
and install under `/lib/firmware/` as required by the stack.

## Validation

```sh
# Electrical presence (root, no kernel driver required)
sudo python3 scripts/probe-i2c.py

# Optional: raw NCI ISO15693 UID (root; hold a tag near the camera area)
sudo python3 scripts/raw-nci-tag-smoke.py

# With st-nci bound:
ls /sys/class/nfc
# then use your userspace (neard, nfctool, …)
```

## Pitfalls

- **Reset polarity / idle level:** if GPIO 38 is left low, the chip does not
  answer on I2C.
- **Framing:** this silicon wants **raw NCI**, not NDLC-over-I2C assumptions
  from some older ST docs.
- **NCI 2.0 CORE_INIT:** use payload `00 00` (`20 01 02 00 00`), not an empty
  init that older stacks send.

## Upstream

DT + Kconfig enablement are normal mainline / distro kernel material. Driver
fixes, if any, should go to `drivers/nfc/st-nci` with a proper series.

## License

GPL-2.0-only for DT/kernel material; see `LICENSE`.
