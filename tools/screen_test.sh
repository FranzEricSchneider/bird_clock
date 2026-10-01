#!/usr/bin/env bash
# Turns the screen off and on 20 times to check that it really sleeps and wakes.
# Press Escape to quit the clock first, then run: tools/screen_test.sh
set -euo pipefail

for i in $(seq 20); do
  ddcutil setvcp d6 4; sleep 10
  ddcutil setvcp d6 1; sleep 5
done
