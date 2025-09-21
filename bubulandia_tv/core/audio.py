"""Audio utilities including text-to-speech for Bubulandia TV."""
from __future__ import annotations

import math
import queue
import threading
from array import array
from typing import Dict, Optional

import pygame

try:  # pyttsx3 is optional during testing environments
    import pyttsx3
except Exception:  # pragma: no cover - fallback when dependency missing
    pyttsx3 = None  # type: ignore


class AudioManager:
    """Coordinates text-to-speech and playful sound effects."""

    def __init__(self) -> None:
        self._queue: "queue.Queue[Optional[str]]" = queue.Queue()
        self._stop_event = threading.Event()
        self._engine = None
        self._voice_ready = False
        self._thread: Optional[threading.Thread] = None
        if pyttsx3 is not None:
            try:
                self._engine = pyttsx3.init()
                self._configure_voice()
                self._thread = threading.Thread(target=self._speech_loop, daemon=True)
                self._thread.start()
            except Exception:
                self._engine = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._init_mixer()

    # ------------------------------------------------------------------
    # Speech
    # ------------------------------------------------------------------

    def _configure_voice(self) -> None:
        if self._engine is None:
            return
        try:
            voices = self._engine.getProperty("voices")
            chosen = None
            for voice in voices:
                name = getattr(voice, "name", "").lower()
                languages = ",".join(getattr(voice, "languages", [])).lower()
                if "spanish" in name or "es_" in languages or "spa" in languages:
                    chosen = voice.id
                    break
            if chosen:
                self._engine.setProperty("voice", chosen)
            self._engine.setProperty("rate", 158)
            self._voice_ready = True
        except Exception:
            self._voice_ready = False

    def speak(self, text: str) -> None:
        """Queue text for speech synthesis."""

        if self._engine is None:
            return
        self._queue.put(text)

    def stop(self) -> None:
        if self._engine is None:
            return
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._queue.put(None)
            self._thread.join(timeout=1.0)
        try:
            self._engine.stop()
        except Exception:
            pass

    def _speech_loop(self) -> None:
        if self._engine is None:
            return
        while not self._stop_event.is_set():
            try:
                text = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if text is None:
                break
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Sound effects
    # ------------------------------------------------------------------

    def _init_mixer(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sounds["ding"] = self._create_tone(990, 0.25, volume=0.4)
            self.sounds["pop"] = self._create_tone(620, 0.2, volume=0.35)
        except Exception:
            self.sounds = {}

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass

    def _create_tone(self, frequency: int, duration: float, *, volume: float = 0.5, sample_rate: int = 44100) -> pygame.mixer.Sound:
        count = int(duration * sample_rate)
        buffer = array("h")
        for i in range(count):
            angle = 2 * math.pi * frequency * (i / sample_rate)
            sample = int(volume * 32767 * math.sin(angle))
            buffer.append(sample)
        raw = buffer.tobytes()
        return pygame.mixer.Sound(buffer=raw)

