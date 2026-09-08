"""
Configuración visual y constantes para la aplicación Color Picker.
Tema: Pastel Sage / Mint Green.
"""

# Ventana principal
APP_TITLE = "Color Picker"
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 650
MIN_WIDTH = 800
MIN_HEIGHT = 550

# Temas (claro/oscuro)
THEMES = {
    "dark": {
        "bg": "#1e1e1e",             # Fondo principal oscuro clásico VS Code
        "sidebar": "#252526",        # Sidebar ligeramente diferenciada
        "card_bg": "#2d2d2d",        # Superficies y contenedores elevados
        "accent": "#4ec9b0",         # Acento estilo teal/menta característico
        "button": "#2e5c46",         # Botón primario verde apagado cómodo
        "button_2": "#3a3d41",       # Botón secundario neutro
        "canvas_border": "#5af78e", # Borde neón suave (menta con transparencia sutil)
        "text_main": "#d4d4d4",      # Texto principal estándar legible
        "text_2": "#858585"          # Texto secundario / muted
    },
    "light": {
        "bg": "#E9EFE9",             # Fondo suave
        "sidebar": "#D8E2DC",        # Fondo sidebar
        "card_bg": "#FFFFFF",        # Fondo tarjetas y contenedores blancos
        "accent" : "#99BC85",        # Acento para algun boton especifico
        "button" : "#88AA74",        # Color botones primarios
        "button_2": "#C7D3C8",       # Color botones secundarios
        "canvas_border": "#B8C5B9",  # Color borde del canvas
        "text_main": "#2D3732",      # Texto principal
        "text_2" : "#6B7C72"         # Textos secundarios
        }
}

# Fonts presets
FONT_PRESETS = {
    "panton": {
        "title": ("Panton-Trial", 15, "bold"),
        "subtitle": ("Panton-Trial", 10, "bold"),
        "normal": ("Panton-Trial", 9),
        "code": ("Consolas", 9, "bold"),
        "badge": ("Panton-Trial", 9),
        "inspector": ("Panton-Trial", 9)
    },
    "pixel": {
        "title": ("Determination", 15, "bold"),
        "subtitle": ("Determination", 10, "bold"),
        "normal": ("Determination", 9),
        "code": ("Consolas", 9, "bold"),
        "badge": ("Determination", 8),
        "inspector": ("Determination", 9)
    }
}

# Restricciones del área de imagen
CANVAS_MAX_WIDTH = 580
CANVAS_MAX_HEIGHT = 380