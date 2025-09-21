"""Learn scene that auto-plays educational content."""
from __future__ import annotations

import random
import math
from typing import List, Optional

import pygame

from ..core import scene, theme, ui
from ..data import data

MODULES = {
    "colors": {
        "title": "Colores",
        "items": data.COLORS,
    },
    "fruits": {
        "title": "Frutas",
        "items": data.FRUITS,
    },
    "shapes": {
        "title": "Formas",
        "items": data.SHAPES,
    },
    "alphabet": {
        "title": "Abecedario",
        "items": data.ALPHABET,
    },
    "numbers": {
        "title": "Números",
        "items": data.NUMBERS,
    },
}

PLAY_SCENE_FOR_MODULE = {
    "colors": "play_colors",
    "fruits": "play_fruits",
    "shapes": "play_shapes",
    "alphabet": "play_alphabet",
    "numbers": "play_numbers",
}


class LearnScene(scene.Scene):
    def __init__(self, manager: scene.SceneManager) -> None:
        super().__init__(manager)
        self.background = ui.AnimatedBackground((1920, 1080))
        self.buttons = {
            "home": ui.Button(pygame.Rect(120, 900, 320, 120), "Inicio", self.go_home),
            "repeat": ui.Button(pygame.Rect(520, 900, 320, 120), "Repetir", self.repeat_item),
            "next": ui.Button(pygame.Rect(920, 900, 320, 120), "Siguiente", self.next_item),
            "toggle": ui.Button(pygame.Rect(1320, 900, 420, 120), "Cambiar a Juego", self.toggle_mode),
        }
        self.progress_bar = ui.ProgressBar(pygame.Rect(360, 120, 1200, 40))
        self.module_order: List[str] = data.MODULE_ORDER[:]
        self.module_index = 0
        self.item_index = 0
        self.current_module = "colors"
        self.current_item = None
        self.auto_timer = 0.0
        self.auto_delay = 2.6
        self.scale_tween = ui.Tween(0.5, 1.0, 0.6, ui.ease_out_back)
        self.scale = 1.0
        self._fruit_bubbles = []

    def enter(self, start_module: Optional[str] = None, **kwargs) -> None:
        if start_module and start_module in self.module_order:
            self.module_index = self.module_order.index(start_module)
        else:
            self.module_index = 0
        self.item_index = 0
        self._load_module()
        self._present_item()

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def _load_module(self) -> None:
        self.current_module = self.module_order[self.module_index]
        self.items = list(MODULES[self.current_module]["items"])
        self.item_index = 0
        self.progress_bar.set_progress(0)

    def _present_item(self) -> None:
        items = MODULES[self.current_module]["items"]
        if self.item_index >= len(items):
            self.next_module()
            return
        self.current_item = items[self.item_index]
        self.auto_timer = 0.0
        if self.current_module == "fruits":
            self._fruit_bubbles = [
                (random.randint(80, 800), random.randint(80, 360), random.randint(20, 50))
                for _ in range(8)
            ]
        else:
            self._fruit_bubbles = []
        self.scale_tween.reset(0.6, 1.0)
        self.manager.context.audio.play("pop")
        self._speak_current()
        progress = (self.item_index + 1) / len(items)
        self.progress_bar.set_progress(progress)

    def _speak_current(self) -> None:
        item = self.current_item
        if item is None:
            return
        module = self.current_module
        if module == "colors":
            name = item["name"]
            text = f"Color {name}"
        elif module == "fruits":
            text = f"Esto es una {item}"
        elif module == "shapes":
            text = f"Forma {item}"
        elif module == "alphabet":
            text = f"Letra {item}"
        else:
            text = f"Número {item}"
        self.manager.context.audio.speak(text)

    def next_item(self) -> None:
        self.auto_timer = 0.0
        self.item_index += 1
        items = MODULES[self.current_module]["items"]
        if self.item_index >= len(items):
            self.next_module()
        else:
            self._present_item()

    def previous_item(self) -> None:
        if self.item_index > 0:
            self.item_index -= 1
            self._present_item()

    def next_module(self) -> None:
        self.module_index += 1
        if self.module_index >= len(self.module_order):
            self.manager.go_to("home")
            return
        self._load_module()
        self.auto_timer = 0.0
        self._present_item()

    def repeat_item(self) -> None:
        self.auto_timer = 0.0
        self.manager.context.audio.play("ding")
        self._speak_current()

    def go_home(self) -> None:
        self.manager.go_to("home")

    def toggle_mode(self) -> None:
        scene_name = PLAY_SCENE_FOR_MODULE.get(self.current_module, "play_colors")
        self.manager.go_to(scene_name)

    # ------------------------------------------------------------------
    # Pygame events
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                self.next_item()
            elif event.key == pygame.K_r:
                self.repeat_item()
            elif event.key == pygame.K_j:
                self.toggle_mode()
        for button in self.buttons.values():
            button.handle_event(event)

    def update(self, dt: float) -> None:
        self.background.update(dt)
        self.auto_timer += dt
        if self.auto_timer >= self.auto_delay:
            self.auto_timer = 0.0
            self.next_item()
        if self.scale_tween.active:
            self.scale = self.scale_tween.update(dt)
        for button in self.buttons.values():
            button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)
        module_title = MODULES[self.current_module]["title"]
        title_font = theme.get_font(theme.TITLE_SIZE)
        ui.draw_text(surface, module_title, title_font, theme.THEME.text_primary, (960, 180))
        self.progress_bar.draw(surface)
        if self.current_item is not None:
            self._draw_card(surface)
        for button in self.buttons.values():
            button.draw(surface)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _draw_card(self, surface: pygame.Surface) -> None:
        card_rect = pygame.Rect(0, 0, 880, 520)
        card_rect.center = (960, 560)
        scaled = card_rect.inflate(card_rect.width * (self.scale - 1), card_rect.height * (self.scale - 1))
        ui.draw_shadow(surface, scaled, theme.CARD_RADIUS)
        ui.draw_round_rect(surface, scaled, theme.THEME.card_background, theme.CARD_RADIUS)

        module = self.current_module
        if module == "colors":
            self._draw_color_item(surface, scaled)
        elif module == "fruits":
            self._draw_fruit_item(surface, scaled)
        elif module == "shapes":
            self._draw_shape_item(surface, scaled)
        elif module == "alphabet":
            self._draw_letter_item(surface, scaled)
        else:
            self._draw_number_item(surface, scaled)

    def _draw_color_item(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        item = self.current_item
        color = item["rgb"]
        name = item["name"].capitalize()
        circle_center = (rect.centerx, rect.centery - 40)
        pygame.draw.circle(surface, color, circle_center, 150)
        pygame.draw.circle(surface, (255, 255, 255, 100), circle_center, 155, width=6)
        self._draw_smiley(surface, circle_center, color)
        label_font = theme.get_font(theme.SUBTITLE_SIZE)
        ui.draw_text(surface, name, label_font, theme.THEME.text_primary, (rect.centerx, rect.bottom - 120))

    def _draw_smiley(self, surface: pygame.Surface, center: tuple, color: tuple) -> None:
        cx, cy = center
        pygame.draw.circle(surface, (255, 255, 255), (cx - 40, cy - 30), 18)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 40, cy - 30), 18)
        pygame.draw.circle(surface, (60, 60, 90), (cx - 40, cy - 30), 8)
        pygame.draw.circle(surface, (60, 60, 90), (cx + 40, cy - 30), 8)
        pygame.draw.arc(surface, (80, 60, 90), pygame.Rect(cx - 60, cy - 10, 120, 80), 0.2, 2.9, width=6)

    def _draw_fruit_item(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        name = str(self.current_item).capitalize()
        bubble_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        for x, y, radius in self._fruit_bubbles:
            pygame.draw.circle(bubble_surface, (255, 255, 255, 60), (x, y), radius)
        surface.blit(bubble_surface, rect.topleft)
        fruit_color = (255, 190, 160)
        fruit_rect = pygame.Rect(0, 0, 240, 260)
        fruit_rect.center = (rect.centerx, rect.centery - 40)
        pygame.draw.ellipse(surface, fruit_color, fruit_rect)
        pygame.draw.circle(surface, (255, 210, 180), (fruit_rect.centerx, fruit_rect.top + 60), 60)
        leaf = pygame.Rect(0, 0, 120, 60)
        leaf.center = (fruit_rect.centerx + 70, fruit_rect.top + 30)
        pygame.draw.ellipse(surface, (160, 220, 140), leaf)
        self._draw_smiley(surface, fruit_rect.center, fruit_color)
        label_font = theme.get_font(theme.SUBTITLE_SIZE)
        ui.draw_text(surface, name, label_font, theme.THEME.text_primary, (rect.centerx, rect.bottom - 110))

    def _draw_shape_item(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        name = str(self.current_item).capitalize()
        shape_rect = pygame.Rect(0, 0, 300, 300)
        shape_rect.center = (rect.centerx, rect.centery)
        draw_color = (180, 200, 255)
        name_font = theme.get_font(theme.SUBTITLE_SIZE)
        ui.draw_text(surface, name, name_font, theme.THEME.text_primary, (rect.centerx, rect.bottom - 100))
        kind = self.current_item
        _draw_shape(surface, shape_rect, draw_color, kind)

    def _draw_letter_item(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        letter = str(self.current_item)
        letter_font = theme.get_font(220)
        ui.draw_text(surface, letter, letter_font, theme.THEME.text_primary, rect.center)

    def _draw_number_item(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        number = str(self.current_item)
        number_font = theme.get_font(220)
        ui.draw_text(surface, number, number_font, theme.THEME.text_primary, rect.center)


def _draw_shape(surface: pygame.Surface, rect: pygame.Rect, color: tuple, name: str) -> None:
    center = rect.center
    if name == "círculo":
        pygame.draw.circle(surface, color, center, rect.width // 2)
    elif name == "cuadrado":
        pygame.draw.rect(surface, color, rect)
    elif name == "triángulo":
        points = [
            (center[0], rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
        ]
        pygame.draw.polygon(surface, color, points)
    elif name == "rectángulo":
        pygame.draw.rect(surface, color, rect.inflate(80, -80))
    elif name == "estrella":
        points = []
        for i in range(5):
            angle = i * (2 * 3.14159 / 5) - 3.14159 / 2
            outer = pygame.Vector2(math.cos(angle), math.sin(angle)) * (rect.width / 2)
            inner = pygame.Vector2(math.cos(angle + 3.14159 / 5), math.sin(angle + 3.14159 / 5)) * (rect.width / 4)
            points.append((center[0] + outer.x, center[1] + outer.y))
            points.append((center[0] + inner.x, center[1] + inner.y))
        pygame.draw.polygon(surface, color, points)
    elif name == "corazón":
        heart = pygame.Surface(rect.size, pygame.SRCALPHA)
        w, h = rect.size
        pygame.draw.circle(heart, color, (w * 0.3, h * 0.35), w * 0.25)
        pygame.draw.circle(heart, color, (w * 0.7, h * 0.35), w * 0.25)
        pygame.draw.polygon(heart, color, [(0, h * 0.35), (w, h * 0.35), (w / 2, h)])
        surface.blit(heart, rect.topleft)
    elif name == "óvalo":
        pygame.draw.ellipse(surface, color, rect)
    elif name == "rombo":
        points = [
            (center[0], rect.top),
            (rect.left, center[1]),
            (center[0], rect.bottom),
            (rect.right, center[1]),
        ]
        pygame.draw.polygon(surface, color, points)
    elif name == "pentágono":
        points = []
        for i in range(5):
            angle = i * (2 * 3.14159 / 5) - 3.14159 / 2
            vec = pygame.Vector2(math.cos(angle), math.sin(angle)) * (rect.width / 2)
            points.append((center[0] + vec.x, center[1] + vec.y))
        pygame.draw.polygon(surface, color, points)
    elif name == "hexágono":
        points = []
        for i in range(6):
            angle = i * (2 * 3.14159 / 6) - 3.14159 / 2
            vec = pygame.Vector2(math.cos(angle), math.sin(angle)) * (rect.width / 2)
            points.append((center[0] + vec.x, center[1] + vec.y))
        pygame.draw.polygon(surface, color, points)

