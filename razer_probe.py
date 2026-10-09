#!/usr/bin/env python3
"""Probe a Razer Tartarus V2 Pro (1532:02EB) for lighting control.

Sends lighting-effect commands only. Uses NOSTORE, so nothing is written
to the pad's onboard memory. Unplug/replug resets the pad.

Usage:
  python3 razer_probe.py list
  python3 razer_probe.py probe off [--all]
  python3 razer_probe.py probe red [--all]
  Add "--iface N" to test only one USB interface.

Packet layout and command IDs are from memory of the openrazer driver and
are UNVERIFIED for this device. The point of the probe is to find out
which style (if any) the pad answers to.
"""
import sys
import time

import hid

VID, PID = 0x1532, 0x02EB
STATUS = {0: "new", 1: "busy", 2: "OK", 3: "FAILED", 4: "timeout", 5: "not supported"}


def report(tx, cls, cmd, args):
    r = bytearray(90)
    r[1] = tx              # transaction id
    r[5] = len(args)       # data size
    r[6] = cls             # command class
    r[7] = cmd             # command id
    r[8:8 + len(args)] = bytes(args)
    crc = 0
    for b in r[2:88]:
        crc ^= b
    r[88] = crc
    return bytes(r)


def send(dev, pkt):
    dev.send_feature_report(b"\x00" + pkt)
    time.sleep(0.05)
    resp = bytes(dev.get_feature_report(0, 91))
    return resp[1:] if len(resp) == 91 else resp


def candidates(effect):
    rgb = [255, 0, 0]
    for tx in (0x1F, 0xFF):
        for led in (0x05, 0x00):
            args = [0, led, 0, 0, 0, 0] if effect == "off" else [0, led, 1, 0, 0, 1] + rgb
            yield f"extended tx={tx:#04x} led={led:#04x}", report(tx, 0x0F, 0x02, args)
        args = [0] if effect == "off" else [6] + rgb
        yield f"standard tx={tx:#04x}", report(tx, 0x03, 0x0A, args)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    devs = hid.enumerate(VID, PID)
    if not devs:
        sys.exit("No device found for 1532:02EB. Is it plugged in?")

    if cmd == "list":
        for d in devs:
            print(f"interface={d['interface_number']} usage_page={d['usage_page']:#06x} "
                  f"usage={d['usage']:#04x} product={d['product_string']!r}")
        return

    effect = sys.argv[2] if len(sys.argv) > 2 else "off"
    ask_all = "--all" in sys.argv
    want = int(sys.argv[sys.argv.index("--iface") + 1]) if "--iface" in sys.argv else None
    for d in devs:
        iface = d["interface_number"]
        if want is not None and iface != want:
            continue
        dev = hid.device()
        try:
            dev.open_path(d["path"])
        except OSError as e:
            print(f"iface {iface}: open failed ({e}). Check Input Monitoring for Terminal.")
            continue
        for label, pkt in candidates(effect):
            try:
                resp = send(dev, pkt)
            except OSError as e:
                print(f"iface {iface} | {label} | error: {e}")
                continue
            st = resp[0] if resp else None
            print(f"iface {iface} | {label} | reply: {STATUS.get(st, st)}")
            if st == 2 or ask_all:
                if input("  did the lights change? [y/N] ").strip().lower() == "y":
                    print(f"*** WORKS: iface {iface} | {label}")
        dev.close()


if __name__ == "__main__":
    main()
