#!/usr/bin/env python3
"""Prove ST21NFCD is electrically present on Fairphone 5 (I2C-9 @ 0x08).

Pulses TLMM reset GPIO 38, then i2cget on bus 9 address 0x08.
Exit 0 only if a byte is read successfully.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

try:
    import gpiod
    from gpiod.line import Direction, Value
except ImportError:
    print("NEED: install python3-libgpiod and i2c-tools", file=sys.stderr)
    sys.exit(2)

I2C_BUS = 9
I2C_ADDR = 0x08
RESET_LINE = 38


def find_tlmm() -> str:
    for name in sorted(os.listdir("/dev")):
        if not name.startswith("gpiochip"):
            continue
        path = f"/dev/{name}"
        with gpiod.Chip(path) as chip:
            info = chip.get_info()
            if "tlmm" in (info.label or "").lower() or "pinctrl" in (info.label or "").lower():
                if info.num_lines > 100:
                    return path
            if info.num_lines >= 176:
                return path
    raise RuntimeError("tlmm gpiochip not found")


def i2cget(bus: int, addr: int) -> str | None:
    r = subprocess.run(
        ["i2cget", "-y", str(bus), f"0x{addr:02x}", "0"],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return r.stdout.strip()
    return None


def main() -> int:
    if os.geteuid() != 0:
        print("run as root", file=sys.stderr)
        return 2
    before = i2cget(I2C_BUS, I2C_ADDR)
    print(f"before_reset: {before!r}")
    chip = find_tlmm()
    print(f"tlmm={chip}")
    with gpiod.request_lines(
        chip,
        consumer="probe_st21_i2c",
        config={
            RESET_LINE: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.INACTIVE
            )
        },
    ) as req:
        time.sleep(0.02)
        req.set_value(RESET_LINE, Value.ACTIVE)
        time.sleep(0.1)
    after = i2cget(I2C_BUS, I2C_ADDR)
    print(f"after_reset: {after!r}")
    if after is None:
        print("FAIL: no I2C response from ST21 at 0x08")
        return 1
    print(f"PASS: ST21 responded with {after} on i2c-{I2C_BUS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
