"""Screen power and keyboard/mouse detection."""

import glob
import subprocess


def input_present():
    """True if a USB keyboard or mouse is plugged in."""
    return bool(glob.glob("/dev/input/by-id/*-event-kbd") + glob.glob("/dev/input/by-id/*-event-mouse"))


def set_screen(on, cfg):
    subprocess.run(cfg["screen_on_cmd" if on else "screen_off_cmd"], shell=True)
