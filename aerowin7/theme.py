"""Theme management for the AeroTkinter demo project."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ThemePalette:
    """Collection of colors used by widgets and layout surfaces."""

    name: str
    background_start: str
    background_end: str
    card_color: str
    card_border: str
    text_primary: str
    text_muted: str
    accent: str
    accent_hover: str
    secondary: str
    secondary_hover: str
    entry_background: str
    entry_text: str
    shadow: str
    glow: str


LIGHT_THEME = ThemePalette(
    name="light",
    background_start="#cfe9ff",
    background_end="#8bbce6",
    card_color="#d9efff88",
    card_border="#ffffffa6",
    text_primary="#0f2f4a",
    text_muted="#325777",
    accent="#3d88cf",
    accent_hover="#58a0e5",
    secondary="#6d89a3",
    secondary_hover="#87a6c5",
    entry_background="#ffffff96",
    entry_text="#11324f",
    shadow="#17324a44",
    glow="#93d0ff",
)

DARK_THEME = ThemePalette(
    name="dark",
    background_start="#1b2a3b",
    background_end="#35526f",
    card_color="#25364a9a",
    card_border="#93c3ff66",
    text_primary="#eef6ff",
    text_muted="#c8dbef",
    accent="#5ca5eb",
    accent_hover="#77bdfd",
    secondary="#5b6f85",
    secondary_hover="#7289a3",
    entry_background="#2f445b99",
    entry_text="#f0f7ff",
    shadow="#00000088",
    glow="#7ec4ff",
)


THEMES: Dict[str, ThemePalette] = {
    LIGHT_THEME.name: LIGHT_THEME,
    DARK_THEME.name: DARK_THEME,
}


def get_theme(name: str) -> ThemePalette:
    """Return a theme by name, fallback to light for unknown names."""

    return THEMES.get((name or "").lower(), LIGHT_THEME)
