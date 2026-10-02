#!/usr/bin/env bash
# One-time Pi setup. Run as the normal user from the repo folder: ./setup.sh
# Safe to re-run after an update.
set -euo pipefail
cd "$(dirname "$0")"

echo "Installing packages..."
sudo apt-get update
sudo apt-get install -y ddcutil python3-pygame

echo "Locking down the network..."
sudo systemctl disable --now ssh || true
sudo tee /etc/systemd/system/radios-off.service >/dev/null <<EOF
[Unit]
Description=Turn off Wi-Fi and Bluetooth at every boot
After=systemd-rfkill.service NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/sbin/rfkill block bluetooth
# NetworkManager turns Wi-Fi back on after an rfkill block, so turn it off through NetworkManager.
ExecStart=/usr/bin/nmcli radio wifi off

[Install]
WantedBy=multi-user.target
EOF

echo "Setting the time from time.txt at every boot..."
# The Pi has no clock battery and Wi-Fi is off, so it can't keep the time itself.
sudo tee /etc/systemd/system/set-time.service >/dev/null <<EOF
[Unit]
Description=Set the time from time.txt
After=fake-hwclock.service systemd-timesyncd.service
Before=getty@tty1.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'date -s "\$\$(cat $PWD/time.txt)"'

[Install]
WantedBy=multi-user.target
EOF

echo "Setting the clock to start on boot..."
# Log in automatically on tty1, then ~/.profile starts the clock there.
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf >/dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF
start_line="[ \"\$(tty)\" = /dev/tty1 ] && $PWD/run.sh"
grep -qxF "$start_line" ~/.profile 2>/dev/null || echo "$start_line" >> ~/.profile

sudo systemctl daemon-reload
sudo systemctl enable radios-off.service set-time.service
echo "Done. Reboot to start the clock: sudo reboot"
