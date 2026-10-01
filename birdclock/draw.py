"""Draws the analog clock, bird image, and bird name."""

import math

import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CLOCK_RADIUS = 0.45  # fraction of the screen's shorter side
BIRD_DIAMETER = 1.1  # fraction of the clock radius, so the bird's edge (0.55) stops short of the hour hand's tip (0.65)


def make_face(size):
    """The clock face without hands. Drawn once, then reused every frame."""
    face = pygame.Surface((size, size), pygame.SRCALPHA)
    c = (size // 2, size // 2)
    r = int(size * CLOCK_RADIUS)
    pygame.draw.circle(face, WHITE, c, r, max(2, size // 150))
    for i in range(60):
        long_tick = i % 5 == 0
        inner = r * (0.85 if long_tick else 0.93)
        width = max(2, size // (120 if long_tick else 400))
        pygame.draw.line(face, WHITE, _point(c, inner, i * 6), _point(c, r * 0.97, i * 6), width)
    return face


def draw_clock(screen, face, now, second_hand):
    rect = face.get_rect(center=screen.get_rect().center)
    screen.blit(face, rect)
    c, r = rect.center, rect.width * CLOCK_RADIUS
    minutes = now.minute + now.second / 60
    hands = [((now.hour % 12 + minutes / 60) * 30, 0.65, 0.025), (minutes * 6, 0.9, 0.015)]
    if second_hand:
        hands.append((now.second * 6, 0.9, 0.005))
    for angle, length, width in hands:
        pygame.draw.line(screen, WHITE, c, _point(c, r * length, angle), max(2, int(rect.width * width)))
    pygame.draw.circle(screen, WHITE, c, max(4, int(rect.width * 0.02)))


def draw_bird(screen, image, alpha):
    image.set_alpha(alpha)
    screen.blit(image, image.get_rect(center=screen.get_rect().center))


def draw_name(screen, font, name, alpha, y):
    """Name centered at height y, with a black shadow so it reads on any background."""
    for offset, color in ((3, BLACK), (0, WHITE)):
        text = font.render(name, True, color)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(screen.get_width() // 2 + offset, y + offset))
        screen.blit(text, rect)


def _point(center, length, degrees):
    a = math.radians(degrees)
    return (center[0] + length * math.sin(a), center[1] - length * math.cos(a))
