#!/usr/bin/env bash
# Replaces the Pi's bird files with a copy of the given folder.
# Usage: tools/install_assets.sh /media/usb/bird-assets
set -euo pipefail

src="${1:?Usage: tools/install_assets.sh <bird-assets folder>}"
dest="$HOME/bird-assets"
[ -d "$src" ] || { echo "Not a folder: $src" >&2; exit 1; }

rm -rf "$dest"
cp -r "$src" "$dest"
echo "Installed $src to $dest"
