# Tartarus V2 Pro lighting on macOS

Pad: Razer Tartarus V2 Pro, USB 1532:02EB
Script: `~/razer/razer_light.py`
Control channel: HID interface 3, extended matrix effect, transaction ID 0x1F, LED 0x05
Packet layout is from memory of the openrazer driver, confirmed only by the behavior below.

## Running it

From any folder, no venv activation needed:

    ~/razer/.venv/bin/python ~/razer/razer_light.py <command>

## Effects

| Command | What it does | Status |
| --- | --- | --- |
| `wave [1\|2] [speed]` | Color-cycling wave. 1 = left to right, 2 = right to left. Speed is 1-255, default 40, smooth range. | Tested, saves with --store |
| `spectrum` | Slow transition from color to color (pad's default) | Tested, saves with --store |
| `breathing` | Pulses in random colors | Tested, saves with --store |
| `breathing-color RRGGBB` | Pulses in one color | Red tested |
| `starlight [1-3]` | Keys twinkle randomly in random colors | Tested, saves with --store |
| `reactive [1-4]` | Key lights a random color on press, then fades | Tested, saves with --store |
| `reactive-color RRGGBB [1-4]` | Same as reactive, fixed color | Untested |
| `color RRGGBB` | Solid color, e.g. `ff8800` | Red tested |
| `off` | Fades to black (solid black, not the "none" effect) | Tested, saves with --store |

Speed numbers run the same direction everywhere: lower is faster, higher is slower.

- Wave: 1-255. At 200 the wave steps column to column.
- Starlight: 1-3.
- Reactive: 1-4 (higher means a longer glow).
- Spectrum and breathing have no speed setting that I know of.

## Brightness

| Command | What it does | Status |
| --- | --- | --- |
| `brightness 0-100` | Sets brightness by percent (maps to 0-255) | Tested, saves with --store |
| `getbrightness` | Reads the current value, out of 255 | Tested |

- 20 is a visible dimming. 50 looked barely different from full.
- 20% reads back as 51 of 255. The pad's default is 255.

## Saving to the pad

- No flag: the setting is temporary and reverts on unplug/replug (effect goes back to spectrum, brightness to 255).
- `--store`: saves to onboard memory. Confirmed to persist across replug for all effects, speed settings, and brightness.
- Example: `wave 1 25 --store`
- I don't know the memory's rewrite limit. Use `--store` for deliberate changes only, never in anything automated.

## Aliases (add to ~/.zshrc, open a new Terminal after)

    alias tartwave='~/razer/.venv/bin/python ~/razer/razer_light.py wave --store'
    alias tartoff='~/razer/.venv/bin/python ~/razer/razer_light.py off --store'

## Not supported

- Ripple (press spreads light to neighboring keys): probably drawn by Synapse, not a built-in effect, so it would need an always-running program. Skipped.
- Also not covered: per-key colors.
- Thumbstick: lighting commands don't touch it, and it still needs Synapse.

## Caveats

- Synapse on a Windows machine will probably override the lighting while it runs. Whether the stored Mac-side setting comes back afterward is untested.
- Interfaces 1 and 2 won't open on macOS (keyboard-class). Interface 4 returns junk. Only interface 3 matters.
- If macOS changes HID permissions or a firmware update changes the packet layout, the script is small enough to debug.
- To reset to defaults: `spectrum --store`, then `brightness 100 --store`. Untested. Synapse on Windows is the fallback.
