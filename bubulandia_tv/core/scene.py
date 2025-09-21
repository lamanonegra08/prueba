"""Scene management utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pygame

from .audio import AudioManager


class Scene:
    """Base class for all game scenes."""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    def enter(self, **kwargs) -> None:  # pragma: no cover - interface hook
        pass

    def exit(self) -> None:  # pragma: no cover - interface hook
        pass

    def handle_event(self, event: pygame.event.Event) -> None:  # pragma: no cover
        pass

    def update(self, dt: float) -> None:  # pragma: no cover
        pass

    def draw(self, surface: pygame.Surface) -> None:  # pragma: no cover
        pass


@dataclass
class GameContext:
    screen: pygame.Surface
    audio: AudioManager


class SceneManager:
    """Router responsible for switching between scenes."""

    def __init__(self, context: GameContext) -> None:
        self.context = context
        self.scenes: Dict[str, Scene] = {}
        self.current: Optional[Scene] = None
        self.current_name: Optional[str] = None

    def register(self, name: str, scene: Scene) -> None:
        self.scenes[name] = scene

    def go_to(self, name: str, **kwargs) -> None:
        if name not in self.scenes:
            raise KeyError(f"Scene '{name}' is not registered")
        if self.current:
            self.current.exit()
        self.current = self.scenes[name]
        self.current_name = name
        self.current.enter(**kwargs)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.current:
            self.current.draw(surface)
