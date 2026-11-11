# Staged upstream series: ST21NFCD raw-NCI support (v5)

**Status: posted to the mailing lists, NOT merged.** These patches are a
local copy for building test kernels. They are not in mainline or
linux-next, and no distro kernel carries them yet.

| | |
|---|---|
| Series | `[PATCH v5 0/4] nfc: st-nci: Fairphone 5 NFC bring-up (ST21NFCD)` |
| Posted | 2026-10-05 (20:51 UTC) |
| Message-ID | `20261005-fp5-st21nfcd-v5-v5-0-7be15a86c61c@proton.me` |
| Lore | https://lore.kernel.org/oe-linux-nfc/20261005-fp5-st21nfcd-v5-v5-0-7be15a86c61c@proton.me/ |
| Patchwork (oe-linux-nfc) | https://patchwork.kernel.org/project/oe-linux-nfc/list/?series=1179912 |
| Base in cover letter | `cee9395acd8043be0644b25c34bfa86623f2b935` |

The files here were exported with `git format-patch` after `git am` of the
patchwork mbox. Patch bodies, authorship and trailers are unchanged.

| # | Patch | Author | Review tags on v5 |
|---|-------|--------|-------------------|
| 1 | dt-bindings: net: nfc: add st,st21nfcd | Kristian Brox | Reviewed-by: Krzysztof Kozlowski |
| 2 | nfc: st-nci: add raw NCI path for ST21NFCD | Kristian Brox | none |
| 3 | nfc: st-nci: map proprietary RF protocol 0x90 to MIFARE | Tim auf der Landwehr | none |
| 4 | arm64: dts: qcom: qcm6490-fairphone-fp5: add ST21NFCD NFC | Kristian Brox | Reviewed-by: Konrad Dybcio, Abel Vesa |

## Apply check (2026-11-11)

`git am` of all four patches applies cleanly, no fuzz, on:

- mainline `067c5c24cef23d913b67eaaf71ae67e7169a6620` (master, after v7.4-rc2)
- linux-next `next-20261110` (`793807ca13bf3072fc6d16ce6d90e9ab9beff2a5`)

No compile or `dtbs_check` run was done for this check (the build box
could not install flex, bison, dtc or lld). Run those before a v6.

```sh
cd linux
git am /path/to/fp5-nfc/upstream/st21nfcd-v5/000*.patch
```

## Open review items (from the list, before a v6)

- Luca Weiss (v4, 2026-09-18): with neard, start poll, stop, start again
  gives `nci_start_poll: failed to set local general bytes` after a
  `__nci_request` timeout. Polling stays dead until reboot. Kristian could
  not reproduce it with nfctool or neard 0.20 (2026-09-23). The v5 cover
  letter still lists it as unreproduced. This is the main blocker.
- On every poll start, `nci_start_poll: failed to set listen parameters`:
  `CORE_SET_CONFIG` id `0x54` returns status `0x09` (reported by
  Kristian, 2026-09-23). Polling still works.
- Val Packett (v5, 2026-10-12): ST21NFCJ on the Motorola Edge 30 uses the
  same raw-NCI protocol but gets desynced frames (`7e 60 00`,
  `79 3e 59 c0 ...`). Tim's dropped workarounds (reference-clock restart,
  leading-`0x7e` check) did not fix it there.
- The automated review (Sashiko) flagged existing st-nci problems on
  v3/v4: no NCI unregister when `devm_request_threaded_irq()` fails, a
  teardown-order problem in `ndlc_remove()`, an skb size problem in the
  NDLC `st_nci_i2c_read()` path, and leaked supervisor skbs. These are
  old bugs, not new ones from the series. Separate prep fixes in front of
  the raw-NCI patch would make the series easier to merge.
- netdevbpf patchwork marks the series "awaiting-upstream". It goes
  through the NFC tree (oe-linux-nfc), so it needs an ack or pick-up from
  the NFC maintainer side.
