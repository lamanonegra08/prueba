"""Color matching mini-game with drag and drop."""
from __future__ import annotations

import random
from typing import List, Optional

import pygame

from ..core import scene, theme, ui
from ..data import data


PRIMARY_COLORS = ["rojo", "azul", "amarillo", "verde"]


class ColorBin:
    def __init__(self, name: str, color: tuple, rect: pygame.Rect) -> None:
        self.name = name
        self.color = color
        self.rect = rect
        self.label = theme.get_font(theme.BODY_SIZE).render(name.capitalize(), True, theme.THEME.text_primary)
        self.filled = False

    def draw(self, surface: pygame.Surface) -> None:
        inner = self.rect.inflate(-20, -20)
        ui.draw_shadow(surface, inner, 40)
        ui.draw_round_rect(surface, inner, self.color, 40)
        label_rect = self.label.get_rect(center=(inner.centerx, inner.bottom + 50))
        surface.blit(self.label, label_rect)


class ColorSticker:
    def __init__(self, name: str, color: tuple, start_pos: tuple) -> None:
        self.name = name
        self.color = color
        self.position = pygame.Vector2(start_pos)
        self.home = pygame.Vector2(start_pos)
        self.offset = pygame.Vector2()
        self.dragging = False
        self.placed = False
        self.scale = 1.0
        self.bounce = ui.Tween(0.8, 1.0, 0.4, ui.ease_out_back)
        self.move_target: Optional[pygame.Vector2] = None

    def rect(self) -> pygame.Rect:
        size = int(160 * self.scale)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = self.position
        return rect

    def start_drag(self, point: tuple) -> None:
        if self.placed:
            return
        self.dragging = True
        self.offset = self.position - pygame.Vector2(point)

    def drag(self, point: tuple) -> None:
        if not self.dragging:
            return
        self.position = pygame.Vector2(point) + self.offset

    def stop_drag(self) -> None:
        self.dragging = False

    def snap_to(self, point: tuple) -> None:
        self.move_target = pygame.Vector2(point)
        self.bounce.reset(0.85, 1.05)
        self.placed = True

    def return_home(self) -> None:
        self.move_target = self.home.copy()
        self.placed = False

    def update(self, dt: float) -> None:
        if self.move_target is not None:
            direction = self.move_target - self.position
            if direction.length() < 5:
                self.position = self.move_target
                self.move_target = None
            else:
                self.position += direction * min(dt * 6, 1)
        if self.bounce.active:
            self.scale = self.bounce.update(dt)
        else:
            self.scale += (1.0 - self.scale) * min(dt * 5, 1)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect()
        pygame.draw.circle(surface, self.color, rect.center, rect.width // 2)
        pygame.draw.circle(surface, (255, 255, 255), rect.center, rect.width // 2, width=6)
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx - 30, rect.centery - 20), 14)
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 30, rect.centery - 20), 14)
        pygame.draw.circle(surface, (50, 50, 80), (rect.centerx - 30, rect.centery - 20), 6)
        pygame.draw.circle(surface, (50, 50, 80), (rect.centerx + 30, rect.centery - 20), 6)
        pygame.draw.arc(surface, (80, 60, 90), pygame.Rect(rect.centerx - 50, rect.centery - 10, 100, 80), 0.2, 2.9, width=5)


