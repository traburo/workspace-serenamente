import base64
import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MAX_IMAGE_BYTES = 12 * 1024 * 1024


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes
    mime_type: str
    model: str


class ImageGenerationError(RuntimeError):
    pass


def compose_image_prompt(piece):
    direction = (piece.get("visual_direction") or "Imagen editorial humana y cotidiana").strip()
    objective = (piece.get("objective") or "Acompañar el mensaje con sensibilidad").strip()
    return (
        "Crea una imagen editorial vertical 4:5 para Instagram de Serenamente. "
        f"Objetivo comunicacional: {objective}. Dirección visual: {direction}. "
        "Público: mujeres adultas que viven sobrecarga. La imagen debe sentirse humana, "
        "cálida, sobria y profesional; evitar estética clínica, dramatización, perfección irreal, "
        "estereotipos de género y símbolos genéricos de wellness. Composición con aire suficiente "
        "para añadir texto posteriormente. No incluir palabras, logotipos, marcas de agua, menores "
        "ni representar a una persona real identificable."
    )


class NanoBananaImageService:
    def __init__(self, api_key, model="gemini-3.1-flash-lite-image", timeout=90):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @property
    def configured(self):
        return bool(self.api_key)

    def generate(self, prompt):
        if not self.api_key:
            raise ImageGenerationError("Nano Banana no está configurado. Falta GEMINI_API_KEY.")
        endpoint = (
            "https://generativelanguage.googleapis.com/v1/models/"
            f"{self.model}:generateContent"
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": "4:5"},
            },
        }).encode("utf-8")
        request = Request(
            endpoint, data=payload, method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read())
        except HTTPError as error:
            raise ImageGenerationError(f"Google rechazó la generación (HTTP {error.code}).") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ImageGenerationError("No fue posible completar la generación de imagen.") from error

        parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in reversed(parts):
            inline = part.get("inlineData") or part.get("inline_data")
            if not inline or not inline.get("data"):
                continue
            mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            if mime_type not in {"image/png", "image/jpeg", "image/webp"}:
                raise ImageGenerationError("Google devolvió un formato de imagen no permitido.")
            try:
                data = base64.b64decode(inline["data"], validate=True)
            except ValueError as error:
                raise ImageGenerationError("La imagen generada llegó dañada.") from error
            if not data or len(data) > MAX_IMAGE_BYTES:
                raise ImageGenerationError("La imagen generada está vacía o supera 12 MB.")
            return GeneratedImage(data=data, mime_type=mime_type, model=self.model)
        raise ImageGenerationError("Google no devolvió una imagen utilizable.")
