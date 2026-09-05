"""
Área de trabajo: renderizado de imagen con zoom adaptativo, cuentagotas y grid de colores.
"""
from tkinter import messagebox, ttk
import os
import tkinter as tk
import config
import color_engine


class WorkspaceView(tk.Frame):
    def __init__(self, parent, project_manager, on_palette_updated):
        super().__init__(parent, bg=config.COLOR_BG_DARK)
        self.pm = project_manager
        self.on_palette_updated = on_palette_updated

        self.current_original_img = None
        self.current_tk_img = None
        self.current_scale = 1.0

        self._build_ui()

    def _build_ui(self):
        # 1. Barra superior de proyecto
        self.header_frame = tk.Frame(self, bg=config.COLOR_BG_DARK)
        self.header_frame.pack(fill="x", padx=20, pady=(16, 10))

        self.lbl_title = tk.Label(
            self.header_frame,
            text="Select or create a palette",
            font=config.FONT_TITLE,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_TEXT_MAIN,
        )
        self.lbl_title.pack(side="left")

        # Toast notification para 'Copied!'
        self.lbl_feedback = tk.Label(
            self.header_frame,
            text="",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_ACCENT_HOVER,
        )
        self.lbl_feedback.pack(side="right", padx=10)

        # 2. Contenedor de la Imagen / Canvas
        self.canvas_card = tk.Frame(self, bg=config.COLOR_CARD_BG, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        self.canvas_card.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.canvas = tk.Canvas(
            self.canvas_card,
            bg=config.COLOR_CARD_BG,
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Button-1>", self._on_canvas_clicked)

        # 3. Barra de acciones (Herramientas)
        self.toolbar_frame = tk.Frame(self, bg=config.COLOR_BG_DARK)
        self.toolbar_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.lbl_hint = tk.Label(
            self.toolbar_frame,
            text="• Left click: Copy HEX  |  Right click: Delete  |  Scroll: Wheel",
            font=config.FONT_BADGE,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_TEXT_MUTED,
        )
        self.lbl_hint.pack(side="right")
        
        self.btn_auto = tk.Button(
            self.toolbar_frame,
            text="✨ Auto Extract Palette",
            font=config.FONT_NORMAL,
            bg=config.COLOR_BUTTON_SECONDARY,
            fg=config.COLOR_TEXT_MAIN,
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
            font=config.FONT_NORMAL,
            bg=config.COLOR_BG_DARK,
            fg=config.COLOR_TEXT_MUTED,
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=4,
            command=self._clear_palette,
        )
        self.btn_clear.pack(side="left")

        # 4. Contenedor Scrolleable para Swatches
        self.swatches_outer = tk.Frame(self, bg=config.COLOR_BG_DARK, height=78)
        self.swatches_outer.pack(fill="x", padx=20, pady=(0, 10))
        self.swatches_outer.pack_propagate(False)

        # Barra de desplazamiento horizontal
        self.swatches_scrollbar = ttk.Scrollbar(
            self.swatches_outer, orient="horizontal"
        )

        self.swatches_canvas = tk.Canvas(
            self.swatches_outer,
            bg=config.COLOR_BG_DARK,
            highlightthickness=0,
            height=54,
            xscrollcommand=self.swatches_scrollbar.set,
        )
        self.swatches_scrollbar.config(command=self.swatches_canvas.xview)

        self.swatches_canvas.pack(side="top", fill="both", expand=True)
        # La scrollbar se empaca debajo del canvas
        self.swatches_scrollbar.pack(side="bottom", fill="x")

        self.swatches_inner = tk.Frame(
            self.swatches_canvas, bg=config.COLOR_BG_DARK
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
                font=config.FONT_NORMAL,
                bg=config.COLOR_BG_DARK,
                fg=config.COLOR_TEXT_MUTED,
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
                highlightbackground=config.COLOR_BORDER,
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
            self.lbl_title.config(text="No palette Selected")
            self.btn_auto.config(state="disabled")
            self.btn_clear.config(state="disabled")
            self._render_swatches([])
            return

        self.lbl_title.config(text=project["name"])
        self.btn_auto.config(state="normal")
        self.btn_clear.config(state="normal")

        image_path = project.get("image_path", "")
        if not os.path.exists(image_path):
            self.canvas.create_text(
                200, 150, text="Image not found at path.", font=config.FONT_NORMAL, fill=config.COLOR_TEXT_MUTED
            )
            self._render_swatches(project.get("palette", []))
            return

        # Escalar y montar en canvas
        orig, scaled, tk_img, scale = color_engine.load_and_scale_image(
            image_path, config.CANVAS_MAX_WIDTH, config.CANVAS_MAX_HEIGHT
        )
        self.current_original_img = orig
        self.current_tk_img = tk_img
        self.current_scale = scale

        # Posicionar imagen en el centro del canvas
        self.canvas.create_image(
            config.CANVAS_MAX_WIDTH // 2,
            config.CANVAS_MAX_HEIGHT // 2,
            image=self.current_tk_img,
            anchor="center",
            tags="main_img",
        )

        self._render_swatches(project.get("palette", []))

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