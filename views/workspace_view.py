"""
Área de trabajo: renderizado de imagen con zoom adaptativo, cuentagotas y grid de colores.
"""
from tkinter import ttk
import os
import tkinter as tk
from tkinterdnd2 import DND_FILES
import core.color_engine as color_engine

class WorkspaceView(tk.Frame):
    def __init__(self, parent, project_manager, theme_manager, on_palette_updated, on_file_dropped=None):
        self.tm = theme_manager
        self.pm = project_manager
        self.on_palette_updated = on_palette_updated

        super().__init__(parent, bg=self.tm.colors["bg"])
        
        self.current_original_img = None
        self.current_tk_img = None
        self.current_scale = 1.0
        self.loupe_enabled = tk.BooleanVar(value=True)
        self.on_file_dropped = on_file_dropped

        self._build_ui()
        self._setup_dnd()

    def _build_ui(self):
        # 1. Barra superior de proyecto
        self.header_frame = tk.Frame(self, bg=self.tm.colors["bg"])
        self.header_frame.pack(fill="x", padx=20, pady=(16, 10))

        self.lbl_title = tk.Label(
            self.header_frame,
            text="Select or create a palette",
            font=self.tm.fonts["title"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_main"],
        )
        self.lbl_title.pack(side="left")

        # Toast notification para 'Copied!'
        self.lbl_feedback = tk.Label(
            self.header_frame,
            text="",
            font=self.tm.fonts["subtitle"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["accent"],
        )
        self.lbl_feedback.pack(side="right", padx=10)

        # 2. Contenedor de la Imagen / Canvas
        self.canvas_card = tk.Frame(
            self,
            bg=self.tm.colors["card_bg"],
            highlightbackground=self.tm.colors["canvas_border"],
            highlightthickness=1,
        )
        self.canvas_card.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.canvas = tk.Canvas(
            self.canvas_card,
            bg=self.tm.colors["card_bg"],
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Button-1>", self._on_canvas_clicked)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Eventos para una lupa minimalista XD
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        # 3. Barra de acciones (Herramientas)
        self.toolbar_frame = tk.Frame(self, bg=self.tm.colors["bg"])
        self.toolbar_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.lbl_hint = tk.Label(
            self.toolbar_frame,
            text="• Left click: Copy HEX  |  Right click: Delete  |  Scroll: Wheel",
            font=self.tm.fonts["badge"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_2"],
        )
        self.lbl_hint.pack(side="right")
        
        self.btn_auto = tk.Button(
            self.toolbar_frame,
            text="✨ Auto Extract Palette",
            font=self.tm.fonts["normal"],
            bg=self.tm.colors["button_2"],
            fg=self.tm.colors["text_main"],
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._extract_auto_palette,
        )
        self.btn_auto.pack(side="left", padx=(0, 8))

        self.btn_clear = tk.Button(
            self.toolbar_frame,
            text="Clear Swatches",
            font=self.tm.fonts["normal"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_2"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=4,
            command=self._clear_palette,
        )
        self.btn_clear.pack(side="left")
        
        # Button para activar o desactivar la lupa
        self.chk_loupe = tk.Checkbutton(
            self.toolbar_frame,
            text="⌕ Loupe",
            variable=self.loupe_enabled,
            command=self._on_toggle_loupe,
            font=self.tm.fonts["inspector"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["text_main"],
            activebackground=self.tm.colors["bg"],
            activeforeground=self.tm.colors["text_main"],
            selectcolor=self.tm.colors["card_bg"],
            cursor="hand2",
        )
        self.chk_loupe.pack(side="left", padx=(0,0))

        # 4. Contenedor Scrolleable para Swatches
        self.swatches_outer = tk.Frame(self, bg=self.tm.colors["bg"], height=78)
        self.swatches_outer.pack(fill="x", padx=20, pady=(0, 10))
        self.swatches_outer.pack_propagate(False)

        # Barra de desplazamiento horizontal
        self.swatches_scrollbar = ttk.Scrollbar(
            self.swatches_outer, orient="horizontal"
        )

        self.swatches_canvas = tk.Canvas(
            self.swatches_outer,
            bg=self.tm.colors["bg"],
            highlightthickness=0,
            height=54,
            xscrollcommand=self.swatches_scrollbar.set,
        )
        self.swatches_scrollbar.config(command=self.swatches_canvas.xview)

        self.swatches_canvas.pack(side="top", fill="both", expand=True)
        # La scrollbar se empaca debajo del canvas
        self.swatches_scrollbar.pack(side="bottom", fill="x")

        self.swatches_inner = tk.Frame(
            self.swatches_canvas, bg=self.tm.colors["bg"]
        )
        self.canvas_window_id = self.swatches_canvas.create_window(
            (0, 0), window=self.swatches_inner, anchor="nw"
        )

        # Actualizar área scrolleable y visibilidad de la barra
        self.swatches_inner.bind("<Configure>", self._on_swatches_configure)
        self.swatches_canvas.bind("<Configure>", self._on_swatches_configure)

        # Soporte para rueda del ratón
        self.swatches_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.swatches_inner.bind("<MouseWheel>", self._on_mousewheel)

    def _on_swatches_configure(self, event=None):
        bbox = self.swatches_canvas.bbox("all")
        if not bbox:
            return

        content_width = bbox[2] - bbox[0]
        visible_width = self.swatches_canvas.winfo_width()

        # Si el contenido cabe en la pantalla, fijar el scroll al inicio y no scrollear
        if content_width <= visible_width:
            self.swatches_canvas.configure(scrollregion=(0, 0, visible_width, bbox[3]))
            self.swatches_canvas.xview_moveto(0)
            self.swatches_scrollbar.pack_forget()
        else:
            self.swatches_canvas.configure(scrollregion=bbox)
            if not self.swatches_scrollbar.winfo_ismapped():
                self.swatches_scrollbar.pack(side="bottom", fill="x")

    def _on_mousewheel(self, event):
        bbox = self.swatches_canvas.bbox("all")
        if not bbox:
            return

        content_width = bbox[2] - bbox[0]
        visible_width = self.swatches_canvas.winfo_width()

        # Solo scrollear si los elementos realmente desbordan el área visible
        if content_width > visible_width:
            self.swatches_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _render_swatches(self, colors: list[str]):
        for widget in self.swatches_inner.winfo_children():
            widget.destroy()

        if not colors:
            hint = tk.Label(
                self.swatches_inner,
                text="Click on any pixel or use 'Auto Extract' to collect main colors.",
                font=self.tm.fonts["normal"],
                bg=self.tm.colors["bg"],
                fg=self.tm.colors["text_2"],
            )
            hint.pack(anchor="w", pady=16)
            return

        for hex_code in colors:
            box = tk.Frame(
                self.swatches_inner,
                bg=hex_code,
                width=42,
                height=42,
                relief="flat",
                cursor="hand2",
                highlightbackground=self.tm.colors["canvas_border"],
                highlightthickness=1,
            )
            box.pack(side="left", padx=4, pady=8)
            box.pack_propagate(False)

            # Clic izquierdo para copiar
            box.bind("<Button-1>", lambda e, c=hex_code: self._copy_to_clipboard(c))

            # Clic derecho (<Button-3>) para eliminar
            box.bind("<Button-3>", lambda e, c=hex_code: self._remove_single_color(c))

            # Pasar el scroll si el puntero está encima de los cuadritos
            box.bind("<MouseWheel>", self._on_mousewheel)

    def load_active_project(self):
        project = self.pm.get_active_project()
        self.canvas.delete("all")

        if not project:
            self.lbl_title.config(text="Select or create a palette")
            self.btn_auto.config(state="disabled")
            self.btn_clear.config(state="disabled")
            self.current_original_img = None
            self.current_tk_img = None
            self._render_swatches([])
            return

        self.lbl_title.config(text=project["name"])
        self.btn_auto.config(state="normal")
        self.btn_clear.config(state="normal")

        image_path = project.get("image_path", "")
        if not os.path.exists(image_path):
            self.canvas.create_text(
                200, 
                150, 
                text="Image not found at path.", 
                font=self.tm.fonts["normal"], 
                fill=self.tm.colors["text_2"]
            )
            self.current_original_img = None
            self.current_tk_img = None
            self._render_swatches(project.get("palette", []))
            return
        
        # 1. Abrir la imagen primero
        from PIL import Image
        self.current_original_img = Image.open(image_path).convert("RGB")

        # 2. Asegurar dimensiones geométricas de la ventana
        self.update_idletasks()

        # 3. Renderizar y adaptar al tamaño disponible (éste método ya crea la imagen en el canvas)
        self._render_image_to_fit()

        # 4. Renderizar la paleta de swatches
        self._render_swatches(project.get("palette", []))

    def _on_canvas_resize(self, event):
        """Escala de nuevo cuando la ventana cambia de tamaño o se maximiza."""
        if self.current_original_img:
            self._render_image_to_fit()
    
    def _render_image_to_fit(self):
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        # Evitar cálculos antes de que Tkinter termine de mapear la ventana
        if c_w < 50 or c_h < 50:
            self.after(50, self._render_image_to_fit)
            return
        
        # Margen para no tocar el borde del card
        avail_w = max(20, c_w - 20)
        avail_h = max(20, c_h - 20)

        orig_w, orig_h = self.current_original_img.size
        ratio = min(avail_w / orig_w, avail_h / orig_h)

        new_w = max(1, int(orig_w * ratio))
        new_h = max(1, int(orig_h * ratio))

        # Pixel art / sprites o upscale: mantener bordes nítidos con NEAREST
        if ratio >= 1.0 or (orig_w <= 128 and orig_h <= 128):
            resampling = color_engine.Image.Resampling.NEAREST
        else:
            resampling = color_engine.Image.Resampling.LANCZOS

        scaled = self.current_original_img.resize((new_w, new_h), resampling)

        self.current_tk_img = color_engine.ImageTk.PhotoImage(scaled)
        self.current_scale = ratio

        self.canvas.delete("all")
        self.canvas.create_image(
            c_w // 2,
            c_h // 2,
            image=self.current_tk_img,
            anchor="center",
            tags="main_img",
        )
    
    def _on_canvas_clicked(self, event):
        if not self.current_original_img or not self.current_tk_img:
            return

        # Calcular coordenadas relativas al centro de la imagen
        bbox = self.canvas.bbox("main_img")
        if not bbox:
            return
        x1, y1, x2, y2 = bbox

        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            rel_x = event.x - x1
            rel_y = event.y - y1
            hex_color = color_engine.get_color_at_pixel(
                self.current_original_img, rel_x, rel_y, self.current_scale
            )

            if self.pm.add_color_to_active(hex_color):
                self._render_swatches(self.pm.get_active_project()["palette"])
                self._show_feedback(f"Added {hex_color}!")

    def _extract_auto_palette(self):
        if not self.current_original_img:
            return
        colors = color_engine.extract_dominant_colors(self.current_original_img, num_colors=8)
        added = self.pm.add_multiple_colors_to_active(colors)
        if added > 0:
            self._render_swatches(self.pm.get_active_project()["palette"])
            self._show_feedback(f"Extracted {added} colors!")

    def _clear_palette(self):
        self.pm.clear_active_palette()
        self._render_swatches([])
        self._show_feedback("Palette cleared")

    def _remove_single_color(self, hex_code: str):
        if self.pm.remove_color_from_active(hex_code):
            self._render_swatches(self.pm.get_active_project()["palette"])
            self._show_feedback(f"Removed {hex_code}")
    
    def _copy_to_clipboard(self, hex_code: str):
        self.clipboard_clear()
        self.clipboard_append(hex_code)
        self._show_feedback(f"Copied {hex_code} to clipboard!")

    def _show_feedback(self, msg: str):
        self.lbl_feedback.config(text=msg)
        self.after(2200, lambda: self.lbl_feedback.config(text=""))
        
    def _on_mouse_move(self, event):
        """Muestra una mirilla minimalista con el color y HEX en tiempo real."""
        if not self.loupe_enabled.get():
            return

        if not self.current_original_img or not self.current_tk_img:
            return

        bbox = self.canvas.bbox("main_img")
        if not bbox:
            self.canvas.delete("loupe")
            return        
        
        x1, y1, x2, y2 = bbox

        # Si el cursor está dentro de la imagen
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            rel_x = event.x - x1
            rel_y = event.y - y1
            hex_color = color_engine.get_color_at_pixel(
                self.current_original_img, rel_x, rel_y, self.current_scale
            )

            # Posición flotante (offset hacia arriba y a la derecha del cursor)
            lx = event.x + 24
            ly = event.y - 24

            # Evitar que se desborde del canvas por arriba o derecha
            c_w = self.canvas.winfo_width()
            if lx + 70 > c_w:
                lx = event.x - 70
            if ly - 20 < 0:
                ly = event.y + 24

            # Redibujar la mini-píldora
            self.canvas.delete("loupe")

            # 1. Pastilla de fondo oscura/sutil
            self.canvas.create_rectangle(
                lx, ly - 14, lx + 76, ly + 14,
                fill="#1E201E",
                outline="#3A3D3A",
                width=1,
                tags="loupe"
            )

            # 2. Círculo que muestra la muestra de color
            self.canvas.create_oval(
                lx + 5, ly - 7, lx + 19, ly + 7,
                fill=hex_color,
                outline="#FFFFFF",
                width=1,
                tags="loupe"
            )

            # 3. Código HEX en texto fino
            self.canvas.create_text(
                lx + 46, ly,
                text=hex_color.upper(),
                fill="#EDEDED",
                font=("panton UI", 8, "bold"),
                tags="loupe"
            )
        else:
            self.canvas.delete("loupe")

    def _on_toggle_loupe(self):
        """Limpia la mirilla si el usuario la desactiva con el cursor encima."""
        if not self.loupe_enabled.get():
            self.canvas.delete("loupe")
    
    def _on_mouse_leave(self, event=None):
        """Oculta la lupa cuando el ratón sale del área del canvas."""
        self.canvas.delete("loupe")
    
    def _setup_dnd(self):
        # Registrar este frame para aceptar exclusivamente archivos
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_file_drop)

    def _on_file_drop(self, event):
        filepath = event.data.strip()
        if filepath.startswith("{") and filepath.endswith("}"):
            filepath = filepath[1:-1]

        # Llama al callback recibido en el __init__, NO a esta misma función:
        if self.on_file_dropped:
            self.on_file_dropped(filepath)