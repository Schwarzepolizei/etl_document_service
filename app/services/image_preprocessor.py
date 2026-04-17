import io

import cv2
import numpy as np
from PIL import Image


def preprocess_image_for_ocr(file_bytes: bytes) -> Image.Image:
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image bytes")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    thresholded = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    pil_image = Image.fromarray(thresholded)
    return pil_image


def preprocess_pil_image_for_ocr(pil_image: Image.Image) -> Image.Image:
    image = np.array(pil_image)

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    thresholded = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return Image.fromarray(thresholded)