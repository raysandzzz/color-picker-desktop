"""
Vista del sidebar lateral para navegación de proyectos y creación de lienzos.
"""

import tkinter as tk
from tkinter import filedialog, messagebox


class SidebarView(tk.Frame):
    def __init__(self, 
                parent, 
                project_manager, 
                theme_manager, 
                on_project_selected, 
                on_theme_toggle=None, 
                on_font_toggle=None,
                on_project_activated=None
                ):
        self.tm = theme_manager
        self.pm = project_manager
        self.on_project_selected = on_project_selected
        self.on_theme_toggle = on_theme_toggle
        self.on_font_toggle = on_font_toggle
        self.on_project_activated = on_project_activated
        
        super().__init__(parent, bg=self.tm.colors["sidebar"], width=220)
        self.pack_propagate(False)

        self._build_header()
        self._build_project_list()
        self.refresh_list()

    def _prompt_palette_name(self, initial_value: str = "New Palette") -> str | None:
        """Modal con dimensiones fijas y estilo consistente para ingresar el nombre."""
        dialog = tk.Toplevel(self)
        dialog.title("Palette Name")
        dialog.geometry("360x150")
        dialog.resizable(False, False)
        dialog.configure(bg=self.tm.colors["bg"])
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
            font=self.tm.fonts["normal"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_main"],
        )
        lbl.pack(anchor="w", padx=20, pady=(16, 8))

        entry = tk.Entry(dialog, font=self.tm.fonts["normal"], relief="solid", bd=1)
        entry.pack(fill="x", padx=20, ipady=3)
        entry.insert(0, initial_value)
        entry.select_range(0, tk.END)
        entry.focus_set()

        btn_frame = tk.Frame(dialog, bg=self.tm.colors["bg"])
        btn_frame.pack(fill="x", padx=20, pady=(16, 12))

        def confirm(event=None):
            result["name"] = entry.get()
            dialog.destroy()

        def cancel(event=None):
            dialog.destroy()

        btn_cancel = tk.Button(
            btn_frame,
            text="Cancel",
            font=self.tm.fonts["normal"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_2"],
            relief="flat",
            cursor="hand2",
            padx=10,
            command=cancel,
        )
        btn_cancel.pack(side="right", padx=(6, 0))

        btn_ok = tk.Button(
            btn_frame,
            text="Confirm",
            font=self.tm.fonts["subtitle"],
            bg=self.tm.colors["accent"],
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
        header_frame = tk.Frame(self, bg=self.tm.colors["sidebar"])
        header_frame.pack(fill="x", padx=14, pady=(16, 10))

        title = tk.Label(
            header_frame,
            text="Color Picker",
            font=self.tm.fonts["title"],
            bg=self.tm.colors["sidebar"],
            fg=self.tm.colors["text_main"],
        )
        title.pack(anchor="w")

        btn_new = tk.Button(
            self,
            text="➕ New Palette",
            font=self.tm.fonts["subtitle"],
            bg=self.tm.colors["accent"],
            fg="#FFFFFF",
            activebackground=self.tm.colors["accent"],
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
            font=self.tm.fonts["badge"],
            bg=self.tm.colors["sidebar"],
            fg=self.tm.colors["text_2"],
        )
        lbl_section.pack(anchor="w", padx=14, pady=(4, 6))

    def _build_project_list(self):
        footer_frame = tk.Frame(self, bg=self.tm.colors["sidebar"])
        footer_frame.pack(side="bottom", fill="x", padx=12, pady=12)
        
        font_txt = "Aa Pixel" if self.tm.current_font_name == "panton" else "Aa Clean"
        self.btn_font = tk.Button(
            footer_frame,
            text=font_txt,
            font=self.tm.fonts["badge"],
            bg=self.tm.colors["button_2"],
            fg=self.tm.colors["text_main"],
            activebackground=self.tm.colors["button_2"],
            activeforeground=self.tm.colors["text_main"],
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.on_font_toggle,
        )
        self.btn_font.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Botón Theme Toggle (Dark / Light)
        theme_txt = (
            "☀️ Light" if self.tm.current_theme_name == "dark" else "🌙 Dark"
        )
        self.btn_theme = tk.Button(
            footer_frame,
            text=theme_txt,
            font=self.tm.fonts["badge"],
            bg=self.tm.colors["button_2"],
            fg=self.tm.colors["text_main"],
            activebackground=self.tm.colors["button_2"],
            activeforeground=self.tm.colors["text_main"],
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.on_theme_toggle,
        )
        self.btn_theme.pack(side="right", fill="x", expand=True, padx=(4, 0))
        
        # 1. Marco exterior
        self.scroll_container = tk.Frame(self, bg=self.tm.colors["sidebar"])
        self.scroll_container.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # 2. Scrollbar vertical
        self.sidebar_scrollbar = tk.Scrollbar(
            self.scroll_container, orient="vertical"
        )

        # 3. Canvas intermedio para permitir el desplazamiento
        self.list_canvas = tk.Canvas(
            self.scroll_container,
            bg=self.tm.colors["sidebar"],
            highlightthickness=0,
            yscrollcommand=self.sidebar_scrollbar.set,
        )
        self.sidebar_scrollbar.config(command=self.list_canvas.yview)

        self.list_canvas.pack(side="left", fill="both", expand=True)

        # 4. El contenedor real donde se añaden los proyectos (mismo nombre para compatibilidad)
        self.list_container = tk.Frame(self.list_canvas, bg=self.tm.colors["sidebar"])
        self.list_window_id = self.list_canvas.create_window(
            (0, 0), window=self.list_container, anchor="nw"
        )

        # 5. Eventos para ajustar dimensiones y el scroll con la rueda
        self.list_container.bind("<Configure>", self._on_list_configure)
        self.list_canvas.bind("<Configure>", self._on_canvas_configure)

        self.list_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.list_container.bind("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        """Mantiene el frame de palettes con el mismo ancho que el canvas."""
        self.list_canvas.itemconfig(self.list_window_id, width=event.width)

    def _on_list_configure(self, event=None):
        """Muestra u oculta la barra de desplazamiento según el desbordamiento."""
        bbox = self.list_canvas.bbox("all")
        if not bbox:
            return

        content_height = bbox[3] - bbox[1]
        visible_height = self.list_canvas.winfo_height()

        if content_height <= visible_height:
            self.list_canvas.configure(scrollregion=(0, 0, bbox[2], visible_height))
            self.list_canvas.yview_moveto(0)
            self.sidebar_scrollbar.pack_forget()
        else:
            self.list_canvas.configure(scrollregion=bbox)
            if not self.sidebar_scrollbar.winfo_ismapped():
                self.sidebar_scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        """Permite deslizar la lista verticalmente con la rueda."""
        bbox = self.list_canvas.bbox("all")
        if not bbox:
            return

        content_height = bbox[3] - bbox[1]
        visible_height = self.list_canvas.winfo_height()

        if content_height > visible_height:
            self.list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        projects = self.pm.get_all_projects()
        active_id = self.pm.active_project_id

        if not projects:
            empty_lbl = tk.Label(
                self.list_container,
                text="No palettes yet.\nClick '+ New Palette' to start.",
                font=self.tm.fonts["normal"],
                bg=self.tm.colors["sidebar"],
                fg=self.tm.colors["text_2"],
                justify="center",
            )
            empty_lbl.pack(pady=20)
            return

        for p in projects:
            is_active = p["id"] == active_id
            bg_color = self.tm.colors["card_bg"] if is_active else self.tm.colors["sidebar"]
            fg_color = self.tm.colors["text_main"] if is_active else self.tm.colors["text_2"]

            row = tk.Frame(self.list_container, bg=bg_color, cursor="hand2")
            row.pack(fill="x", pady=2, padx=4)
            
            # 1. Empacar PRIMERO el botón de borrar a la derecha para que nunca sea desplazado
            btn_del = tk.Label(
                row,
                text="✕",
                font=("panton UI", 9),
                bg=bg_color,
                fg=self.tm.colors["text_2"],
                cursor="hand2",
                padx=6,
            )
            btn_del.pack(side="right", padx=(0, 4))

            # 2. Si el nombre es muy largo, se corta con los puntos suspensivos
            raw_name = p["name"]
            display_name = raw_name if len(raw_name) <= 22 else raw_name[:20].rstrip() + "..."

            # 3. Empacar el Label con el texto truncado en el espacio sobrante
            name_lbl = tk.Label(
                row,
                text=display_name,
                font=self.tm.fonts["normal"],
                bg=bg_color,
                fg=fg_color,
                anchor="w",
            )
            name_lbl.pack(side="left", fill="x", expand=True, padx=(8, 2), pady=6)

            # Eventos
            row.bind("<Button-1>", lambda e, pid=p["id"]: self._select_project(pid))
            name_lbl.bind("<Button-1>", lambda e, pid=p["id"]: self._select_project(pid))
            btn_del.bind("<Button-1>", lambda e, pid=p["id"], name=p["name"]: self._on_delete_project_clicked(pid, name))

            # Propagar scroll de la rueda del ratón
            row.bind("<MouseWheel>", self._on_mousewheel)
            name_lbl.bind("<MouseWheel>", self._on_mousewheel)
            btn_del.bind("<MouseWheel>", self._on_mousewheel)          
            
    def _on_delete_project_clicked(self, project_id: str, name: str):
        if messagebox.askyesno("Delete Canvas", f"Are you sure you want to delete '{name}'?"):
            self.pm.delete_project(project_id)
            self.refresh_list()
            self.on_project_selected()
    
    def _select_project(self, project_id: str):
        self.pm.set_active_project(project_id)
        self.refresh_list()
        self.on_project_selected()

    def _on_new_palette_clicked(self, filepath=None):
        # 1. Si no viene del Drag & Drop, abrir el explorador de archivos
        if not filepath:
            file_types = [
                (
                    "Image files",
                    "*.png *.jpg *.jpeg *.bmp *.webp *.gif *.tiff",
                )
            ]
            filepath = filedialog.askopenfilename(
                title="Select an Image", filetypes=file_types
            )

        # 2. Si canceló el diálogo o no hay ruta, salir
        if not filepath:
            return

        # 3. Solicitar y validar nombre de la paleta
        name = "New Palette"
        while True:
            name = self._prompt_palette_name(name)
            if name is None:  # Presionó Cancel
                return

            clean_name = name.strip()
            if not clean_name:
                messagebox.showwarning(
                    "Invalid Name", "Palette name cannot be empty."
                )
                name = "New Palette"
                continue

            if self.pm.project_name_exists(clean_name):
                messagebox.showwarning(
                    "Name In Use",
                    f"A palette named '{clean_name}' already exists. Please choose a different name.",
                )
                continue

            # Nombre válido y no duplicado
            break

        # 4. Crear el proyecto
        new_project = self.pm.create_project(name=clean_name, image_path=filepath)

        # 5. NUEVO: Seleccionarlo como el proyecto activo actual
        if hasattr(self.pm, "set_active_project"):
            self.pm.set_active_project(new_project.get("id", clean_name))  # o por nombre/objeto según cómo lo maneje tu PM
        # 6. Refrescar la UI
        self.refresh_list()
        
        if self.on_project_activated:
            self.on_project_activated()