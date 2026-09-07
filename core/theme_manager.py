"""Theme manager module for dynamic light/dark mode toggling."""

from typing import Callable, Dict, List
from core.config import THEMES


class ThemeManager:
    """Manages active theme state and notifies registered UI components on change."""

    def __init__(self, initial_theme: str = "light"):
        self.current_theme_name: str = initial_theme if initial_theme in THEMES else "light"
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
        self.current_theme_name = "dark" if self.current_theme_name == "light" else "light"
        active_colors = self.colors

        # Update colors
        for listener in list(self._listeners):
            listener(active_colors)

        return active_colors