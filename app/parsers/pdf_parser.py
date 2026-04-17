import io
import pdfplumber


def parse_pdf(file_bytes: bytes) -> tuple[str, int, bool]:
    """
    Возвращает:
    full_text, page_count, has_text_layer
    """
    text_pages = []
    has_text_layer = False

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text and page_text.strip():
                has_text_layer = True
                text_pages.append(page_text)
            else:
                text_pages.append("")

        full_text = "\n\n".join(text_pages)
        page_count = len(pdf.pages)

    return full_text, page_count, has_text_layer