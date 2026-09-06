"""
Punto de entrada principal para Color Picker & Palette Extractor.
"""

import sys
import ctypes
import os
import tkinter as tk

import config
from project_manager import ProjectManager
from views.sidebar_view import SidebarView
from views.workspace_view import WorkspaceView


def get_asset_path(relative_path):
    """Obtiene la ruta absoluta para desarrollo y para el ejecutable de PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Activar DPI awareness en Windows
if sys.platform == "win32":
    try:
        # Compatible con Windows 10/11
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            # Fallback para versiones anteriores de Windows
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

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
        # Determinar base_dir compatible con desarrollo y con PyInstaller
        try:
            base_dir = sys._MEIPASS
        except AttributeError:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        ico_path = os.path.join(base_dir, "icon.ico")
        png_path = os.path.join(base_dir, "icon.png")

        if os.path.exists(ico_path):
            try:
                self.iconbitmap(default=ico_path)
            except Exception:
                pass
        elif os.path.exists(png_path):
            try:
                self._app_icon_img = tk.PhotoImage(file=png_path)  # Guardar referencia para evitar garbage collection
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass

    def _on_project_changed(self):
        self.workspace.load_active_project()

    def _on_palette_updated(self):
        pass


if __name__ == "__main__":
    app = ColorPickerApp()
    app.mainloop()