#!/usr/bin/env bash
# One-time Pi setup. Run as the normal user from the repo folder: ./setup.sh
# Safe to re-run after an update.
set -euo pipefail
cd "$(dirname "$0")"

echo "Installing packages..."
sudo apt-get update
sudo apt-get install -y cage wlr-randr python3-pygame

echo "Locking down the network..."
sudo systemctl disable --now ssh || true
sudo tee /etc/systemd/system/radios-off.service >/dev/null <<EOF
[Unit]
Description=Turn off Wi-Fi and Bluetooth at every boot
After=systemd-rfkill.service

[Service]
Type=oneshot
ExecStart=/usr/sbin/rfkill block wifi bluetooth

[Install]
WantedBy=multi-user.target
EOF

echo "Setting the clock to start on boot..."
sudo tee /etc/systemd/system/birdclock.service >/dev/null <<EOF
[Unit]
Description=Bird clock
After=systemd-user-sessions.service radios-off.service
Conflicts=getty@tty1.service

[Service]
User=$USER
WorkingDirectory=$PWD
PAMName=login
TTYPath=/dev/tty1
UtmpIdentifier=tty1
UtmpMode=user
StandardInput=tty-fail
Environment=XDG_SESSION_TYPE=wayland SDL_VIDEODRIVER=wayland
ExecStart=/usr/bin/cage -- /usr/bin/python3 -m birdclock
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable radios-off.service birdclock.service
echo "Done. Reboot to start the clock: sudo reboot"
