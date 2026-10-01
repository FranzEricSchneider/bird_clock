"""Bird clock app. Run from the repo root: python3 -m birdclock [--window] [--fast]"""

import argparse
import math
import random
import time
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

import pygame

from . import draw, hardware, schedule

REPO = Path(__file__).resolve().parent.parent


def load_config():
    cfg = tomllib.loads((REPO / "config.default.toml").read_text())
    user = REPO / "config.toml"
    if user.exists():
        cfg.update(tomllib.loads(user.read_text()))
    return cfg


class Chime:
    """One hourly bird: plays its sound a few times, shows its name, then fades out. Silent skips the sound."""

    def __init__(self, folder, cfg, t, size, silent):
        self.cfg = cfg
        self.image = pygame.transform.smoothscale(pygame.image.load(folder / "image.png").convert_alpha(), (size, size))
        name_file = folder / "name.txt"
        self.name = name_file.read_text().strip() if name_file.exists() else ""
        sounds = sorted((folder / "sounds").glob("*.ogg"))
        self.sound = None
        self.plays_left = 0
        if sounds and not silent and pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound(random.choice(sounds))
            self.sound.set_volume(cfg["volume"])
            self.plays_left = schedule.play_count(self.sound.get_length(), cfg, random)
        self.next_play = t
        self.sounds_done = None  # when the last play finished

    def update(self, t):
        """Advances the chime. Returns False once it is over."""
        if self.sounds_done is None:
            if self.sound and pygame.mixer.get_busy():
                self.next_play = t + self.cfg["pause"]
            elif self.plays_left == 0:
                self.sounds_done = t
            elif t >= self.next_play:
                self.sound.play()
                self.plays_left -= 1
            return True
        return t < self.sounds_done + self.cfg["name_seconds"] + self.cfg["fade_seconds"]

    def alpha(self, t):
        if self.sounds_done is None:
            return 255
        faded = (t - self.sounds_done - self.cfg["name_seconds"]) / max(self.cfg["fade_seconds"], 0.001)
        return int(255 * min(1, max(0, 1 - faded)))


def main():
    parser = argparse.ArgumentParser(description="Bird clock")
    parser.add_argument("--window", action="store_true", help="run in a window and leave screen power alone")
    parser.add_argument("--fast", action="store_true", help="run the clock 60x faster (an hour takes 1 minute)")
    args = parser.parse_args()
    cfg = load_config()
    assets = Path(cfg["assets"]).expanduser()

    start_real, start_clock = time.time(), datetime.now()

    def now():
        if args.fast:
            return start_clock + timedelta(seconds=(time.time() - start_real) * 60)
        return datetime.now()

    pygame.mixer.pre_init(44100)
    pygame.init()
    if args.window:
        screen = pygame.display.set_mode((800, 800))
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    pygame.display.set_caption("Bird clock")
    face = draw.make_face(min(screen.get_size()))
    bird_size = int(min(screen.get_size()) * draw.CLOCK_RADIUS * draw.BIRD_DIAMETER)
    font = pygame.font.Font(None, max(32, screen.get_height() // 14))
    frame_timer = pygame.time.Clock()

    chime = None
    chime_ended = -math.inf
    screen_on = None
    prev = now()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

        t = time.monotonic()
        current = now()
        input_present = hardware.input_present()
        if not chime and schedule.should_chime(prev, current, cfg, input_present):
            folder = assets / schedule.folder_for_hour(current.hour)
            try:
                chime = Chime(folder, cfg, t, bird_size, silent=schedule.is_quiet(current.hour, cfg))
            except (OSError, pygame.error) as e:
                print(f"Skipping {folder}: {e}", flush=True)
        prev = current
        if chime and not chime.update(t):
            chime, chime_ended = None, t

        upcoming = schedule.upcoming_chime_hour(current, cfg)
        waking = upcoming is not None and (assets / schedule.folder_for_hour(upcoming)).is_dir()
        want_on = bool(chime) or waking or t - chime_ended < cfg["sleep_after"] or input_present
        if want_on != screen_on:
            screen_on = want_on
            if not args.window:
                hardware.set_screen(screen_on, cfg)

        # When the screen is off, skip drawing. In a window, show black instead.
        if screen_on or args.window:
            screen.fill(draw.BLACK)
            if screen_on:
                draw.draw_clock(screen, face, current, cfg["second_hand"])
                if chime:
                    alpha = chime.alpha(t)
                    draw.draw_bird(screen, chime.image, alpha)
                    if chime.sounds_done is not None and chime.name:
                        name_y = screen.get_height() // 2 + chime.image.get_height() // 2 + font.get_height()
                        draw.draw_name(screen, font, chime.name, alpha, name_y)
            pygame.display.flip()
        frame_timer.tick(30 if chime else 5)


if __name__ == "__main__":
    main()
