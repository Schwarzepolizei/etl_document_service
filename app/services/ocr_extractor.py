import re

import pytesseract
from pytesseract import Output

from app.schemas.document import Block, BBox


def extract_ocr_data(image, lang: str = "rus+eng", config: str = "--oem 3 --psm 6") -> list[dict]:
    data = pytesseract.image_to_data(
        image,
        lang=lang,
        config=config,
        output_type=Output.DICT
    )

    n = len(data["text"])
    results = []

    for i in range(n):
        text = data["text"][i].strip()

        if not text:
            continue

        conf_raw = data["conf"][i]
        try:
            conf = float(conf_raw)
        except (ValueError, TypeError):
            conf = -1.0

        if conf < 0:
            continue

        results.append(
            {
                "text": text,
                "conf": conf,
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "block_num": int(data["block_num"][i]),
                "par_num": int(data["par_num"][i]),
                "line_num": int(data["line_num"][i]),
                "word_num": int(data["word_num"][i]),
            }
        )

    return results

def build_text_from_ocr_data(ocr_data: list[dict]) -> str:
    if not ocr_data:
        return ""

    lines = {}
    for item in ocr_data:
        key = (item["block_num"], item["par_num"], item["line_num"])
        lines.setdefault(key, []).append(item)

    ordered_lines = []
    for key in sorted(lines.keys()):
        words = sorted(lines[key], key=lambda x: x["word_num"])
        line_text = " ".join(word["text"] for word in words if word["text"].strip())
        if line_text.strip():
            ordered_lines.append(line_text)

    return "\n".join(ordered_lines)


def compute_average_confidence(ocr_data: list[dict]) -> float | None:
    if not ocr_data:
        return None

    confs = [item["conf"] for item in ocr_data if item["conf"] >= 0]
    if not confs:
        return None

    return round(sum(confs) / len(confs), 2)

def build_ocr_line_blocks(ocr_data: list[dict], page_num: int = 1, start_block_index: int = 1) -> list[Block]:
    if not ocr_data:
        return []

    lines = {}
    for item in ocr_data:
        key = (item["block_num"], item["par_num"], item["line_num"])
        lines.setdefault(key, []).append(item)

    blocks = []
    block_index = start_block_index

    for key in sorted(lines.keys()):
        words = sorted(lines[key], key=lambda x: x["word_num"])

        texts = [w["text"] for w in words if w["text"].strip()]
        if not texts:
            continue

        line_text = " ".join(texts).strip()
        if not line_text:
            continue

        x1 = min(w["left"] for w in words)
        y1 = min(w["top"] for w in words)
        x2 = max(w["left"] + w["width"] for w in words)
        y2 = max(w["top"] + w["height"] for w in words)

        confs = [w["conf"] for w in words if w["conf"] >= 0]
        avg_conf = round(sum(confs) / len(confs), 2) if confs else None

        blocks.append(
            Block(
                block_id=f"b{block_index}",
                page_num=page_num,
                block_order=block_index,
                block_type="ocr_line",
                text=line_text,
                bbox=BBox(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                ),
                confidence=avg_conf,
            )
        )

        block_index += 1

    return blocks

def is_noise_text(text: str) -> bool:
    text = text.strip()

    if not text:
        return True

    if len(text) <= 1:
        return True

    letters_or_digits = sum(ch.isalnum() for ch in text)
    non_space_chars = sum(not ch.isspace() for ch in text)

    if non_space_chars == 0:
        return True

    ratio = letters_or_digits / non_space_chars

    if ratio < 0.4:
        return True

    if re.fullmatch(r"[\W_]+", text):
        return True

    return False


def filter_ocr_data(
    ocr_data: list[dict],
    min_conf: float = 35.0,
    min_text_len: int = 2,
) -> list[dict]:
    filtered = []

    for item in ocr_data:
        text = item["text"].strip()
        conf = item["conf"]

        if not text:
            continue

        if conf < min_conf:
            continue

        if len(text) < min_text_len and not text.isdigit():
            continue

        if is_noise_text(text):
            continue

        filtered.append(item)

    return filtered