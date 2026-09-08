"""
Work area: image rendering with adaptive zoom, eyedropper and color grid.
"""
from tkinter import ttk
from tkinter import dialog
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
        # 1. Project top bar
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

        # Toast notification for 'Copied!'
        self.lbl_feedback = tk.Label(
            self.header_frame,
            text="",
            font=self.tm.fonts["subtitle"],
            bg=self.tm.colors["bg"],
            fg=self.tm.colors["accent"],
        )
        self.lbl_feedback.pack(side="right", padx=10)

        # 2. Image Container / Canvas
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
        
        # Events for a minimalist magnifying glass XD
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        # 3. Action Bar (Tools)
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
        
        # Button to activate or deactivate the magnifying glass
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

        # 4. Scrollable Container for Swatches
        self.swatches_outer = tk.Frame(self, bg=self.tm.colors["bg"], height=78)
        self.swatches_outer.pack(fill="x", padx=20, pady=(0, 10))
        self.swatches_outer.pack_propagate(False)

        # Horizontal scroll bar
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
        # The scrollbar is packed below the canvas
        self.swatches_scrollbar.pack(side="bottom", fill="x")

        self.swatches_inner = tk.Frame(
            self.swatches_canvas, bg=self.tm.colors["bg"]
        )
        self.canvas_window_id = self.swatches_canvas.create_window(
            (0, 0), window=self.swatches_inner, anchor="nw"
        )

        # Update scrollable area and bar visibility
        self.swatches_inner.bind("<Configure>", self._on_swatches_configure)
        self.swatches_canvas.bind("<Configure>", self._on_swatches_configure)

        # Mouse wheel support
        self.swatches_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.swatches_inner.bind("<MouseWheel>", self._on_mousewheel)

    def _on_swatches_configure(self, event=None):
        bbox = self.swatches_canvas.bbox("all")
        if not bbox:
            return

        content_width = bbox[2] - bbox[0]
        visible_width = self.swatches_canvas.winfo_width()

        # If the content fits on the screen, set the scroll to the beginning and do not scroll
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

        # Only scroll if elements actually overflow the visible area
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

            # Left click to copy
            box.bind("<Button-1>", lambda e, c=hex_code: self._copy_to_clipboard(c))

            # Right click (<Button-3>) to delete
            box.bind("<Button-3>", lambda e, c=hex_code: self._remove_single_color(c))

            # Scroll if the pointer is over the squares
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
        
        # 1. Open the image first
        from PIL import Image
        self.current_original_img = Image.open(image_path).convert("RGB")

        # 2. Ensure geometric dimensions of the window
        self.update_idletasks()

        # 3. Render and adapt to the available size (this method already creates the image on the canvas)
        self._render_image_to_fit()

        # 4. Render the swatches palette
        self._render_swatches(project.get("palette", []))

    def _on_canvas_resize(self, event):
        """Scales again when the window is resized or maximized."""
        if self.current_original_img:
            self._render_image_to_fit()
    
    def _render_image_to_fit(self):
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        # Avoid calculations before Tkinter finishes mapping the window
        if c_w < 50 or c_h < 50:
            self.after(50, self._render_image_to_fit)
            return
        
        # Margin to avoid touching the edge of the card
        avail_w = max(20, c_w - 20)
        avail_h = max(20, c_h - 20)

        orig_w, orig_h = self.current_original_img.size
        ratio = min(avail_w / orig_w, avail_h / orig_h)

        new_w = max(1, int(orig_w * ratio))
        new_h = max(1, int(orig_h * ratio))

        # Pixel art/sprites or upscale: keep sharp edges with NEAREST
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

        # Calculate coordinates relative to the center of the image
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
        """Displays a minimalist peephole with real-time color and HEX."""
        if not self.loupe_enabled.get():
            return

        if not self.current_original_img or not self.current_tk_img:
            return

        bbox = self.canvas.bbox("main_img")
        if not bbox:
            self.canvas.delete("loupe")
            return        
        
        x1, y1, x2, y2 = bbox

        # If the cursor is inside the image
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            rel_x = event.x - x1
            rel_y = event.y - y1
            hex_color = color_engine.get_color_at_pixel(
                self.current_original_img, rel_x, rel_y, self.current_scale
            )

            # Floating position (offset up and to the right of the cursor)
            lx = event.x + 24
            ly = event.y - 24

            # Prevent it from overflowing from the canvas at the top or right
            c_w = self.canvas.winfo_width()
            if lx + 70 > c_w:
                lx = event.x - 70
            if ly - 20 < 0:
                ly = event.y + 24

            # Redraw the mini-pill
            self.canvas.delete("loupe")

            # 1. Dark/subtle background pickup
            self.canvas.create_rectangle(
                lx, ly - 14, lx + 76, ly + 14,
                fill="#1E201E",
                outline="#3A3D3A",
                width=1,
                tags="loupe"
            )

            # 2. Circle showing color swatch
            self.canvas.create_oval(
                lx + 5, ly - 7, lx + 19, ly + 7,
                fill=hex_color,
                outline="#FFFFFF",
                width=1,
                tags="loupe"
            )

            # 3. HEX code in fine text
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
        """Clears the peephole if the user deactivates it with the cursor over it."""
        if not self.loupe_enabled.get():
            self.canvas.delete("loupe")
    
    def _on_mouse_leave(self, event=None):
        """Hide the magnifying glass when the mouse leaves the canvas area."""
        self.canvas.delete("loupe")
    
    def _setup_dnd(self):
        # Register this frame to exclusively accept files
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_file_drop)

    def _on_dialog_close(self):
        self._is_dialog_open = False
        dialog.destroy()
    
    def _on_file_drop(self, event):
        if getattr(self, "_is_dialog_open", False):
            return

        filepath = event.data.strip()
        if filepath.startswith("{") and filepath.endswith("}"):
            filepath = filepath[1:-1]

        if self.on_file_dropped:
            self._is_dialog_open = True
            self.after(20, lambda path=filepath: self.on_file_dropped(path))