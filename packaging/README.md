# Distro packaging drafts (not submitted)

These are proposals only. Nothing has been sent to Nura or BengalOS.
Send them only once the raw-NCI driver patch is merged, or is carried as
a downstream patch in the distro kernel tree (sc7280-mainline).

State as of 2026-11-11:

| Distro | Kernel | NFC kconfig | DT node | neard |
|--------|--------|-------------|---------|-------|
| Nura edge (pmaports `577b7da7`) | `linux-postmarketos-qcom-sc7280` 7.2.9 (sc7280-mainline tag `v7.2.9-sc7280`) | `# CONFIG_NFC is not set` | no (comment only) | Alpine `neard` 0.20-r0 exists, not in device-fairphone-fp5 |
| BengalOS (`linux-sc7280` `bengalos/latest` `0a23f438`, 7.2.8) | `bengalos-kernel-sc7280` -> `linux-image-7.2.8-sc7280+` | `# CONFIG_NFC is not set` in `sc7280.config`; no NFC in `fp5_defconfig` | no (comment only) | `neard` installed (bengalos meta), but `disable neard.*` in the immutable-image preset because Phosh/GNOME have no NFC UI yet |

## Nura: `linux-postmarketos-qcom-sc7280`

1. Carry the v5 patches 0002 and 0003 (driver) and 0004 (DT) in the
   sc7280-mainline tree. This tree is the kernel source for both Nura and
   BengalOS.
2. Config (in `config-postmarketos-qcom-sc7280.aarch64`, then
   `pmbootstrap kconfig check`):

   ```
   CONFIG_NFC=m
   CONFIG_NFC_NCI=m
   CONFIG_NFC_ST_NCI_I2C=m
   ```

3. `device-fairphone-fp5`: optional `neard` (and `neard-openrc` /
   `neard-systemd`) in an `nfc` subpackage, or a pointer in the wiki.
4. `kconfig-generic.toml` `category:nfc` currently lists PN5xx/HCI only.
   Adding `NFC_NCI` and `NFC_ST_NCI_I2C` there would also cover generic
   kernels.

## BengalOS: `pkgs/kernels/linux-sc7280`

1. Same driver and DT patches (best taken from sc7280-mainline).
2. `arch/arm64/configs/sc7280.config` (and `fp5_defconfig` if it is
   used for FP5 images): the same three `=m` lines as above.
3. Keep `neard` disabled by default until Phosh has an NFC consumer. For
   testing: `systemctl enable --now neard` and `nfctool -d nfc0 -1 -p`.
