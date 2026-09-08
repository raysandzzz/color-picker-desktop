"""
Data persistence manager for projects and palettes saved in JSON.
"""

import json
import os
import uuid
from typing import Callable, Dict, List
from core.config import THEMES

DATA_FILE = os.path.join(os.path.dirname(__file__), "projects.json")


class ProjectManager:
    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.active_project_id = None

        self._listeners: List[Callable[[Dict[str, str]], None]] = []
        
        # Load existing data
        self.projects, self.theme_name, self.font_name = self._load_data()
        
        # If there are already previous projects, we select the most recent
        if self.projects:
            self.active_project_id = self.projects[0]["id"]

    def project_name_exists(self, name: str) -> bool:
        """Check if a project with the same name already exists."""
        normalized = name.strip().lower()
        return any(p["name"].strip().lower() == normalized for p in self.projects)
    
    def _load_data(self) -> tuple[list[dict], str, str]:
        """Loads the configured project list, theme and font from the JSON."""
        if not os.path.exists(self.filepath):
            return [], "light", "panton"
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            if isinstance(content, dict):
                return (
                    content.get("projects", []),
                    content.get("theme", "dark"),
                    content.get("font", "panton"),
                )

            # Compatibility
            if isinstance(content, list):
                return content, "dark", "panton"

        except (json.JSONDecodeError, IOError):
            return [], "dark", "panton"

        return [], "dark", "panton"

    def _save_data(self) -> None:
        """Saves the palettes(projects) and the current theme in the JSON."""
        data = {
            "projects": self.projects,
            "theme": self.theme_name,
            "font": self.font_name
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_theme_preference(self, theme_name: str) -> None:
        """Updates the current theme and persists it in the JSON."""
        self.theme_name = theme_name
        self._save_data()
    
    def save_font_preference(self, font_name: str) -> None:
        self.font_name = font_name
        self._save_data()
    
    def create_project(self, name: str, image_path: str) -> dict:
        """Create and register a new palette file with its associated image."""
        project = {
            "id": str(uuid.uuid4())[:8],
            "name": name.strip() or "Untitled Palette",
            "image_path": image_path,
            "palette": [],  # Ordered list of HEX strings
        }
        self.projects.insert(0, project)  # Most recent first
        self.active_project_id = project["id"]
        self._save_data()
        return project

    def get_all_projects(self) -> list[dict]:
        """Returns the complete list of saved projects."""
        return self.projects

    def get_active_project(self) -> dict | None:
        """Returns the dictionary of the current active project."""
        for p in self.projects:
            if p["id"] == self.active_project_id:
                return p
        return None

    def set_active_project(self, project_id: str):
        """Sets the active project based on its ID."""
        self.active_project_id = project_id

    def add_color_to_active(self, hex_color: str) -> bool:
        """
        Adds a color to the active project's palette.
        Avoid consecutive or repeated duplicates if it already exists.
        Returns True if it was added, False if it was already there.
        """
        project = self.get_active_project()
        if not project:
            return False

        hex_color = hex_color.upper()
        if hex_color not in project["palette"]:
            project["palette"].append(hex_color)
            self._save_data()
            return True
        return False

    def add_multiple_colors_to_active(self, hex_list: list[str]) -> int:
        """Adds a list of colors to the active project. Returns how many were added."""
        project = self.get_active_project()
        if not project:
            return 0

        added = 0
        for color in hex_list:
            c = color.upper()
            if c not in project["palette"]:
                project["palette"].append(c)
                added += 1

        if added > 0:
            self._save_data()
        return added

    def clear_active_palette(self):
        """Clears saved colors from the current project."""
        project = self.get_active_project()
        if project:
            project["palette"] = []
            self._save_data()

    def delete_project(self, project_id: str):
        """Delete a project from the registry."""
        self.projects = [p for p in self.projects if p["id"] != project_id]
        if self.active_project_id == project_id:
            self.active_project_id = self.projects[0]["id"] if self.projects else None
        self._save_data()
    
    def remove_color_from_active(self, hex_color: str) -> bool:
        """Removes a specific color from the active project palette."""
        project = self.get_active_project()
        if not project:
            return False

        hex_color = hex_color.upper()
        if hex_color in project["palette"]:
            project["palette"].remove(hex_color)
            self._save_data()
            return True
        return False