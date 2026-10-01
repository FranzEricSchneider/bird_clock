#!/usr/bin/env python3
"""Builds or updates one hour's bird folder. Needs pygame and ffmpeg.

Example:
    python3 tools/add_bird.py --dest /media/usb/bird-assets --hour 7 \\
        --name "American Robin" --image robin.jpg --sound robin1.mp3 --sound robin2.wav
"""

import argparse
import re
import subprocess
from pathlib import Path

import pygame

WINDOW = 600
FRAME_RADIUS = 250
PEAK_DB = -1  # loudest moment of every sound, in dB below clipping


def crop_window(path):
    """Lets the user drag and zoom the picture under a circle frame.

    Returns (image, scale, offset) describing where the picture sat, or None if cancelled.
    """
    screen = pygame.display.set_mode((WINDOW, WINDOW))
    pygame.display.set_caption("Drag to move, scroll to zoom, Enter to save, Esc to cancel")
    image = pygame.image.load(path).convert()
    center = pygame.Vector2(WINDOW / 2)
    scale = 2 * FRAME_RADIUS / min(image.get_size())
    offset = center - pygame.Vector2(image.get_size()) * scale / 2  # picture's top-left corner
    dragging = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return image, scale, offset
            zoom = 1.0
            if event.type == pygame.MOUSEWHEEL:
                zoom = 1.1 ** event.y
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                zoom = 1.1
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                zoom = 1 / 1.1
            scale *= zoom
            offset = center - (center - offset) * zoom
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                offset += event.rel

        screen.fill((40, 40, 40))
        size = pygame.Vector2(image.get_size()) * scale
        screen.blit(pygame.transform.smoothscale(image, (int(size.x), int(size.y))), offset)
        shade = pygame.Surface((WINDOW, WINDOW), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        pygame.draw.circle(shade, (0, 0, 0, 0), center, FRAME_RADIUS)
        screen.blit(shade, (0, 0))
        pygame.draw.circle(screen, (255, 255, 255), center, FRAME_RADIUS, 2)
        pygame.display.flip()
        pygame.time.wait(15)


def render_circle(image, scale, offset, size):
    """The circle-cropped picture with a black ring and transparent corners, size x size."""
    big = size * 2  # draw at 2x, then shrink, to smooth the circle edges
    k = big / (2 * FRAME_RADIUS)  # window pixels -> output pixels
    frame_corner = pygame.Vector2(WINDOW / 2 - FRAME_RADIUS)
    out = pygame.Surface((big, big), pygame.SRCALPHA)
    out.fill((0, 0, 0, 255))
    picture = pygame.transform.smoothscale(image, [int(n * scale * k) for n in image.get_size()])
    out.blit(picture, (offset - frame_corner) * k)

    mask = pygame.Surface((big, big), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (big / 2, big / 2), big / 2)
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pygame.draw.circle(out, (0, 0, 0, 255), (big / 2, big / 2), big / 2, big // 32)
    return pygame.transform.smoothscale(out, (size, size))


def convert_sound(src, dest):
    """Converts to .ogg with its loudest moment at PEAK_DB, so every bird peaks at the same level."""
    measure = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    peak = float(re.search(r"max_volume: (\S+) dB", measure.stderr).group(1))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-af", f"volume={PEAK_DB - peak}dB", "-ar", "44100", "-c:a", "libvorbis", str(dest)],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Build or update one hour's bird folder.")
    parser.add_argument("--dest", required=True, type=Path, help="bird-assets folder")
    parser.add_argument("--hour", required=True, type=int, choices=range(1, 13))
    parser.add_argument("--name")
    parser.add_argument("--image", type=Path)
    parser.add_argument("--sound", type=Path, action="append", default=[], help="repeat for more sounds")
    parser.add_argument("--size", type=int, default=512, help="image width and height in pixels")
    args = parser.parse_args()

    folder = args.dest / f"{args.hour:02d}"
    (folder / "sounds").mkdir(parents=True, exist_ok=True)
    if args.name:
        (folder / "name.txt").write_text(args.name + "\n")
    if args.image:
        pygame.init()
        crop = crop_window(args.image)
        if crop is None:
            raise SystemExit("Cancelled; image not saved.")
        pygame.image.save(render_circle(*crop, args.size), folder / "image.png")
    for sound in args.sound:
        convert_sound(sound, folder / "sounds" / f"{sound.stem}.ogg")
    print(f"Updated {folder}")


if __name__ == "__main__":
    main()
