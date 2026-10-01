#!/usr/bin/env bash
# Turns the screen off and on 20 times to check that it really sleeps and wakes.
# Run from a second console (Ctrl+Alt+F2): tools/screen_test.sh
set -euo pipefail

sudo systemctl stop birdclock || true
cage -- sh -c '
  for i in $(seq 20); do
    wlr-randr --output HDMI-A-1 --off; sleep 10
    wlr-randr --output HDMI-A-1 --on;  sleep 5
  done'
sudo systemctl start birdclock
