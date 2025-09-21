"""Reusable UI elements for Bubulandia TV."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import pygame

from . import theme

EaseFunction = Callable[[float], float]


# ---------------------------------------------------------------------------
# EASING UTILITIES
# ---------------------------------------------------------------------------

def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


class Tween:
    """Simple tween helper that interpolates between two values."""

    def __init__(
        self,
        start: float,
        end: float,
        duration: float,
        easing: EaseFunction = ease_out_cubic,
    ) -> None:
        self.start_value = start
        self.end_value = end
        self.duration = max(0.001, duration)
        self.easing = easing
        self.elapsed = 0.0
        self.active = False
        self.value = start

    def reset(self, start: Optional[float] = None, end: Optional[float] = None) -> None:
        if start is not None:
            self.start_value = start
        if end is not None:
            self.end_value = end
        self.elapsed = 0.0
        self.active = True
        self.value = self.start_value

    def update(self, dt: float) -> float:
        if not self.active:
            return self.value
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        eased = self.easing(progress)
        self.value = self.start_value + (self.end_value - self.start_value) * eased
        if progress >= 1.0:
            self.active = False
        return self.value

    def finish(self) -> None:
        self.value = self.end_value
        self.active = False


# ---------------------------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------------------------

def draw_round_rect(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], radius: int) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_shadow(surface: pygame.Surface, rect: pygame.Rect, radius: int, opacity: int = 80) -> None:
    shadow_rect = rect.copy()
    shadow_rect.move_ip(0, 12)
    shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (*theme.THEME.shadow, opacity), shadow_surface.get_rect(), border_radius=radius)
    surface.blit(shadow_surface, shadow_rect)


# ---------------------------------------------------------------------------
# BUTTONS
# ---------------------------------------------------------------------------


class Button:
    """Rounded button with hover and bounce animation."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None],
        *,
        font: Optional[pygame.font.Font] = None,
    ) -> None:
        self.base_rect = rect
        self.text = text
        self.callback = callback
        self.font = font or theme.get_font(theme.BUTTON_TEXT_SIZE)
        self.scale = 1.0
        self._bounce = Tween(0.92, 1.0, 0.35, ease_out_back)
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self.text_surface = self.font.render(self.text, True, theme.THEME.text_primary)

    @property
    def rect(self) -> pygame.Rect:
        scaled = pygame.Rect(0, 0, int(self.base_rect.width * self.scale), int(self.base_rect.height * self.scale))
        scaled.center = self.base_rect.center
        return scaled

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._bounce.reset(0.88, 1.0)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.callback()
            self.pressed = False

    def update(self, dt: float) -> None:
        if self._bounce.active:
            self.scale = self._bounce.update(dt)
        else:
            target = 1.04 if self.hovered else 1.0
            self.scale += (target - self.scale) * min(10 * dt, 1)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect
        color = theme.BUTTON_COLORS["default"]
        if self.pressed:
            color = theme.BUTTON_COLORS["active"]
        elif self.hovered:
            color = theme.BUTTON_COLORS["hover"]
        draw_shadow(surface, rect, theme.BUTTON_RADIUS)
        draw_round_rect(surface, rect, color, theme.BUTTON_RADIUS)

        text_rect = self.text_surface.get_rect(center=rect.center)
        surface.blit(self.text_surface, text_rect)


# ---------------------------------------------------------------------------
# PROGRESS BAR
# ---------------------------------------------------------------------------


class ProgressBar:
    """Rounded progress bar used in the learn scene."""

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.progress = 0.0

    def set_progress(self, value: float) -> None:
        self.progress = max(0.0, min(1.0, value))

    def draw(self, surface: pygame.Surface) -> None:
        draw_round_rect(surface, self.rect, (*theme.THEME.shadow, 60), theme.BUTTON_RADIUS)
        inner_rect = self.rect.inflate(-20, -20)
        draw_round_rect(surface, inner_rect, (255, 255, 255, 200), theme.BUTTON_RADIUS)
        if self.progress > 0:
            filled_width = int(inner_rect.width * self.progress)
            fill_rect = pygame.Rect(inner_rect.left, inner_rect.top, filled_width, inner_rect.height)
            draw_round_rect(surface, fill_rect, theme.THEME.accent, theme.BUTTON_RADIUS)


# ---------------------------------------------------------------------------
# BACKGROUND ELEMENTS
# ---------------------------------------------------------------------------


