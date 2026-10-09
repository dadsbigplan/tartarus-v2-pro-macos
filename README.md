# tartarus-v2-pro-macos

A small Python script that controls the lighting on a Razer Tartarus V2 Pro (USB 1532:02EB) from macOS, with no Razer software. Razer doesn't ship a Mac app for this pad.

It can switch the built-in effects (wave, spectrum, breathing, starlight, reactive), set a solid color or turn the lights off, change effect speed, and set brightness. With `--store`, the pad saves the setting itself, so nothing needs to run in the background.

## Tested on

- One Razer Tartarus V2 Pro (1532:02EB)
- macOS 27 on Apple Silicon

That's all it's been tested on. Other Razer devices, other macOS versions, and other firmware are untested.

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install hidapi

macOS may ask for Input Monitoring permission for Terminal the first time you run it.

## Usage

    ~/path/to/.venv/bin/python razer_light.py wave
    ~/path/to/.venv/bin/python razer_light.py off
    ~/path/to/.venv/bin/python razer_light.py brightness 20

Add `--store` to save the setting to the pad's onboard memory. Without it, the setting is temporary and resets when you unplug the pad.

The full command list, speed ranges, and test notes are in [tartarus-v2-pro-lighting.md](tartarus-v2-pro-lighting.md).

## Files

- `razer_light.py`: the lighting script
- `razer_probe.py`: the discovery script used to find which interface and packet style the pad answers to
- `tartarus-v2-pro-lighting.md`: command reference and test notes

## Warnings

- `--store` writes to the pad's memory. I don't know the rewrite limit. Use it for deliberate changes, not in anything automated.
- The packet format follows the openrazer driver for Linux, from memory, and was confirmed only by testing on one pad.
- This does not enable the thumbstick. That needs Razer's Synapse.

## Credits

Packet format and the idea come from the [openrazer](https://github.com/openrazer/openrazer) project. This is an independent script, not affiliated with Razer or openrazer.

## Support

None promised. It works on my pad. If you try it on another device, you're on your own. Issues and pull requests may sit unanswered.

## License

MIT
