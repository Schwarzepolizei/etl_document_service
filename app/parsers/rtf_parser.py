from striprtf.striprtf import rtf_to_text


def parse_rtf(file_bytes: bytes) -> str:
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text = file_bytes.decode("latin-1", errors="ignore")

    return rtf_to_text(text)