@dataclass
class FloatingShape:
    kind: str
    position: pygame.Vector2
    velocity: pygame.Vector2
    size: float
    opacity: int

    def update(self, dt: float, bounds: Tuple[int, int]) -> None:
        self.position += self.velocity * dt
        width, height = bounds
        if self.position.x > width + self.size:
            self.position.x = -self.size
        if self.position.x < -self.size:
            self.position.x = width + self.size
        if self.position.y > height + self.size:
            self.position.y = -self.size
        if self.position.y < -self.size:
            self.position.y = height + self.size

    def draw(self, surface: pygame.Surface) -> None:
        colour = pygame.Color(255, 255, 255, self.opacity)
        if self.kind == "circle":
            pygame.draw.circle(surface, colour, self.position, self.size)
        else:  # star
            points = []
            for i in range(5):
                angle = i * (math.pi * 2 / 5) - math.pi / 2
                outer = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.size
                inner = pygame.Vector2(math.cos(angle + math.pi / 5), math.sin(angle + math.pi / 5)) * (self.size * 0.5)
                points.append(self.position + outer)
                points.append(self.position + inner)
            pygame.draw.polygon(surface, colour, points)


class AnimatedBackground:
    """Animated gradient background with floating translucent shapes."""

    def __init__(self, size: Tuple[int, int]) -> None:
        self.size = size
        self.time = 0.0
        self.gradient_cache = pygame.Surface(size).convert()
        self.floaters: List[FloatingShape] = []
        width, height = size
        for _ in range(24):
            kind = random.choice(["circle", "star"])
            position = pygame.Vector2(random.uniform(0, width), random.uniform(0, height))
            velocity = pygame.Vector2(random.uniform(-20, 20), random.uniform(10, 30))
            size_value = random.uniform(20, 60)
            opacity = random.randint(40, 90)
            self.floaters.append(FloatingShape(kind, position, velocity, size_value, opacity))

    def update(self, dt: float) -> None:
        self.time += dt
        width, height = self.size
        for floater in self.floaters:
            floater.update(dt, self.size)

        colour_a = _lerp_colour(theme.THEME.background_a, theme.THEME.background_b, (math.sin(self.time * 0.2) + 1) / 2)
        colour_b = _lerp_colour(theme.THEME.background_b, theme.THEME.background_c, (math.cos(self.time * 0.15) + 1) / 2)

        gradient_height = 256
        temp = pygame.Surface((1, gradient_height)).convert()
        for y in range(gradient_height):
            ratio = y / (gradient_height - 1)
            colour = _lerp_colour(colour_a, colour_b, ratio)
            temp.set_at((0, y), colour)
        gradient = pygame.transform.smoothscale(temp, self.size)
        self.gradient_cache.blit(gradient, (0, 0))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.gradient_cache, (0, 0))
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        for floater in self.floaters:
            floater.draw(overlay)
        surface.blit(overlay, (0, 0))


def _lerp_colour(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------------------
# CONFETTI
# ---------------------------------------------------------------------------


@dataclass
class ConfettiParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    colour: pygame.Color
    life: float
    rotation: float
    spin: float

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.velocity.y += 30 * dt
        self.life -= dt
        self.rotation += self.spin * dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.life <= 0:
            return
        size = 14
        points = []
        for i in range(4):
            angle = self.rotation + i * (math.pi / 2)
            points.append((self.position.x + math.cos(angle) * size, self.position.y + math.sin(angle) * size))
        pygame.draw.polygon(surface, self.colour, points)


class ConfettiBurst:
    """Confetti burst triggered on success events."""

    def __init__(self) -> None:
        self.particles: List[ConfettiParticle] = []

    def trigger(self, position: Tuple[float, float]) -> None:
        cx, cy = position
        for _ in range(60):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 180)
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            colour = pygame.Color(random.randint(180, 255), random.randint(150, 255), random.randint(150, 255))
            spin = random.uniform(-4, 4)
            particle = ConfettiParticle(pygame.Vector2(cx, cy), velocity, colour, life=1.6, rotation=random.random(), spin=spin)
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(surface)


# ---------------------------------------------------------------------------
# STAR STICKERS
# ---------------------------------------------------------------------------


@dataclass
class StarSticker:
    position: Tuple[int, int]
    scale: float = 1.0
    glow: float = 0.0

    def update(self, dt: float) -> None:
        self.glow += dt * 3

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.position
        radius = 28 * self.scale
        colour = pygame.Color(*theme.THEME.star)
        for ring in range(3):
            alpha = max(0, 120 - ring * 40)
            glow_radius = radius + ring * 10 + math.sin(self.glow + ring) * 4
            pygame.draw.circle(surface, (*colour[:3], alpha), (x, y), int(glow_radius))
        points = []
        for i in range(5):
            angle = math.pi / 2 + i * (2 * math.pi / 5)
            outer = (x + math.cos(angle) * radius, y - math.sin(angle) * radius)
            inner_angle = angle + math.pi / 5
            inner = (x + math.cos(inner_angle) * radius * 0.5, y - math.sin(inner_angle) * radius * 0.5)
            points.append(outer)
            points.append(inner)
        pygame.draw.polygon(surface, colour, points)


# ---------------------------------------------------------------------------
# UTILITY LABEL
# ---------------------------------------------------------------------------


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, colour: Tuple[int, int, int], center: Tuple[int, int]) -> None:
    label = font.render(text, True, colour)
    surface.blit(label, label.get_rect(center=center))
