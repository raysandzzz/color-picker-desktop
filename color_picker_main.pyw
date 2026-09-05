"""
Punto de entrada principal para Pastel Color Picker & Palette Extractor.
"""

import ctypes
import os
import tkinter as tk

import config
from project_manager import ProjectManager
from views.sidebar_view import SidebarView
from views.workspace_view import WorkspaceView

# Configurar AppUserModelID para que Windows muestre el icono en la barra de tareas
try:
    myappid = "pythonprojects.gui.pastelcolorpicker.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass


class ColorPickerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WIDTH, config.MIN_HEIGHT)
        self.configure(bg=config.COLOR_BG_DARK)

        self._set_app_icon()

        # Instanciar el gestor de datos
        self.pm = ProjectManager()

        # Contenedor principal
        self.main_container = tk.Frame(self, bg=config.COLOR_BG_DARK)
        self.main_container.pack(fill="both", expand=True)

        # Montar W  orkspace a la derecha
        self.workspace = WorkspaceView(
            self.main_container,
            project_manager=self.pm,
            on_palette_updated=self._on_palette_updated,
        )
        self.workspace.pack(side="right", fill="both", expand=True)

        # Montar Sidebar a la izquierda
        self.sidebar = SidebarView(
            self.main_container,
            project_manager=self.pm,
            on_project_selected=self._on_project_changed,
        )
        self.sidebar.pack(side="left", fill="y")

        # Cargar el proyecto activo inicial si existe
        self.workspace.load_active_project()

    def _set_app_icon(self):
        base_dir = os.path.dirname(__file__)
        ico_path = os.path.join(base_dir, "icon.ico")
        png_path = os.path.join(base_dir, "icon.png")

        if os.path.exists(ico_path):
            try:
                self.iconbitmap(default=ico_path)
            except Exception:
                pass
        elif os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, img)
            except Exception:
                pass

    def _on_project_changed(self):
        self.workspace.load_active_project()

    def _on_palette_updated(self):
        pass


if __name__ == "__main__":
    app = ColorPickerApp()
    app.mainloop()