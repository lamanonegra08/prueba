"""Home scene with animated logo and friendly bear."""
from __future__ import annotations

import math
from typing import Tuple

import pygame

from ..core import scene, theme, ui


class PastelBear:
    """Cute bear drawn with pygame primitives."""

    def __init__(self, center: Tuple[int, int]) -> None:
        self.center = pygame.Vector2(center)
        self.wave_time = 0.0
        self.blink_timer = 2.5
        self.blink_duration = 0.28
        self.blink_elapsed = 0.0
        self.blinking = False

    def update(self, dt: float) -> None:
        self.wave_time += dt
        if self.blinking:
            self.blink_elapsed += dt
            if self.blink_elapsed >= self.blink_duration:
                self.blinking = False
                self.blink_elapsed = 0.0
                self.blink_timer = 2.0 + 2.5 * math.sin(self.wave_time)
        else:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.blinking = True
                self.blink_elapsed = 0.0
                self.blink_duration = 0.25 + 0.1 * math.sin(self.wave_time * 0.5)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = self.center
        bear_color = (255, 220, 200)
        belly_color = (255, 235, 220)
        ear_inner = (255, 200, 210)
        outline = (245, 180, 165)

        body_rect = pygame.Rect(0, 0, 260, 310)
        body_rect.center = (cx, cy + 160)
        pygame.draw.ellipse(surface, bear_color, body_rect)
        belly_rect = body_rect.inflate(-80, -90)
        pygame.draw.ellipse(surface, belly_color, belly_rect)

        head_radius = 150
        head_center = (cx, cy - 40)
        pygame.draw.circle(surface, bear_color, head_center, head_radius)

        for dx in (-90, 90):
            ear_center = (head_center[0] + dx, head_center[1] - 120)
            pygame.draw.circle(surface, bear_color, ear_center, 60)
            pygame.draw.circle(surface, ear_inner, ear_center, 40)

        left_arm_rect = pygame.Rect(0, 0, 80, 180)
        left_arm_rect.center = (cx - 150, cy + 120)
        pygame.draw.ellipse(surface, bear_color, left_arm_rect)

        right_arm_rect = pygame.Rect(0, 0, 80, 180)
        right_arm_rect.center = (cx + 150, cy + 60)
        angle = math.sin(self.wave_time * 2.2) * 25
        arm_surface = pygame.Surface(right_arm_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(arm_surface, bear_color, arm_surface.get_rect())
        rotated = pygame.transform.rotozoom(arm_surface, -angle, 1.0)
        rect = rotated.get_rect(center=right_arm_rect.center)
        surface.blit(rotated, rect)

        paw_center = (rect.centerx + 20, rect.centery + 60)
        pygame.draw.circle(surface, belly_color, paw_center, 42)
        pygame.draw.circle(surface, outline, paw_center, 42, width=4)

        closeness = 0.0
        if self.blinking and self.blink_duration > 0:
            phase = min(self.blink_elapsed / self.blink_duration, 1.0)
            closeness = math.sin(phase * math.pi)

        for dx in (-60, 60):
            eye_center = (head_center[0] + dx, head_center[1] - 30)
            eye_height = max(6, 26 * (1 - closeness))
            eye_rect = pygame.Rect(0, 0, 28, int(eye_height))
            eye_rect.center = eye_center
            pygame.draw.ellipse(surface, (60, 60, 80), eye_rect)
            highlight = pygame.Rect(0, 0, 10, max(4, int(eye_height * 0.4)))
            highlight.center = (eye_center[0] - 4, eye_center[1] - 2)
            pygame.draw.ellipse(surface, (255, 255, 255, 180), highlight)

        nose_rect = pygame.Rect(0, 0, 54, 38)
        nose_rect.center = (head_center[0], head_center[1] + 10)
        pygame.draw.ellipse(surface, (120, 80, 90), nose_rect)
        mouth_color = (180, 120, 130)
        pygame.draw.arc(surface, mouth_color, pygame.Rect(head_center[0] - 40, head_center[1] + 20, 80, 60), math.pi * 0.1, math.pi - math.pi * 0.1, width=4)

        cheek_color = (255, 190, 200)
        for dx in (-70, 70):
            pygame.draw.circle(surface, cheek_color, (head_center[0] + dx, head_center[1] + 20), 30)


class HomeScene(scene.Scene):
    def __init__(self, manager: scene.SceneManager) -> None:
        super().__init__(manager)
        self.background = ui.AnimatedBackground((1920, 1080))
        self.logo_surface = self._create_logo_surface()
        self.logo_rect = self.logo_surface.get_rect(center=(960, 240))
        self.bear = PastelBear((960, 520))
        self.buttons = [
            ui.Button(pygame.Rect(0, 0, theme.BUTTON_WIDTH, theme.BUTTON_HEIGHT), "¡Comenzar a Jugar!", self.start_play),
            ui.Button(pygame.Rect(0, 0, theme.BUTTON_WIDTH, theme.BUTTON_HEIGHT), "Aprender", self.start_learn),
        ]
        self.buttons[0].base_rect.center = (960, 760)
        self.buttons[1].base_rect.center = (960, 910)

    def _create_logo_surface(self) -> pygame.Surface:
        font = theme.get_font(140)
        text = "Bubulandia TV"
        base = font.render(text, True, (255, 255, 255))
        gradient = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        width, height = base.get_size()
        colours = theme.LOGO_GRADIENT
        segments = len(colours) - 1
        for x in range(width):
            ratio = x / max(1, width - 1)
            pos = ratio * segments
            idx = min(int(pos), segments - 1)
            frac = pos - idx
            c1 = colours[idx]
            c2 = colours[min(idx + 1, segments)]
            colour = [int(c1[i] + (c2[i] - c1[i]) * frac) for i in range(3)]
            pygame.draw.line(gradient, (*colour, 255), (x, 0), (x, height))
        gradient.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        glow_surface = pygame.Surface((base.get_width() + 40, base.get_height() + 40), pygame.SRCALPHA)
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx * dx + dy * dy <= 36:
                    glow_surface.blit(base, (dx + 20, dy + 20))
        glow_surface.blit(gradient, (20, 20))
        glow_surface = pygame.transform.smoothscale(glow_surface, glow_surface.get_size())
        return glow_surface

    def enter(self, **kwargs) -> None:
        self.manager.context.audio.play("ding")
        self.manager.context.audio.speak("¡Bienvenido a Bubulandia TV!")

    def start_play(self) -> None:
        self.manager.go_to("play_colors")

    def start_learn(self) -> None:
        self.manager.go_to("learn")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                self.start_play()
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        self.background.update(dt)
        self.bear.update(dt)
        for button in self.buttons:
            button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)
        surface.blit(self.logo_surface, self.logo_rect)
        self.bear.draw(surface)
        subtitle_font = theme.get_font(theme.SUBTITLE_SIZE)
        ui.draw_text(surface, "Aprende y juega con colores, frutas y más", subtitle_font, theme.THEME.text_secondary, (960, 420))
        for button in self.buttons:
            button.draw(surface)
