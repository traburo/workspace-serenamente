from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


WIDTH = 1080
HEIGHT = 1350
INK = "#153f36"
CREAM = "#fffaf4"
GOLD = "#bd8420"
FONT_PATH = Path(__file__).resolve().parents[1] / "static" / "fonts" / "DejaVuSans.ttf"


def carousel_copy(piece):
    theme = (piece.get("title") or "").replace("Carrusel", "").strip(" —-")
    theme = theme or "Una pausa también es avanzar"
    return [
        theme,
        "La sobrecarga no siempre se ve como una gran crisis.",
        "Puede sentirse como cansancio constante, incluso después de descansar.",
        "O como la sensación de que siempre queda algo pendiente.",
        "Hacer una pausa no elimina tus responsabilidades. Te permite mirarlas con más claridad.",
        piece.get("cta") or "Guárdalo para volver a esta idea cuando lo necesites.",
    ]


def _font(size, serif=False):
    candidates = [str(FONT_PATH), "DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrapped_lines(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_text_block(draw, text, box, font, fill, spacing=18):
    x, y, width, _height = box
    lines = _wrapped_lines(draw, text, font, width)
    line_height = font.size + spacing if hasattr(font, "size") else 52
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height


def render_carousel_slide(image_bytes, text, index, logo_bytes):
    with Image.open(BytesIO(image_bytes)) as source:
        background = ImageOps.fit(source.convert("RGB"), (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    background = ImageEnhance.Color(background).enhance(0.82)
    canvas = background.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if index == 0:
        draw.rounded_rectangle((55, 665, 1025, 1260), radius=34, fill=(255, 250, 244, 242))
        draw.rectangle((110, 735, 270, 746), fill=GOLD)
        _draw_text_block(draw, text, (110, 790, 850, 370), _font(72, serif=True), INK, 22)
        label = "UN MOMENTO PARA COMPRENDER"
    elif index == 5:
        draw.rounded_rectangle((55, 590, 1025, 1260), radius=34, fill=(21, 63, 54, 238))
        _draw_text_block(draw, text, (110, 720, 850, 360), _font(58, serif=True), CREAM, 22)
        label = "GUÁRDALO · COMPÁRTELO · VUELVE"
    else:
        draw.rounded_rectangle((55, 760, 1025, 1260), radius=34, fill=(255, 250, 244, 242))
        draw.rectangle((110, 830, 230, 841), fill=GOLD)
        _draw_text_block(draw, text, (110, 885, 850, 300), _font(52, serif=True), INK, 20)
        label = "SERENAMENTE"

    draw.text((72, 60), label, font=_font(24), fill=CREAM, stroke_width=1, stroke_fill=INK)
    draw.text((890, 60), f"{index + 1:02d} / 06", font=_font(22), fill=CREAM,
              stroke_width=1, stroke_fill=INK)
    canvas = Image.alpha_composite(canvas, overlay)

    with Image.open(BytesIO(logo_bytes)) as logo_source:
        logo = logo_source.convert("RGBA")
        logo.thumbnail((285, 235), Image.Resampling.LANCZOS)
    plate = Image.new("RGBA", (logo.width + 26, logo.height + 20), (255, 250, 244, 235))
    plate.alpha_composite(logo, (13, 10))
    canvas.alpha_composite(plate, (72, 112))

    output = BytesIO()
    canvas.convert("RGB").save(output, format="JPEG", quality=92, optimize=True)
    return output.getvalue()
