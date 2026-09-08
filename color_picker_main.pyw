"""
Main entry point for Color Picker & Palette Extractor.
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
        # 0x10 = FR_PRIVATE (only available to your process while it is open)
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

def get_asset_path(relative_path):
    """Gets the absolute path for development and for the PyInstaller executable."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) 

load_custom_font(get_asset_path("assets/fonts/determination.ttf"))
load_custom_font(get_asset_path("assets/fonts/Panton-Trial-Bold.ttf"))
load_custom_font(get_asset_path("assets/fonts/Panton-Trial-Regular.ttf"))

# Activate DPI awareness in Windows
if sys.platform == "win32":
    try:
        # Compatible with Windows 10/11
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            # Fallback for older versions of Windows
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Set AppUserModelID so that Windows displays the icon on the taskbar
try:
    myappid = "pythonprojects.gui.colorpicker.2.0"
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
        
        # Data manager instance
        self.pm = ProjectManager()
        
        # Theme manager instance
        self.tm = ThemeManager(initial_theme=self.pm.theme_name)
        
        self.configure(bg=self.tm.colors["bg"])
        
        # Main container
        self.main_container = tk.Frame(self, bg=self.tm.colors["bg"])
        self.main_container.pack(fill="both", expand=True)

        # Load the initial active project if it exists

        self.project_manager = ProjectManager()

        # ThemeManager takes care of the colors
        self.tm = ThemeManager(
            initial_theme=self.project_manager.theme_name,
            on_theme_change=self.project_manager.save_theme_preference,
            initial_font= self.project_manager.font_name
        )
    
        self._build_ui()
        
    def _build_ui(self):
        # 1. If a previous container already exists (by a toggle), destroy it
        if self.main_container is not None:
            self.main_container.destroy()

        self.configure(bg=self.tm.colors["bg"])

        # 2. Create a NEW container hanging directly from the window (self)
        self.main_container = tk.Frame(self, bg=self.tm.colors["bg"])
        self.main_container.pack(fill="both", expand=True)

        # 3. Pack the sidebar and workspace inside this new main_container
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
        # Determine base_dir compatible with development and PyInstaller
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
                self._app_icon_img = tk.PhotoImage(file=png_path)  # Save reference to avoid garbage collection
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass

    def _on_project_changed(self):
        self.workspace.load_active_project()

    def _on_palette_updated(self):
        pass
    
    def _handle_theme_toggle(self):
        self.tm.toggle_theme()
        # 1. Tell the ProjectManager and save in the JSON immediately:
        self.pm.save_theme_preference(self.tm.current_theme_name)
        # 2. Rebuild UI:
        self._build_ui()

    def _handle_font_toggle(self):
        self.tm.toggle_font()
        # 1. Tell the ProjectManager and save in the JSON immediately:
        self.pm.save_font_preference(self.tm.current_font_name)
        # 2. Rebuild UI:
        self._build_ui()
        
if __name__ == "__main__":
    app = ColorPickerApp()
    app.mainloop()