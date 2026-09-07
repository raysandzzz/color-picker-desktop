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
        "bg": "#E9EFE9",             # Fondo suave
        "sidebar": "#D8E2DC",        # Fondo sidebar
        "card_bg": "#FFFFFF",        # Fondo tarjetas y contenedores blancos
        "accent" : "#99BC85",        # Acento para algun boton especifico
        "button" : "#88AA74",        # Color botones primarios
        "button_2": "#C7D3C8",       # Color botones secundarios
        "canvas_border": "#B8C5B9",  # Color borde del canvas
        "text_main": "#2D3732",      # Texto principal
        "text_2" : "#6B7C72"         # Textos secundarios
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
    "segoe": {
        "title": ("Segoe UI", 15, "bold"),
        "subtitle": ("Segoe UI", 10, "bold"),
        "normal": ("Segoe UI", 9),
        "code": ("Consolas", 9, "bold"),
        "badge": ("Segoe UI", 8),
    },
    "pixel": {
        "title": ("Minecraft", 15, "bold"),
        "subtitle": ("Minecraft", 10, "bold"),
        "normal": ("Minecraft", 9),
        "code": ("Consolas", 9, "bold"),
        "badge": ("Minecraft", 8)
    }
}

# Restricciones del área de imagen
CANVAS_MAX_WIDTH = 580
CANVAS_MAX_HEIGHT = 380