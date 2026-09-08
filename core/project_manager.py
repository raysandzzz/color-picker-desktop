"""
Gestor de persistencia de datos para proyectos y paletas guardadas en JSON.
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
        
        # Cargar datos existentes
        self.projects, self.theme_name, self.font_name = self._load_data()
        
        # Si ya existen proyectos previos, seleccionamos el más reciente
        if self.projects:
            self.active_project_id = self.projects[0]["id"]

    def project_name_exists(self, name: str) -> bool:
        """Verifica si ya existe un proyecto con el mismo nombre."""
        normalized = name.strip().lower()
        return any(p["name"].strip().lower() == normalized for p in self.projects)
    
    def _load_data(self) -> tuple[list[dict], str, str]:
        """Carga la lista de proyectos, el tema y la fuente configurados desde el JSON."""
        if not os.path.exists(self.filepath):
            return [], "light", "segoe"
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            if isinstance(content, dict):
                return (
                    content.get("projects", []),
                    content.get("theme", "dark"),
                    content.get("font", "segoe"),
                )

            # Compatibilidad
            if isinstance(content, list):
                return content, "dark", "segoe"

        except (json.JSONDecodeError, IOError):
            return [], "dark", "segoe"

        return [], "dark", "segoe"

    def _save_data(self) -> None:
        """Guarda los proyectos y el tema actual en el JSON."""
        data = {
            "projects": self.projects,
            "theme": self.theme_name,
            "font": self.font_name
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_theme_preference(self, theme_name: str) -> None:
        """Actualiza el tema actual y lo persiste en el JSON."""
        self.theme_name = theme_name
        self._save_data()
    
    def save_font_preference(self, font_name: str) -> None:
        self.font_name = font_name
        self._save_data()
    
    def create_project(self, name: str, image_path: str) -> dict:
        """Crea y registra una nuevo archivo de paleta con su imagen asociada."""
        project = {
            "id": str(uuid.uuid4())[:8],
            "name": name.strip() or "Untitled Palette",
            "image_path": image_path,
            "palette": [],  # Lista ordenada de strings HEX
        }
        self.projects.insert(0, project)  # El más reciente primero
        self.active_project_id = project["id"]
        self._save_data()
        return project

    def get_all_projects(self) -> list[dict]:
        """Devuelve la lista completa de proyectos guardados."""
        return self.projects

    def get_active_project(self) -> dict | None:
        """Devuelve el diccionario del proyecto activo actual."""
        for p in self.projects:
            if p["id"] == self.active_project_id:
                return p
        return None

    def set_active_project(self, project_id: str):
        """Establece el proyecto activo según su ID."""
        self.active_project_id = project_id

    def add_color_to_active(self, hex_color: str) -> bool:
        """
        Agrega un color a la paleta del proyecto activo.
        Evita duplicados consecutivos o repetidos si ya existe.
        Retorna True si fue agregado, False si ya estaba.
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
        """Agrega una lista de colores al proyecto activo. Retorna cuántos se añadieron."""
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
        """Limpia los colores guardados del proyecto actual."""
        project = self.get_active_project()
        if project:
            project["palette"] = []
            self._save_data()

    def delete_project(self, project_id: str):
        """Elimina un proyecto del registro."""
        self.projects = [p for p in self.projects if p["id"] != project_id]
        if self.active_project_id == project_id:
            self.active_project_id = self.projects[0]["id"] if self.projects else None
        self._save_data()
    
    def remove_color_from_active(self, hex_color: str) -> bool:
        """Elimina un color específico de la paleta del proyecto activo."""
        project = self.get_active_project()
        if not project:
            return False

        hex_color = hex_color.upper()
        if hex_color in project["palette"]:
            project["palette"].remove(hex_color)
            self._save_data()
            return True
        return False