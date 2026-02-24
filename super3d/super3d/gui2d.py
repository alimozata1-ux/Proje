"""Super3D 2D GUI / pixel-shape yardımcı modülü."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame


@dataclass
class Rect2D:
    x: int
    y: int
    w: int
    h: int
    color: tuple[int, int, int] = (200, 200, 200)
    filled: bool = True
    thickness: int = 1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h), 0 if self.filled else self.thickness)


@dataclass
class Circle2D:
    x: int
    y: int
    r: int
    color: tuple[int, int, int] = (200, 200, 200)
    filled: bool = True
    thickness: int = 1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r, 0 if self.filled else self.thickness)


@dataclass
class Line2D:
    x1: int
    y1: int
    x2: int
    y2: int
    color: tuple[int, int, int] = (220, 220, 220)
    thickness: int = 1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.line(screen, self.color, (self.x1, self.y1), (self.x2, self.y2), self.thickness)


@dataclass
class PixelShape:
    pixels: list[str]
    pixel_size: int = 4
    on_color: tuple[int, int, int] = (255, 255, 255)
    off_color: tuple[int, int, int] | None = None

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        for py, row in enumerate(self.pixels):
            for px, ch in enumerate(row):
                if ch != "0":
                    pygame.draw.rect(
                        screen,
                        self.on_color,
                        (x + px * self.pixel_size, y + py * self.pixel_size, self.pixel_size, self.pixel_size),
                    )
                elif self.off_color is not None:
                    pygame.draw.rect(
                        screen,
                        self.off_color,
                        (x + px * self.pixel_size, y + py * self.pixel_size, self.pixel_size, self.pixel_size),
                    )


@dataclass
class Button:
    x: int
    y: int
    w: int
    h: int
    text: str
    on_click: Callable[[], None] | None = None
    bg: tuple[int, int, int] = (55, 90, 140)
    fg: tuple[int, int, int] = (245, 245, 245)
    hover_bg: tuple[int, int, int] = (75, 120, 180)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen: pygame.Surface) -> None:
        mouse = pygame.mouse.get_pos()
        color = self.hover_bg if self.rect().collidepoint(mouse) else self.bg
        pygame.draw.rect(screen, color, self.rect(), border_radius=7)
        pygame.draw.rect(screen, (230, 230, 230), self.rect(), 1, border_radius=7)
        font = pygame.font.SysFont("consolas", 18)
        txt = font.render(self.text, True, self.fg)
        screen.blit(txt, (self.x + 10, self.y + (self.h - txt.get_height()) // 2))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect().collidepoint(event.pos):
            if self.on_click:
                self.on_click()


@dataclass
class InputBox:
    x: int
    y: int
    w: int
    h: int
    text: str = ""
    active: bool = False
    max_len: int = 28

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen: pygame.Surface) -> None:
        border = (80, 210, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, (28, 32, 42), self.rect(), border_radius=6)
        pygame.draw.rect(screen, border, self.rect(), 1, border_radius=6)
        font = pygame.font.SysFont("consolas", 18)
        txt = font.render(self.text, True, (240, 240, 240))
        screen.blit(txt, (self.x + 8, self.y + (self.h - txt.get_height()) // 2))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect().collidepoint(event.pos)
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode and len(self.text) < self.max_len and event.unicode.isprintable():
                self.text += event.unicode


@dataclass
class Toggle:
    x: int
    y: int
    w: int
    h: int
    text: str
    value: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen: pygame.Surface) -> None:
        bg = (55, 145, 85) if self.value else (95, 70, 70)
        pygame.draw.rect(screen, bg, self.rect(), border_radius=7)
        pygame.draw.rect(screen, (230, 230, 230), self.rect(), 1, border_radius=7)
        font = pygame.font.SysFont("consolas", 16)
        txt = font.render(f"{self.text}: {'ON' if self.value else 'OFF'}", True, (245, 245, 245))
        screen.blit(txt, (self.x + 8, self.y + (self.h - txt.get_height()) // 2))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect().collidepoint(event.pos):
            self.value = not self.value


@dataclass
class Slider:
    x: int
    y: int
    w: int
    h: int
    min_value: float
    max_value: float
    value: float
    label: str = "Slider"
    dragging: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def ratio(self) -> float:
        span = max(1e-6, self.max_value - self.min_value)
        return max(0.0, min(1.0, (self.value - self.min_value) / span))

    def _set_from_mouse(self, mx: int) -> None:
        r = max(0.0, min(1.0, (mx - self.x) / max(1, self.w)))
        self.value = self.min_value + (self.max_value - self.min_value) * r

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (35, 35, 42), self.rect(), border_radius=5)
        fill_w = int(self.w * self.ratio())
        pygame.draw.rect(screen, (90, 190, 240), (self.x, self.y, fill_w, self.h), border_radius=5)
        pygame.draw.rect(screen, (230, 230, 230), self.rect(), 1, border_radius=5)
        font = pygame.font.SysFont("consolas", 16)
        txt = font.render(f"{self.label}: {self.value:.3f}", True, (240, 240, 240))
        screen.blit(txt, (self.x, self.y - 18))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect().collidepoint(event.pos):
            self.dragging = True
            self._set_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])


@dataclass
class GuiManager:
    buttons: list[Button] = field(default_factory=list)
    inputs: list[InputBox] = field(default_factory=list)
    shapes: list[object] = field(default_factory=list)
    toggles: list[Toggle] = field(default_factory=list)
    sliders: list[Slider] = field(default_factory=list)

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)
        for i in self.inputs:
            i.handle_event(event)
        for t in self.toggles:
            t.handle_event(event)
        for sl in self.sliders:
            sl.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        for s in self.shapes:
            if hasattr(s, "draw"):
                s.draw(screen)
        for b in self.buttons:
            b.draw(screen)
        for i in self.inputs:
            i.draw(screen)
        for t in self.toggles:
            t.draw(screen)
        for sl in self.sliders:
            sl.draw(screen)
