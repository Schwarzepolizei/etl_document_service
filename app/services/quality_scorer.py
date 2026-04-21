import re
from typing import Optional


def compute_text_noise_ratio(text: str) -> float:
    if not text.strip():
        return 1.0

    non_space_chars = [ch for ch in text if not ch.isspace()]
    if not non_space_chars:
        return 1.0

    bad_chars = sum(
        1 for ch in non_space_chars
        if not (ch.isalnum() or ch in ".,:;!?()[]%+-=/№\"'«»")
    )

    return round(bad_chars / len(non_space_chars), 4)
