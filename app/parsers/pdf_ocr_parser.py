import io

import fitz
import pytesseract
from PIL import Image

from app.services.image_preprocessor import preprocess_pil_image_for_ocr


def parse_scanned_pdf(file_bytes: bytes) -> tuple[list[str], int]:
    page_texts = []

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        pix = page.get_pixmap(dpi=250)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        if image.mode != "RGB":
            image = image.convert("RGB")

        processed_image = preprocess_pil_image_for_ocr(image)

        text = pytesseract.image_to_string(
            processed_image,
            lang="rus+eng",
            config="--oem 3 --psm 6"
        ).strip()

        page_texts.append(text)

    page_count = len(page_texts)
    pdf.close()

    return page_texts, page_count