import io

import fitz  
import pytesseract
from PIL import Image


def parse_scanned_pdf(file_bytes: bytes) -> tuple[list[str], int]:
    """
    OCR для scan PDF:
    - каждая страница рендерится в изображение
    - затем прогоняется через pytesseract

    Возвращает:
    page_texts, page_count
    """
    page_texts = []

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        if image.mode != "RGB":
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image, lang="rus+eng").strip()
        page_texts.append(text)

    page_count = len(page_texts)
    pdf.close()

    return page_texts, page_count