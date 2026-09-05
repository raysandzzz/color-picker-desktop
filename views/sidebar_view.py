"""
Vista del sidebar lateral para navegación de proyectos y creación de lienzos.
"""

import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import config


class SidebarView(tk.Frame):
    def __init__(self, parent, project_manager, on_project_selected):
        super().__init__(parent, bg=config.COLOR_SIDEBAR, width=220)
        self.pack_propagate(False)
        self.pm = project_manager
        self.on_project_selected = on_project_selected

        self._build_header()
        self._build_project_list()
        self.refresh_list()

    def _prompt_palette_name(self, initial_value: str = "New Palette") -> str | None:
        """Modal con dimensiones fijas y estilo consistente para ingresar el nombre."""
        dialog = tk.Toplevel(self)
        dialog.title("Palette Name")
        dialog.geometry("360x150")
        dialog.resizable(False, False)
        dialog.configure(bg=config.COLOR_BG_DARK)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Centrar relativo a la ventana principal
        root_x = self.winfo_toplevel().winfo_x()
        root_y = self.winfo_toplevel().winfo_y()
        root_w = self.winfo_toplevel().winfo_width()
        root_h = self.winfo_toplevel().winfo_height()
        pos_x = root_x + (root_w // 2) - 180
        pos_y = root_y + (root_h // 2) - 75
        dialog.geometry(f"+{pos_x}+{pos_y}")

        result = {"name": None}

        lbl = tk.Label(
            dialog,
            text="Enter a name for this palette:",
            font=config.FONT_NORMAL,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_TEXT_MAIN,
        )
        lbl.pack(anchor="w", padx=20, pady=(16, 8))

        entry = tk.Entry(dialog, font=config.FONT_NORMAL, relief="solid", bd=1)
        entry.pack(fill="x", padx=20, ipady=3)
        entry.insert(0, initial_value)
        entry.select_range(0, tk.END)
        entry.focus_set()

        btn_frame = tk.Frame(dialog, bg=config.COLOR_BG_DARK)
        btn_frame.pack(fill="x", padx=20, pady=(16, 12))

        def confirm(event=None):
            result["name"] = entry.get()
            dialog.destroy()

        def cancel(event=None):
            dialog.destroy()

        btn_cancel = tk.Button(
            btn_frame,
            text="Cancel",
            font=config.FONT_NORMAL,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_TEXT_MUTED,
            relief="flat",
            cursor="hand2",
            padx=10,
            command=cancel,
        )
        btn_cancel.pack(side="right", padx=(6, 0))

        btn_ok = tk.Button(
            btn_frame,
            text="Confirm",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=2,
            command=confirm,
        )
        btn_ok.pack(side="right")

        dialog.bind("<Return>", confirm)
        dialog.bind("<Escape>", cancel)

        self.wait_window(dialog)
        return result["name"]
    
    def _build_header(self):
        header_frame = tk.Frame(self, bg=config.COLOR_SIDEBAR)
        header_frame.pack(fill="x", padx=14, pady=(16, 10))

        title = tk.Label(
            header_frame,
            text="Color Picker",
            font=config.FONT_TITLE,
            bg=config.COLOR_SIDEBAR,
            fg=config.COLOR_TEXT_MAIN,
        )
        title.pack(anchor="w")

        btn_new = tk.Button(
            self,
            text="➕ New Palette",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_ACCENT,
            fg="#FFFFFF",
            activebackground=config.COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            pady=6,
            command=self._on_new_palette_clicked,
        )
        btn_new.pack(fill="x", padx=14, pady=(6, 14))

        lbl_section = tk.Label(
            self,
            text="SAVED PALETTES",
            font=config.FONT_BADGE,
            bg=config.COLOR_SIDEBAR,
            fg=config.COLOR_TEXT_MUTED,
        )
        lbl_section.pack(anchor="w", padx=14, pady=(4, 6))

    def _build_project_list(self):
        self.list_container = tk.Frame(self, bg=config.COLOR_SIDEBAR)
        self.list_container.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    def refresh_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        projects = self.pm.get_all_projects()
        active_id = self.pm.active_project_id

        if not projects:
            empty_lbl = tk.Label(
                self.list_container,
                text="No projects yet.\nClick '+ New Palette' to start.",
                font=config.FONT_NORMAL,
                bg=config.COLOR_SIDEBAR,
                fg=config.COLOR_TEXT_MUTED,
                justify="center",
            )
            empty_lbl.pack(pady=20)
            return

        for p in projects:
            is_active = p["id"] == active_id
            bg_color = config.COLOR_CARD_BG if is_active else config.COLOR_SIDEBAR
            fg_color = config.COLOR_TEXT_MAIN if is_active else config.COLOR_TEXT_MUTED

            row = tk.Frame(self.list_container, bg=bg_color, cursor="hand2")
            row.pack(fill="x", pady=2, padx=4)

            name_lbl = tk.Label(
                row,
                text=p["name"],
                font=config.FONT_NORMAL,
                bg=bg_color,
                fg=fg_color,
                anchor="w",
            )
            name_lbl.pack(side="left", fill="x", expand=True, padx=(8, 2), pady=6)

            # Botón para borrar la paleta anteriormente extraida
            btn_del = tk.Label(
                row,
                text="✕",
                font=("Segoe UI", 9),
                bg=bg_color,
                fg=config.COLOR_TEXT_MUTED,
                cursor="hand2",
                padx=6,
            )
            btn_del.pack(side="right", padx=(0, 4))

            # Eventos
            row.bind("<Button-1>", lambda e, pid=p["id"]: self._select_project(pid))
            name_lbl.bind("<Button-1>", lambda e, pid=p["id"]: self._select_project(pid))
            btn_del.bind("<Button-1>", lambda e, pid=p["id"], name=p["name"]: self._on_delete_project_clicked(pid, name))

    def _on_delete_project_clicked(self, project_id: str, name: str):
        if messagebox.askyesno("Delete Canvas", f"Are you sure you want to delete '{name}'?"):
            self.pm.delete_project(project_id)
            self.refresh_list()
            self.on_project_selected()
    
    def _select_project(self, project_id: str):
        self.pm.set_active_project(project_id)
        self.refresh_list()
        self.on_project_selected()

    def _on_new_palette_clicked(self):
        file_types = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=file_types)

        if not file_path:
            return

        name = "New Palette"
        while True:
            name = self._prompt_palette_name(name)
            if name is None:  # Presionó Cancel
                return

            clean_name = name.strip()
            if not clean_name:
                messagebox.showwarning("Invalid Name", "Palette name cannot be empty.")
                name = "New Palette"
                continue

            if self.pm.project_name_exists(clean_name):
                messagebox.showwarning(
                    "Name In Use",
                    f"A palette named '{clean_name}' already exists. Please choose a different name."
                )
                continue

            # Nombre válido y no duplicado
            break

        project = self.pm.create_project(name, file_path)
        self.refresh_list()
        self.on_project_selected()