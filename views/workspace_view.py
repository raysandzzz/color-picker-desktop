"""
Área de trabajo: renderizado de imagen con zoom adaptativo, cuentagotas y grid de colores.
"""

import os
import tkinter as tk
from tkinter import messagebox
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
            text="Select or create a project",
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

        # 4. Grilla de Swatches (Cuadros de color)
        self.swatches_frame = tk.Frame(self, bg=config.COLOR_BG_DARK)
        self.swatches_frame.pack(fill="x", padx=20, pady=(0, 16))

    def load_active_project(self):
        project = self.pm.get_active_project()
        self.canvas.delete("all")

        if not project:
            self.lbl_title.config(text="No Project Selected")
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

    def _render_swatches(self, colors: list[str]):
        for widget in self.swatches_frame.winfo_children():
            widget.destroy()

        if not colors:
            hint = tk.Label(
                self.swatches_frame,
                text="Click on any pixel or use 'Auto Extract' to collect colors.",
                font=config.FONT_NORMAL,
                bg=config.COLOR_BG_DARK,
                fg=config.COLOR_TEXT_MUTED,
            )
            hint.pack(anchor="w", pady=6)
            return

        for hex_code in colors:
            box = tk.Frame(
                self.swatches_frame,
                bg=hex_code,
                width=42,
                height=42,
                relief="flat",
                cursor="hand2",
                highlightbackground=config.COLOR_BORDER,
                highlightthickness=1,
            )
            box.pack(side="left", padx=4, pady=4)
            box.pack_propagate(False)

            # Clic Izquierdo -> Copiar al portapapeles
            box.bind("<Button-1>", lambda e, c=hex_code: self._copy_to_clipboard(c))
            
            # Clic Derecho (<Button-3>) -> Eliminar swatch
            box.bind("<Button-3>", lambda e, c=hex_code: self._remove_single_color(c))

        if not colors:
            hint = tk.Label(
                self.swatches_frame,
                text="Click on any pixel or use 'Auto Extract' to collect colors.",
                font=config.FONT_NORMAL,
                bg=config.COLOR_BG_DARK,
                fg=config.COLOR_TEXT_MUTED,
            )
            hint.pack(anchor="w", pady=6)
            return

        for hex_code in colors:
            box = tk.Frame(
                self.swatches_frame,
                bg=hex_code,
                width=42,
                height=42,
                relief="flat",
                cursor="hand2",
                highlightbackground=config.COLOR_BORDER,
                highlightthickness=1,
            )
            box.pack(side="left", padx=4, pady=4)
            box.pack_propagate(False)

            # Clic para copiar al portapapeles
            box.bind("<Button-1>", lambda e, c=hex_code: self._copy_to_clipboard(c))

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