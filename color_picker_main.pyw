"""
Punto de entrada principal para Color Picker & Palette Extractor.
"""

import sys
import ctypes
import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD

import core.config as config
from core.project_manager import ProjectManager
from views.sidebar_view import SidebarView
from views.workspace_view import WorkspaceView
from core.theme_manager import ThemeManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_custom_font(relative_path: str):
    font_path = os.path.join(BASE_DIR, relative_path)
    if os.path.exists(font_path):
        # 0x10 = FR_PRIVATE (solo disponible para tu proceso mientras esté abierto)
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

load_custom_font("assets/fonts/determination.ttf")
load_custom_font("assets/fonts/Panton-Trial-Bold.ttf")
load_custom_font("assets/fonts/Panton-Trial-Regular.ttf")

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


class ColorPickerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WIDTH, config.MIN_HEIGHT)
        
        self._set_app_icon()
        
        # Instancia del gestor de datos
        self.pm = ProjectManager()
        
        # Instancia del gestor de tema
        self.tm = ThemeManager(initial_theme=self.pm.theme_name)
        
        self.configure(bg=self.tm.colors["bg"])
        
        # Contenedor principal
        self.main_container = tk.Frame(self, bg=self.tm.colors["bg"])
        self.main_container.pack(fill="both", expand=True)

        # Cargar el proyecto activo inicial si existe

        self.project_manager = ProjectManager()

        # ThemeManager se encarga de los colores
        self.tm = ThemeManager(
            initial_theme=self.project_manager.theme_name,
            on_theme_change=self.project_manager.save_theme_preference,
            initial_font= self.project_manager.font_name
        )
    
        self._build_ui()
        
    def _build_ui(self):
        # 1. Si ya existe un contenedor previo (por un toggle), destrúyelo
        if self.main_container is not None:
            self.main_container.destroy()

        self.configure(bg=self.tm.colors["bg"])

        # 2. Crea un contenedor NUEVO colgado directamente de la ventana (self)
        self.main_container = tk.Frame(self, bg=self.tm.colors["bg"])
        self.main_container.pack(fill="both", expand=True)

        # 3. Empaca la sidebar y workspace dentro de este nuevo main_container
        self.sidebar = SidebarView(
            self.main_container,
            project_manager=self.pm,
            theme_manager=self.tm,
            on_project_selected=self._on_project_changed,
            on_theme_toggle=self._handle_theme_toggle,
            on_font_toggle=self._handle_font_toggle,
            on_project_activated=lambda: self.workspace.load_active_project()
        )
        self.sidebar.pack(side="left", fill="y")

        self.workspace = WorkspaceView(
            self.main_container,
            project_manager=self.pm,
            theme_manager=self.tm,
            on_palette_updated=self.sidebar.refresh_list,
            on_file_dropped=self.sidebar._on_new_palette_clicked
        )
        self.workspace.pack(side="right", fill="both", expand=True)

    def _set_app_icon(self):
        # Determinar base_dir compatible con desarrollo y con PyInstaller
        try:
            base_dir = sys._MEIPASS
        except AttributeError:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        ico_path = os.path.join(base_dir, "assets/icon.ico")
        png_path = os.path.join(base_dir, "assets/icon.png")

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
    
    def _handle_theme_toggle(self):
        self.tm.toggle_theme()
        # 1. Avisarle al ProjectManager y guardar en el JSON de inmediato:
        self.pm.save_theme_preference(self.tm.current_theme_name)
        # 2. Reconstruir UI:
        self._build_ui()

    def _handle_font_toggle(self):
        self.tm.toggle_font()
        # 1. Avisarle al ProjectManager y guardar en el JSON de inmediato:
        self.pm.save_font_preference(self.tm.current_font_name)
        # 2. Reconstruir UI:
        self._build_ui()
        
if __name__ == "__main__":
    app = ColorPickerApp()
    app.mainloop()