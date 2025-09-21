"""Fruit memory matching mini-game."""
from __future__ import annotations

import math
import random
from typing import List, Optional

import pygame

from ..core import scene, theme, ui
from ..data import data


class MemoryCard:
    def __init__(self, fruit: str, rect: pygame.Rect) -> None:
        self.fruit = fruit
        self.rect = rect
        self.flip = 0.0
        self.flip_tween: Optional[ui.Tween] = None
        self.face_target = 0.0
        self.matched = False
        self.front_surface = self._create_front_surface()
        self.back_surface = self._create_back_surface()

    def _create_front_surface(self) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        ui.draw_round_rect(surface, surface.get_rect(), (255, 245, 220), 36)
        face_rect = pygame.Rect(0, 0, self.rect.width - 60, self.rect.height - 120)
        face_rect.center = (self.rect.width // 2, self.rect.height // 2 - 30)
        colour = (255, 180, 190)
        pygame.draw.ellipse(surface, colour, face_rect)
        pygame.draw.circle(surface, (255, 200, 210), (face_rect.centerx, face_rect.top + 40), 50)
        pygame.draw.circle(surface, (255, 255, 255), (face_rect.centerx - 30, face_rect.centery - 20), 16)
        pygame.draw.circle(surface, (255, 255, 255), (face_rect.centerx + 30, face_rect.centery - 20), 16)
        pygame.draw.circle(surface, (70, 70, 90), (face_rect.centerx - 30, face_rect.centery - 20), 7)
        pygame.draw.circle(surface, (70, 70, 90), (face_rect.centerx + 30, face_rect.centery - 20), 7)
        pygame.draw.arc(surface, (90, 70, 90), pygame.Rect(face_rect.centerx - 50, face_rect.centery - 5, 100, 70), 0.2, 2.9, width=6)
        leaf = pygame.Rect(0, 0, 120, 60)
        leaf.center = (face_rect.centerx + 80, face_rect.top + 10)
        pygame.draw.ellipse(surface, (180, 230, 180), leaf)
        label_font = theme.get_font(theme.BODY_SIZE)
        label = label_font.render(self.fruit.capitalize(), True, theme.THEME.text_primary)
        surface.blit(label, label.get_rect(center=(self.rect.width // 2, self.rect.height - 70)))
        return surface

    def _create_back_surface(self) -> pygame.Surface:
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        ui.draw_round_rect(surface, surface.get_rect(), (220, 220, 255), 36)
        question_font = theme.get_font(96)
        ui.draw_text(surface, "?", question_font, (255, 255, 255), (self.rect.width // 2, self.rect.height // 2))
        return surface

    def contains(self, point: tuple) -> bool:
        return self.rect.collidepoint(point)

    def reveal(self) -> None:
        self.face_target = 1.0
        self.flip_tween = ui.Tween(self.flip, 1.0, 0.35, ui.ease_in_out_quad)
        self.flip_tween.reset(self.flip, 1.0)

    def hide(self) -> None:
        self.face_target = 0.0
        self.flip_tween = ui.Tween(self.flip, 0.0, 0.35, ui.ease_in_out_quad)
        self.flip_tween.reset(self.flip, 0.0)

    def update(self, dt: float) -> None:
        if self.flip_tween:
            self.flip = self.flip_tween.update(dt)
            if not self.flip_tween.active:
                self.flip_tween = None
        else:
            self.flip += (self.face_target - self.flip) * min(dt * 5, 1)

    @property
    def face_up(self) -> bool:
        return self.flip >= 0.95

    def draw(self, surface: pygame.Surface) -> None:
        angle = self.flip * math.pi
        scale = max(0.05, abs(math.cos(angle)))
        base = self.front_surface if self.flip >= 0.5 else self.back_surface
        scaled_width = max(10, int(self.rect.width * scale))
        scaled = pygame.transform.smoothscale(base, (scaled_width, self.rect.height))
        draw_rect = scaled.get_rect(center=self.rect.center)
        surface.blit(scaled, draw_rect)


class PlayFruitsScene(scene.Scene):
    def __init__(self, manager: scene.SceneManager) -> None:
        super().__init__(manager)
        self.background = ui.AnimatedBackground((1920, 1080))
        self.buttons = {
            "home": ui.Button(pygame.Rect(120, 900, 320, 120), "Inicio", self.go_home),
            "repeat": ui.Button(pygame.Rect(520, 900, 320, 120), "Repetir", self.repeat_instructions),
            "next": ui.Button(pygame.Rect(920, 900, 320, 120), "Siguiente", self.go_next),
            "toggle": ui.Button(pygame.Rect(1320, 900, 420, 120), "Cambiar a Aprender", self.go_learn),
        }
        self.cards: List[MemoryCard] = []
        self.selected: List[MemoryCard] = []
        self.reveal_delay = 0.0
        self.attempts = 0
        self.confetti = ui.ConfettiBurst()
        self.stars: List[ui.StarSticker] = []
        self.completed = False

    def enter(self, **kwargs) -> None:
        self._create_cards()
        self.selected.clear()
        self.reveal_delay = 0.0
        self.attempts = 0
        self.stars.clear()
        self.confetti.particles.clear()
        self.completed = False
        self.repeat_instructions()

    def _create_cards(self) -> None:
        fruits = random.sample(data.FRUITS, 4)
        deck = fruits * 2
        random.shuffle(deck)
        self.cards = []
        positions = []
        start_x, start_y = 500, 320
        spacing_x, spacing_y = 260, 260
        for row in range(2):
            for col in range(4):
                rect = pygame.Rect(0, 0, 200, 260)
                rect.center = (start_x + col * spacing_x, start_y + row * spacing_y)
                positions.append(rect)
        for fruit, rect in zip(deck, positions):
            self.cards.append(MemoryCard(fruit, rect))

    def repeat_instructions(self) -> None:
        self.manager.context.audio.speak("Encuentra las parejas de frutas")

    def go_home(self) -> None:
        self.manager.go_to("home")

    def go_next(self) -> None:
        self.manager.go_to("play_shapes")

    def go_learn(self) -> None:
        self.manager.go_to("learn", start_module="fruits")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                if self.completed:
                    self.go_next()
            elif event.key == pygame.K_r:
                self.repeat_instructions()
            elif event.key == pygame.K_j:
                self.go_learn()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        for button in self.buttons.values():
            button.handle_event(event)

    def _handle_click(self, pos: tuple) -> None:
        if self.reveal_delay > 0:
            return
        for card in self.cards:
            if card.matched or card in self.selected:
                continue
            if card.contains(pos):
                card.reveal()
                self.selected.append(card)
                if len(self.selected) == 2:
                    self.reveal_delay = 0.8
                    self.attempts += 1
                break

    def update(self, dt: float) -> None:
        self.background.update(dt)
        self.confetti.update(dt)
        if self.reveal_delay > 0:
            self.reveal_delay -= dt
            if self.reveal_delay <= 0:
                self._evaluate_selection()
        for card in self.cards:
            card.update(dt)
        for star in self.stars:
            star.update(dt)
        for button in self.buttons.values():
            button.update(dt)

    def _evaluate_selection(self) -> None:
        if len(self.selected) != 2:
            return
        first, second = self.selected
        if first.fruit == second.fruit:
            first.matched = second.matched = True
            first.reveal()
            second.reveal()
            self.manager.context.audio.play("ding")
            self.manager.context.audio.speak(f"Esto es una {first.fruit}")
            center = ((first.rect.centerx + second.rect.centerx) // 2, 200)
            self.stars.append(ui.StarSticker(center))
            self.confetti.trigger(center)
            self._check_completion()
        else:
            first.hide()
            second.hide()
        self.selected.clear()

    def _check_completion(self) -> None:
        if all(card.matched for card in self.cards) and not self.completed:
            self.completed = True
            self.manager.context.audio.speak("¡Muy bien!")
            self.manager.context.audio.play("ding")

    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)
        title_font = theme.get_font(theme.TITLE_SIZE)
        ui.draw_text(surface, "Memoria de Frutas", title_font, theme.THEME.text_primary, (960, 140))
        subtitle_font = theme.get_font(theme.BODY_SIZE)
        ui.draw_text(surface, "Haz clic para destapar y encontrar las parejas", subtitle_font, theme.THEME.text_secondary, (960, 220))
        attempts_font = theme.get_font(theme.SMALL_SIZE)
        ui.draw_text(surface, f"Intentos: {self.attempts}", attempts_font, theme.THEME.text_secondary, (960, 260))
        for card in self.cards:
            card.draw(surface)
        for star in self.stars:
            star.draw(surface)
        if self.completed:
            banner_font = theme.get_font(theme.SUBTITLE_SIZE)
            ui.draw_text(surface, "¡Bravo!", banner_font, theme.THEME.accent, (960, 300))
        self.confetti.draw(surface)
        for button in self.buttons.values():
            button.draw(surface)

