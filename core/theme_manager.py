"""Theme manager module for dynamic light/dark mode toggling."""

from typing import Callable, Dict, List, Optional
from core.config import THEMES, FONT_PRESETS


class ThemeManager:
    """Manages active theme state and notifies registered UI components on change."""
    
    def __init__(self, 
                initial_theme: str = "light", 
                initial_font: str = "panton",
                on_theme_change: Optional[Callable[[str], None]] = None
                ):
        
        self.current_theme_name: str = initial_theme if initial_theme in THEMES else "light"
        self.current_font_name = initial_font
        self.current_font_name = (
            initial_font if initial_font in FONT_PRESETS else "panton"
        )
        self.on_theme_change = on_theme_change
        self._listeners: List[Callable[[Dict[str, str]], None]] = []

    @property
    def colors(self) -> Dict[str, str]:
        """Returns the dictionary of color tokens for the current theme."""
        return THEMES[self.current_theme_name]

    @property
    def is_dark(self) -> bool:
        """Returns True if the current theme is dark."""
        return self.current_theme_name == "light"

    def register_listener(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Subscribes a component's update callback to theme changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Removes a component's update callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def toggle_theme(self) -> Dict[str, str]:
        """Switches between dark and light, notifying all active UI listeners."""
        self.current_theme_name = "light" if self.current_theme_name == "dark" else "dark"
        active_colors = self.colors

        if self.on_theme_change:
            self.on_theme_change(self.current_theme_name)

        active_colors = self.colors
        for listener in list(self._listeners):
            listener(active_colors)

        return active_colors
    
    @property
    def fonts(self):
        """Retorna el set de fuentes activo ('title', 'normal', etc.)."""
        return FONT_PRESETS.get(self.current_font_name, FONT_PRESETS["panton"])

    def toggle_font(self):
        """Alterna entre la tipografía estándar y la pixel/retro."""
        self.current_font_name = "pixel" if self.current_font_name == "panton" else "panton"
        return self.fonts