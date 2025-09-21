"""Centralised theme definitions for Bubulandia TV."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame

PastelColor = Tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    """Container for shared colour and size definitions."""

    background_a: PastelColor
    background_b: PastelColor
    background_c: PastelColor
    text_primary: PastelColor
    text_secondary: PastelColor
    card_background: PastelColor
    shadow: PastelColor
    accent: PastelColor
    star: PastelColor


THEME = Theme(
    background_a=(255, 214, 234),
    background_b=(210, 235, 255),
    background_c=(210, 255, 230),
    text_primary=(60, 60, 80),
    text_secondary=(90, 90, 120),
    card_background=(255, 255, 255),
    shadow=(180, 190, 220),
    accent=(255, 170, 200),
    star=(255, 215, 120),
)

LOGO_GRADIENT = [
    (255, 180, 200),
    (220, 170, 255),
    (170, 200, 255),
    (170, 235, 210),
    (250, 245, 180),
]

BUTTON_COLORS = {
    "default": (240, 230, 255),
    "hover": (250, 240, 255),
    "active": (230, 210, 250),
}

CARD_RADIUS = 36
BUTTON_RADIUS = 42
BUTTON_HEIGHT = 120
BUTTON_WIDTH = 360
BUTTON_TEXT_SIZE = 48
TITLE_SIZE = 88
SUBTITLE_SIZE = 56
BODY_SIZE = 42
SMALL_SIZE = 28


def get_font(size: int, bold: bool = True) -> pygame.font.Font:
    """Return a pastel friendly font. Fallback to default if missing."""

    if not pygame.font.get_init():
        pygame.font.init()

    preferred = ["Segoe UI", "Arial", "Poppins", "Quicksand"]
    for name in preferred:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                return font
        except Exception:  # pragma: no cover - defensive, pygame handles fonts
            continue
    return pygame.font.SysFont(pygame.font.get_default_font(), size, bold=bold)


def create_vertical_gradient(height: int, colors: Tuple[PastelColor, PastelColor]) -> pygame.Surface:
    """Create a vertical gradient surface for caching backgrounds."""

    width = 1
    surface = pygame.Surface((width, height)).convert_alpha()
    top, bottom = colors
    for y in range(height):
        ratio = y / max(height - 1, 1)
        colour = [int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3)]
        surface.set_at((0, y), (*colour, 255))
    return pygame.transform.smoothscale(surface, (1920, height))


def softened(colour: PastelColor, amount: float = 0.85) -> PastelColor:
    """Return a softly mixed version of the provided colour."""

    base = pygame.Color(*colour)
    mix = pygame.Color(255, 255, 255)
    result = base.lerp(mix, 1 - amount)
    return result.r, result.g, result.b
