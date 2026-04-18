import pytesseract
from pytesseract import Output


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