"""TODO: Implement number balloon popping mini-game."""
from __future__ import annotations

import pygame

from ..core import scene, theme, ui


class PlayNumbersScene(scene.Scene):
    """Placeholder scene teasing the numbers activity."""

    def __init__(self, manager: scene.SceneManager) -> None:
        super().__init__(manager)
        self.background = ui.AnimatedBackground((1920, 1080))
        self.buttons = {
            "home": ui.Button(pygame.Rect(120, 900, 320, 120), "Inicio", self.go_home),
            "repeat": ui.Button(pygame.Rect(520, 900, 320, 120), "Repetir", self.repeat_message),
            "next": ui.Button(pygame.Rect(920, 900, 320, 120), "Finalizar", self.go_home),
            "toggle": ui.Button(pygame.Rect(1320, 900, 420, 120), "Cambiar a Aprender", self.go_learn),
        }
        self.message = "¡Muy pronto reventaremos globos de números!"

    def enter(self, **kwargs) -> None:
        self.repeat_message()

    def go_home(self) -> None:
        self.manager.go_to("home")

    def go_learn(self) -> None:
        self.manager.go_to("learn", start_module="numbers")

    def repeat_message(self) -> None:
        self.manager.context.audio.speak("El juego de números estará disponible muy pronto")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                self.go_home()
            elif event.key == pygame.K_r:
                self.repeat_message()
            elif event.key == pygame.K_j:
                self.go_learn()
        for button in self.buttons.values():
            button.handle_event(event)

    def update(self, dt: float) -> None:
        self.background.update(dt)
        for button in self.buttons.values():
            button.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.background.draw(surface)
        title_font = theme.get_font(theme.TITLE_SIZE)
        ui.draw_text(surface, "Números - Próximamente", title_font, theme.THEME.text_primary, (960, 200))
        message_font = theme.get_font(theme.SUBTITLE_SIZE)
        ui.draw_text(surface, self.message, message_font, theme.THEME.text_secondary, (960, 360))
        hint_font = theme.get_font(theme.BODY_SIZE)
        ui.draw_text(surface, "Repasa los números en modo aprender", hint_font, theme.THEME.text_secondary, (960, 440))
        for button in self.buttons.values():
            button.draw(surface)

