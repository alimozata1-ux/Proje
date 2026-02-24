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
class GuiManager:
    buttons: list[Button] = field(default_factory=list)
    inputs: list[InputBox] = field(default_factory=list)
    shapes: list[object] = field(default_factory=list)

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)
        for i in self.inputs:
            i.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        for s in self.shapes:
            if hasattr(s, "draw"):
                s.draw(screen)
        for b in self.buttons:
            b.draw(screen)
        for i in self.inputs:
            i.draw(screen)