class PlayColorsScene(scene.Scene):
    def __init__(self, manager: scene.SceneManager) -> None:
        super().__init__(manager)
        self.background = ui.AnimatedBackground((1920, 1080))
        self.buttons = {
            "home": ui.Button(pygame.Rect(120, 900, 320, 120), "Inicio", self.go_home),
            "repeat": ui.Button(pygame.Rect(520, 900, 320, 120), "Repetir", self.repeat_instructions),
            "next": ui.Button(pygame.Rect(920, 900, 320, 120), "Siguiente", self.go_next),
            "toggle": ui.Button(pygame.Rect(1320, 900, 420, 120), "Cambiar a Aprender", self.go_learn),
        }
        self.confetti = ui.ConfettiBurst()
        self.stars: List[ui.StarSticker] = []
        self.bins: List[ColorBin] = []
        self.stickers: List[ColorSticker] = []
        self.active_sticker: Optional[ColorSticker] = None
        self.completed = False
        self.active_sticker = None

    def enter(self, **kwargs) -> None:
        self._setup_bins()
        self._setup_stickers()
        self.stars.clear()
        self.confetti.particles.clear()
        self.completed = False
        self.repeat_instructions()

    def _setup_bins(self) -> None:
        palette = {item["name"]: item["rgb"] for item in data.COLORS}
        x_positions = [420, 760, 1100, 1440]
        self.bins = []
        for idx, name in enumerate(PRIMARY_COLORS):
            rect = pygame.Rect(0, 0, 240, 200)
            rect.center = (x_positions[idx], 730)
            colour = palette.get(name, (220, 220, 220))
            self.bins.append(ColorBin(name, colour, rect))

    def _setup_stickers(self) -> None:
        start_positions = [(380 + i * 360, 320 + (i % 2) * 160) for i in range(len(self.bins))]
        random.shuffle(start_positions)
        self.stickers = []
        for bin_slot, start in zip(self.bins, start_positions):
            sticker = ColorSticker(bin_slot.name, bin_slot.color, start)
            self.stickers.append(sticker)
        self.bins.sort(key=lambda b: b.rect.centerx)

    def repeat_instructions(self) -> None:
        self.manager.context.audio.speak("Arrastra los stickers al color correcto")

    def go_home(self) -> None:
        self.manager.go_to("home")

    def go_next(self) -> None:
        self.manager.go_to("play_fruits")

    def go_learn(self) -> None:
        self.manager.go_to("learn", start_module="colors")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                self.go_next()
            elif event.key == pygame.K_r:
                self.repeat_instructions()
            elif event.key == pygame.K_j:
                self.go_learn()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for sticker in reversed(self.stickers):
                if sticker.rect().collidepoint(event.pos) and not sticker.placed:
                    self.active_sticker = sticker
                    sticker.start_drag(event.pos)
                    break
        elif event.type == pygame.MOUSEMOTION and self.active_sticker:
            self.active_sticker.drag(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active_sticker:
                self._check_drop(self.active_sticker)
                self.active_sticker.stop_drag()
                self.active_sticker = None
        for button in self.buttons.values():
            button.handle_event(event)

    def _check_drop(self, sticker: ColorSticker) -> None:
        for bin_slot in self.bins:
            area = bin_slot.rect.inflate(160, 160)
            if area.collidepoint(sticker.position):
                if bin_slot.name == sticker.name:
                    sticker.snap_to(bin_slot.rect.center)
                    bin_slot.filled = True
                    self.manager.context.audio.play("ding")
                    self.manager.context.audio.speak(f"Color {sticker.name}")
                    self.confetti.trigger(bin_slot.rect.center)
                    self.stars.append(ui.StarSticker((bin_slot.rect.centerx, 180)))
                    self._check_completion()
                    return
        sticker.return_home()

    def _check_completion(self) -> None:
        if all(bin_slot.filled for bin_slot in self.bins) and not self.completed:
            self.completed = True
            self.manager.context.audio.speak("¡Muy bien!")
            self.manager.context.audio.play("ding")

    def update(self, dt: float) -> None:
        self.background.update(dt)
        self.confetti.update(dt)
        for sticker in self.stickers:
            sticker.update(dt)
        for star in self.stars:
            star.update(dt)
        for button in self.buttons.values():
            button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)
        title_font = theme.get_font(theme.TITLE_SIZE)
        ui.draw_text(surface, "Colores", title_font, theme.THEME.text_primary, (960, 140))
        subtitle_font = theme.get_font(theme.BODY_SIZE)
        ui.draw_text(surface, "Arrastra cada sticker a su color pastel", subtitle_font, theme.THEME.text_secondary, (960, 220))
        for bin_slot in self.bins:
            bin_slot.draw(surface)
        for sticker in self.stickers:
            sticker.draw(surface)
        for star in self.stars:
            star.draw(surface)
        if self.completed:
            banner_font = theme.get_font(theme.SUBTITLE_SIZE)
            ui.draw_text(surface, "¡Muy bien!", banner_font, theme.THEME.accent, (960, 320))
        self.confetti.draw(surface)
        for button in self.buttons.values():
            button.draw(surface)

