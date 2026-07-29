#!/usr/bin/env python3
"""Fairphone 5 ST21NFCD raw NCI tag smoke test.

Requires root, python3-libgpiod, and i2c-tools. Prefer kernel st-nci + userspace
NFC tools once DT and modules are live; this script is a low-level electrical
and protocol check (raw NCI + ISO15693 UID).
"""
from __future__ import annotations
import os, sys, time, subprocess
import gpiod
from gpiod.line import Direction, Value

def tlmm():
    for name in sorted(os.listdir("/dev")):
        if not name.startswith("gpiochip"):
            continue
        path = f"/dev/{name}"
        with gpiod.Chip(path) as chip:
            info = chip.get_info()
            if "tlmm" in (info.label or "").lower() or info.num_lines >= 176:
                return path
    raise SystemExit("tlmm not found")

def wr(data: list[int]) -> bool:
    args = ["i2ctransfer", "-y", "9", f"w{len(data)}@0x08"] + [f"0x{b:02x}" for b in data]
    return subprocess.run(args, capture_output=True).returncode == 0

def rd(n: int) -> bytes | None:
    r = subprocess.run(["i2ctransfer", "-y", "9", f"r{n}@0x08"], capture_output=True, text=True)
    if r.returncode:
        return None
    return bytes(int(x, 16) for x in r.stdout.split())

def frame(req, timeout=0.5):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if req.get_value(41) == Value.INACTIVE:
            time.sleep(0.002)
            continue
        hdr = rd(3)
        if not hdr or len(hdr) < 3:
            continue
        plen = hdr[2]
        if plen > 250:
            rd(1)
            continue
        pl = rd(plen) if plen else b""
        return (hdr[0] >> 5) & 7, hdr[0] & 0xF, hdr[1], pl or b""
    return None

def drain(req, t=0.3):
    while frame(req, 0.05):
        pass

def main() -> int:
    if os.geteuid() != 0:
        print("need root", file=sys.stderr)
        return 2
    path = tlmm()
    with gpiod.request_lines(path, consumer="raw-nci-smoke", config={
        38: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
        41: gpiod.LineSettings(direction=Direction.INPUT),
    }) as req:
        time.sleep(0.02)
        req.set_value(38, Value.ACTIVE)  # chip live
        time.sleep(0.15)
        drain(req)
        wr([0x20, 0x00, 0x01, 0x01])
        drain(req, 0.4)
        wr([0x20, 0x01, 0x02, 0x00, 0x00])  # NCI 2.0 INIT
        fr = frame(req, 1.0)
        if not fr or fr[0] != 2 or fr[3][:1] != b"\x00":
            print("CORE_INIT failed", fr)
            return 1
        print("CORE_INIT OK")
        conf = bytes([5, 0x01, 0x01, 0x01, 0x02, 0x01, 0x01, 0x03, 0x01, 0x01, 0x04, 0x01, 0x02, 0x05, 0x01, 0x03])
        wr(list(bytes([0x21, 0x00, len(conf)]) + conf))
        drain(req, 0.3)
        conf = bytes([5, 0x00, 0x01, 0x01, 0x01, 0x02, 0x01, 0x03, 0x01, 0x06, 0x01])
        wr(list(bytes([0x21, 0x03, len(conf)]) + conf))
        print("RF_DISCOVER — present tag near camera (12s)")
        t0 = time.time()
        while time.time() - t0 < 12:
            fr = frame(req, 0.3)
            if not fr:
                continue
            mt, gid, oid, pl = fr
            if mt == 3 and gid == 1 and oid in (3, 5):
                print("ACTIVATED", pl.hex())
                if len(pl) >= 17 and pl[6] >= 10:
                    # tech params after 7-byte fixed prefix; ISO15693 uid 8B at +2 of tech
                    tech = pl[7:7 + pl[6]]
                    if len(tech) >= 10:
                        uid = tech[2:10]
                        print("ISO15693 UID LSB-first:", uid.hex(":"))
                        print("ISO15693 UID MSB-first:", uid[::-1].hex(":"))
                return 0
        print("no tag")
        return 1

if __name__ == "__main__":
    sys.exit(main())
