from docx import Document


def parse_docx(file_bytes: bytes) -> str:
    from io import BytesIO

    doc = Document(BytesIO(file_bytes))

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    return "\n\n".join(paragraphs)