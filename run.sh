#!/usr/bin/env bash
# Runs the clock. ~/.profile starts this after the auto-login on tty1.
# If the clock exits, it is not restarted: the console stays on screen so the crash is noticed. Reboot to restart.
# Output goes to the system log: journalctl -t birdclock
cd "$(dirname "$0")"
SDL_VIDEODRIVER=wayland cage -- python3 -m birdclock 2>&1 | systemd-cat -t birdclock
echo "The bird clock stopped. See why with: journalctl -t birdclock"
