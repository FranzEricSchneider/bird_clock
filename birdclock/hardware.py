"""Screen power and keyboard detection."""

import glob
import subprocess


def input_present():
    """True if a USB keyboard is plugged in."""
    return bool(glob.glob("/dev/input/by-id/*-event-kbd"))


def set_screen(on, cfg):
    subprocess.run(cfg["screen_on_cmd" if on else "screen_off_cmd"], shell=True)
