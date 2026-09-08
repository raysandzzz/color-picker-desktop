"""
Visual settings and constants for the Color Picker app.
Main theme: Pastel Sage/Mint Green.
"""

# Main window
APP_TITLE = "Color Picker"
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 650
MIN_WIDTH = 800
MIN_HEIGHT = 550

# Themes (light/dark)
THEMES = {
    "dark": {
        "bg": "#1e1e1e",             # Classic dark main background
        "sidebar": "#252526",        # Slightly different sidebar
        "card_bg": "#2d2d2d",        # Raised surfaces and containers
        "accent": "#4ec9b0",         # Signature teal/mint style accent
        "button": "#2e5c46",         # Comfortable green primary off button
        "button_2": "#3a3d41",       # Neutral secondary button
        "canvas_border": "#5af78e",  # Soft neon border (mint with subtle transparency)
        "text_main": "#d4d4d4",      # Standard readable main text
        "text_2": "#858585"          # Secondary/muted text
    },
    "light": {
        "bg": "#E9EFE9",             # soft background
        "sidebar": "#D8E2DC",        # sidebar background
        "card_bg": "#FFFFFF",        # White cards and containers background
        "accent" : "#99BC85",        # Accent for some specific button
        "button" : "#88AA74",        # Color primary buttons
        "button_2": "#C7D3C8",       # Color secondary buttons
        "canvas_border": "#B8C5B9",  # Canvas border color
        "text_main": "#2D3732",      # Main text
        "text_2" : "#6B7C72"         # Secondary texts
        }
}

# Font presets
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

# Image area restrictions
CANVAS_MAX_WIDTH = 580
CANVAS_MAX_HEIGHT = 380