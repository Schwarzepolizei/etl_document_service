import io

from PIL import Image
import pytesseract


def parse_image(file_bytes: bytes) -> tuple[str, bool]:
    image = Image.open(io.BytesIO(file_bytes))

    if image.mode != "RGB":
        image = image.convert("RGB")

    text = pytesseract.image_to_string(image, lang="rus+eng")
    text = text.strip()

    has_text = bool(text)
    return text, has_text