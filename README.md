# bird_clock

A Raspberry Pi clock that wakes its screen each hour, shows a bird, plays its call, then goes back to sleep. It runs offline with only a screen and speaker attached.

## How it works

Each hour, outside quiet hours (default 22:00–07:00):
1. The screen wakes about 1 minute early and shows an analog clock.
2. On the hour, the bird's picture appears over the clock, and one of its sounds plays 1–3 times (up to 30 seconds total).
3. The bird's name appears, the bird fades out, and the screen sleeps about 1 minute later.

Between chimes the screen goes into power-save mode instead of showing black. Plugging in a USB keyboard or mouse keeps it on, and during quiet hours it also shows each hour's bird and name, without sound. The Pi's clock is trusted as-is. Wi-Fi, Bluetooth and SSH stay off, so the clock is safe to leave running.

## Hardware

- Raspberry Pi 4 Model B running Raspberry Pi OS Lite (64-bit)
- A screen on the micro-HDMI port next to the power jack
- A powered speaker, on the 3.5mm jack or over HDMI
- A 5V 3A USB-C power supply
- A USB keyboard and mouse, for maintenance only

## Install

On the Pi, with Wi-Fi on and a keyboard plugged in:

```
git clone https://github.com/FranzEricSchneider/bird_clock.git
cd bird_clock && ./setup.sh && sudo reboot
```

`setup.sh` installs `ddcutil` and `pygame`, and disables SSH. It also turns Wi-Fi and Bluetooth off at every boot and logs in automatically on the first console at boot, where `run.sh` starts the clock. If the clock crashes, it is not restarted: the console stays on screen until a reboot. Running it again is safe.

## Bird files

The bird files live in `~/bird-assets` on the Pi, not in this repo:

```
bird-assets/
  01/ … 12/        one folder per clock number; 7 AM and 7 PM both use 07/
    image.png      512x512 circle picture: black ring, transparent corners
    name.txt
    sounds/*.ogg   one is picked at random each hour
```

You choose which birds go in which hours. A missing or broken hour is skipped.

Build the folders on a laptop, which needs `pygame` and `ffmpeg`, then copy them to the Pi:

```
tools/add_bird.py --dest /media/usb/bird-assets --hour 7 \
    --name "American Robin" --image robin.jpg --sound robin1.mp3 --sound robin2.wav
tools/check_assets.py /media/usb/bird-assets
tools/install_assets.sh /media/usb/bird-assets     # on the Pi
```

`add_bird.py` opens a crop window: drag to move the picture, scroll or press `+`/`-` to zoom, and press Enter to save. It converts sounds to `.ogg` with every clip's loudest moment at the same level (-1 dB). Every option is optional, so one part of an hour can be updated at a time.

## Maintenance

Plug in a keyboard, wait about 10 seconds for the screen to wake, and press Escape. The clock quits and leaves a logged-in prompt on screen. Ctrl+Alt+F2 does not work while the clock runs. Reboot to start the clock again.

- **Set the time:** `sudo date -s "2026-09-30 14:05"`
- **Turn on Wi-Fi:** `sudo nmcli radio wifi on`, then wait about 15 seconds for it to connect. `hostname -I` shows the Pi's address. `sudo nmcli radio wifi off` or a reboot turns it off again.
- **Update:** `sudo nmcli radio wifi on && sleep 15 && git pull; sudo reboot` (Wi-Fi turns off again at boot)
- **Logs:** `journalctl -t birdclock`. Raspberry Pi OS keeps logs in memory, so they cover only the current boot.

Wi-Fi is turned off again at every boot, even if it was left on.

## Settings

The defaults are in `config.default.toml`: quiet hours, timing, volume and the screen sleep commands. To change a setting, copy just that line into `config.toml`, which is not tracked by git.

## First-boot checks

- The display, speaker (`speaker-test -c2 -t wav`), keyboard and mouse all work. If sound comes out of the wrong output, change it with `sudo raspi-config` → System Options → Audio.
- **Power:** after a while running, `vcgencmd get_throttled` should print `throttled=0x0`. Anything else means the supply is too weak; use the official 5.1V one.
- **Screen sleep:** press Escape to quit the clock, then run `tools/screen_test.sh`. The screen should go into power-save mode (not "No signal", and not a lit black screen) and wake again, 20 times in a row. If it doesn't, the monitor may not accept power commands over HDMI (`ddcutil detect` shows whether it answers). Change `screen_off_cmd`/`screen_on_cmd`, for example to HDMI-CEC (`cec-ctl`) for TVs.

## Development

```
pip install pygame pytest
python3 -m birdclock --window --fast   # in a window, with each hour lasting 1 minute
python3 -m pytest
```
