#!/usr/bin/env python3
"""Control Tartarus V2 Pro (1532:02EB) lighting on macOS.

Uses the combo confirmed by razer_probe.py: HID interface 3, extended matrix
effect (class 0x0F, cmd 0x02), transaction id 0x1F, LED 0x05.

Usage:
  python3 razer_light.py off            # solid black (the "none" effect did nothing)
  python3 razer_light.py color ff8800   # solid color, hex RRGGBB
  python3 razer_light.py wave [1|2] [speed]   # 1 = left to right, 2 = right to left
                                        # speed = raw byte 1-255, default 40 (UNVERIFIED scale)
  python3 razer_light.py spectrum       # slow color-to-color transition
  python3 razer_light.py starlight [1-3]   # random twinkle, speed (UNVERIFIED speeds)
  python3 razer_light.py reactive [1-4]    # random color on keypress (UNVERIFIED speeds)
  python3 razer_light.py reactive-color ff0000 [1-4]   # fixed-color fallback
  python3 razer_light.py breathing          # pulse in random colors (UNVERIFIED)
  python3 razer_light.py breathing-color ff0000   # pulse in one color (UNVERIFIED)
  python3 razer_light.py brightness 0-100  # brightness percent (UNVERIFIED bytes)
  python3 razer_light.py getbrightness     # read current brightness (UNVERIFIED bytes)
Add --store to ask the pad to save the effect to onboard memory.
"""
import sys
import time

import hid

VID, PID, IFACE, TX, LED = 0x1532, 0x02EB, 3, 0x1F, 0x05


def report(cls, cmd, args):
    r = bytearray(90)
    r[1], r[5], r[6], r[7] = TX, len(args), cls, cmd
    r[8:8 + len(args)] = bytes(args)
    crc = 0
    for b in r[2:88]:
        crc ^= b
    r[88] = crc
    return bytes(r)


def build(argv, store):
    """Return (command_class, command_id, args)."""
    cmd = argv[0] if argv else ""
    fx = 0x0F, 0x02
    if cmd == "off":
        return (*fx, [store, LED, 1, 0, 0, 1, 0, 0, 0])
    if cmd == "color" and len(argv) > 1:
        c = bytes.fromhex(argv[1].lstrip("#"))
        return (*fx, [store, LED, 1, 0, 0, 1, c[0], c[1], c[2]])
    if cmd == "wave":
        direction = int(argv[1]) if len(argv) > 1 else 1
        wspeed = int(argv[2]) if len(argv) > 2 else 0x28   # raw byte, default 40
        return (*fx, [store, LED, 0x04, direction, wspeed, 0])
    if cmd == "spectrum":
        return (*fx, [store, LED, 0x03, 0, 0, 0])
    if cmd == "brightness" and len(argv) > 1:
        level = round(max(0, min(100, int(argv[1]))) * 255 / 100)
        return (0x0F, 0x04, [store, LED, level])
    if cmd == "getbrightness":
        return (0x0F, 0x84, [store, LED, 0])
    if cmd == "breathing":   # random colors (UNVERIFIED bytes)
        return (*fx, [store, LED, 0x02, 0, 0, 0])
    if cmd == "breathing-color" and len(argv) > 1:   # single fixed color
        c = bytes.fromhex(argv[1].lstrip("#"))
        return (*fx, [store, LED, 0x02, 1, 0, 1, c[0], c[1], c[2]])
    speed = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 2
    if cmd == "starlight":
        return (*fx, [store, LED, 0x07, 0, speed, 0])
    if cmd == "reactive":
        return (*fx, [store, LED, 0x05, 0, speed, 0])
    if cmd == "reactive-color" and len(argv) > 1:
        c = bytes.fromhex(argv[1].lstrip("#"))
        speed = int(argv[2]) if len(argv) > 2 else 2
        return (*fx, [store, LED, 0x05, 0, speed, 1, c[0], c[1], c[2]])
    sys.exit(__doc__)


def main():
    argv = [a for a in sys.argv[1:] if a != "--store"]
    store = 0x01 if "--store" in sys.argv else 0x00
    cls, cmd, args = build(argv, store)
    path = next((d["path"] for d in hid.enumerate(VID, PID)
                 if d["interface_number"] == IFACE), None)
    if path is None:
        sys.exit("Pad not found on interface 3. Is it plugged in?")
    dev = hid.device()
    dev.open_path(path)
    dev.send_feature_report(b"\x00" + report(cls, cmd, args))
    time.sleep(0.05)
    resp = bytes(dev.get_feature_report(0, 91))
    resp = resp[1:] if len(resp) == 91 else resp
    print("reply:", {2: "OK", 3: "FAILED", 5: "not supported"}.get(resp[0], resp[0]))
    if argv and argv[0] == "getbrightness":
        print(f"raw args: {resp[8:11].hex()}  (brightness byte = {resp[10]} of 255)")
    dev.close()


if __name__ == "__main__":
    main()
