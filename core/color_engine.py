"""
Motor de procesamiento de imagen y extracción de color usando Pillow.
"""

from PIL import Image, ImageTk

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convierte tupla RGB a formato #RRGGBB en mayúsculas."""
    return f"#{r:02X}{g:02X}{b:02X}"


def load_and_scale_image(image_path: str, max_w: int, max_h: int):
    """
    Carga una imagen y calcula su escala óptima.
    - Si es menor que un tercio del canvas (ej. sprite 16x16), escala con NEAREST para no difuminar.
    - Si excede max_w o max_h, reduce proporcionalmente con LANCZOS.
    Retorna: (PIL.Image original en RGB, PIL.Image escalada, ImageTk.PhotoImage)
    """
    original = Image.open(image_path).convert("RGB")
    orig_w, orig_h = original.size

    scale = 1.0

    # Si es muy pequeña (sprites estilo 16x16, 32x32), aumentamos nítido
    if orig_w < 120 and orig_h < 120:
        factor_w = max_w // orig_w
        factor_h = max_h // orig_h
        zoom = max(1, min(factor_w, factor_h, 8))  # Hasta un máximo de 8x
        target_size = (orig_w * zoom, orig_h * zoom)
        scaled = original.resize(target_size, Image.Resampling.NEAREST)
        scale = zoom
    # Si excede el contenedor, la reducimos manteniendo proporción
    elif orig_w > max_w or orig_h > max_h:
        ratio = min(max_w / orig_w, max_h / orig_h)
        target_size = (int(orig_w * ratio), int(orig_h * ratio))
        scaled = original.resize(target_size, Image.Resampling.LANCZOS)
        scale = ratio
    else:
        scaled = original.copy()
        scale = 1.0

    tk_photo = ImageTk.PhotoImage(scaled)
    return original, scaled, tk_photo, scale


def get_color_at_pixel(original_image: Image.Image, click_x: int, click_y: int, scale: float) -> str:
    """
    Traduce las coordenadas del Canvas a las del pixel original y extrae el HEX.
    """
    if scale <= 0:
        return "#000000"

    orig_x = int(click_x / scale)
    orig_y = int(click_y / scale)

    width, height = original_image.size
    orig_x = max(0, min(orig_x, width - 1))
    orig_y = max(0, min(orig_y, height - 1))

    r, g, b = original_image.getpixel((orig_x, orig_y))[:3]
    return rgb_to_hex(r, g, b)


def extract_dominant_colors(original_image: Image.Image, num_colors: int = 8) -> list[str]:
    """
    Extrae los colores más representativos de la imagen usando cuantización Octree.
    Retorna una lista de cadenas HEX únicas ordenadas.
    """
    # Muestra pequeña para procesar instantáneamente sin freeze en la GUI
    thumb = original_image.copy()
    thumb.thumbnail((150, 150), Image.Resampling.NEAREST)

    quantized = thumb.quantize(colors=num_colors, method=Image.Quantize.FASTOCTREE)
    palette_raw = quantized.getpalette()

    colors = []
    for i in range(num_colors):
        r = palette_raw[i * 3]
        g = palette_raw[i * 3 + 1]
        b = palette_raw[i * 3 + 2]
        hex_val = rgb_to_hex(r, g, b)
        if hex_val not in colors:
            colors.append(hex_val)

    return colors