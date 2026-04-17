import io

from PIL import Image
import pytesseract

from app.services.image_preprocessor import preprocess_image_for_ocr


def parse_image(file_bytes: bytes) -> tuple[str, bool]:
    image = preprocess_image_for_ocr(file_bytes)

    text = pytesseract.image_to_string(
        image,
        lang="rus+eng",
        config="--oem 3 --psm 6"
    ).strip()

    has_text = bool(text)
    return text, has_text