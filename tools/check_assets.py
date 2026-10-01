#!/usr/bin/env python3
"""Checks a bird-assets folder and lists any problems. Needs pygame.

Usage: python3 tools/check_assets.py <bird-assets folder>
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")  # load sounds without a speaker
import pygame  # noqa: E402


def check_hour(folder):
    problems = []
    try:
        image = pygame.image.load(folder / "image.png")
        if image.get_width() != image.get_height():
            problems.append("image.png is not square")
        elif image.get_at((0, 0)).a != 0:
            problems.append("image.png corners are not transparent")
    except (OSError, pygame.error) as e:
        problems.append(f"image.png: {e}")
    name = folder / "name.txt"
    if not name.exists() or not name.read_text().strip():
        problems.append("name.txt is missing or empty")
    sounds = sorted((folder / "sounds").glob("*.ogg"))
    if not sounds:
        problems.append("no sounds/*.ogg")
    for sound in sounds:
        try:
            pygame.mixer.Sound(sound)
        except pygame.error as e:
            problems.append(f"{sound.name}: {e}")
    return problems


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    root = Path(sys.argv[1])
    pygame.mixer.init()
    ok = True
    for hour in range(1, 13):
        folder = root / f"{hour:02d}"
        if not folder.is_dir():
            print(f"{hour:02d}: missing (this hour will be skipped)")
            continue
        problems = check_hour(folder)
        ok = ok and not problems
        print(f"{hour:02d}: " + ("; ".join(problems) if problems else "ok"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
