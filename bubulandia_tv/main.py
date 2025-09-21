"""Entry point for Bubulandia TV."""
from __future__ import annotations

import sys
from pathlib import Path

import pygame

from core import audio
from core.scene import GameContext, SceneManager
from scenes.home import HomeScene
from scenes.learn import LearnScene
from scenes.play_colors import PlayColorsScene
from scenes.play_fruits import PlayFruitsScene
from scenes.play_shapes import PlayShapesScene
from scenes.play_alphabet import PlayAlphabetScene
from scenes.play_numbers import PlayNumbersScene



def create_screen() -> pygame.Surface:
    pygame.display.set_caption("Bubulandia TV")
    flags = pygame.FULLSCREEN | pygame.SCALED
    try:
        screen = pygame.display.set_mode((1920, 1080), flags)
    except pygame.error:
        screen = pygame.display.set_mode((1920, 1080))
    return screen


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = create_screen()
    clock = pygame.time.Clock()
    audio_manager = audio.AudioManager()
    context = GameContext(screen=screen, audio=audio_manager)
    manager = SceneManager(context)

    manager.register("home", HomeScene(manager))
    manager.register("learn", LearnScene(manager))
    manager.register("play_colors", PlayColorsScene(manager))
    manager.register("play_fruits", PlayFruitsScene(manager))
    manager.register("play_shapes", PlayShapesScene(manager))
    manager.register("play_alphabet", PlayAlphabetScene(manager))
    manager.register("play_numbers", PlayNumbersScene(manager))

    manager.go_to("home")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)
        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    audio_manager.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
