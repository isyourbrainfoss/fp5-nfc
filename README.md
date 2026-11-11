# Fairphone 5 — NFC (ST21NFCD)

> **Note**
> This is very experimental. Assume nothing here is written, or necessarily read through or fully understood, by a human unless stated, and that includes this text. Use it at your own risk, but you're encouraged to reuse any parts you find useful. The human work here is mainly ideas, testing in reality, and persistence with a vision.

Linux bring-up notes for the **ST21NFCD** NFC controller on Fairphone 5
(Qualcomm QCM6490 / sc7280): device tree, Kconfig, the staged upstream
driver series, and electrical checks.

Status: **experimental**. ST21NFCD speaks **raw NCI**. Mainline `st-nci`
always wraps NDLC, so mainline alone (compatible `st,st21nfcb-i2c`) does
**not** give a working adapter. Tag reads (ISO15693, NTAG/Type 2, MIFARE
Classic 1K) were done with raw NCI from userspace and with `st-nci` plus
the raw-NCI series in [`upstream/st21nfcd-v5/`](upstream/st21nfcd-v5/).
That series is **posted, not merged** (v5, 2026-10-05). Not an official
Fairphone or distribution package.

## Hardware

| Item | Value |
|------|--------|
| Controller | ST21NFCD |
| Bus | I2C @ `0x08` (SoC `a84000` → typically i2c-9) |
| Reset | TLMM GPIO **38**, active-low (must idle **high** for the chip to run) |
| IRQ | TLMM GPIO **41**, level high |
| Clkreq | TLMM GPIO 39 (`NFC_CLK_REQ`, not described in DT) |
| SYS_CLK | `LN_BB_CLK2` (`&rpmhcc RPMH_LN_BB_CLK2`) |
| VPS_IO | L18B (`vreg_l18b`) |
| Compatible | `st,st21nfcd` (needs the staged series); mainline only has `st,st21nfcb-i2c` / `st,st21nfcc-i2c` (NDLC) |

The mainline FP5 DTS (v7.4-rc2+) still has only the comment
`/* ST21NFC NFC @ 28 */` under `&i2c9`. The chip answers at `0x08`
(see `scripts/probe-i2c.py`).

## Repository layout

```
dt/                    Board DT fragment (same node as upstream v5 patch 4)
kconfig/               Kernel config fragment for st-nci I2C
upstream/st21nfcd-v5/  Staged copy of the posted v5 series + review status
docs/                  Firmware notes
packaging/             Nura / BengalOS packaging drafts (not submitted)
scripts/               I2C presence probe, raw NCI tag smoke, module load helper
```

## Kernel integration

1. Start from mainline, linux-next or sc7280-mainline, then
   `git am upstream/st21nfcd-v5/000*.patch`. Patches 0001–0004 apply
   cleanly on mainline `067c5c24` and next-20261110. If your tree already
   has patch 0004, use `dt/st21nfc.dtsi` only as a reference.
2. Merge `kconfig/nfc.config`.
3. Build modules + DTB; boot with the new DT. The modules are `nfc`,
   `nci`, `st-nci`, `st-nci_i2c`.

## Firmware

Linux `st-nci` does not load firmware from the host. Reader mode works
with the firmware already on the controller. Firmware blobs
(`st21nfc_fw.bin`, etc.) are **not** redistributed here. See
[`docs/firmware.md`](docs/firmware.md).

## Validation

```sh
# Electrical presence (root, no kernel driver required)
sudo python3 scripts/probe-i2c.py

# Optional: raw NCI ISO15693 UID (root; hold a tag near the camera area)
sudo python3 scripts/raw-nci-tag-smoke.py

# With st-nci (+ raw-NCI series) bound:
ls /sys/class/nfc
nfctool -d nfc0 -1 -p          # neard's nfctool
```

## Pitfalls

- **Reset polarity / idle level:** if GPIO 38 is left low, the chip does not
  answer on I2C. In DT this is `GPIO_ACTIVE_LOW`.
- **Framing:** this silicon wants **raw NCI**, not NDLC-over-I2C as in
  the older ST21NFCB docs and mainline `st-nci`.
- **NCI 2.0 CORE_INIT:** use payload `00 00` (`20 01 02 00 00`), not an empty
  init that older stacks send.
- **Poll restart (open):** Luca Weiss reported `failed to set local general
  bytes` after stopping and restarting polling with neard. Not reproduced
  here yet; see `upstream/st21nfcd-v5/README.md`.

## Upstream

- Series: `[PATCH v5 0/4] nfc: st-nci: Fairphone 5 NFC bring-up (ST21NFCD)`,
  https://lore.kernel.org/oe-linux-nfc/20261005-fp5-st21nfcd-v5-v5-0-7be15a86c61c@proton.me/
- Not in mainline (`067c5c24`), linux-next (`next-20261110`),
  sc7280-mainline (`sc7280-7.3.y` `d4efb9f2`), Nura or BengalOS kernels as
  of 2026-11-11.
- Fairphone 4 (`sm7225-fairphone-fp4.dts`) also has `/* ST21NFCD NFC @ 8 */`
  and could reuse the same compatible.

## License

GPL-2.0-only for DT/kernel material; see `LICENSE`.
