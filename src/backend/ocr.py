import logging
from typing import Optional

import mss as _mss
import pytesseract
from PIL import Image, ImageOps


def capture_region(region: list) -> Image.Image:
    """Capture a screen region. region = [left, top, width, height]."""
    left, top, width, height = region
    with _mss.MSS() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.rgb)


def _preprocess(img: Image.Image, threshold: int) -> Image.Image:
    img = img.resize((img.width * 3, img.height * 3), resample=Image.LANCZOS)
    img = ImageOps.grayscale(img)
    return img.point(lambda x: 255 if x > threshold else 0)


def ocr_number(img: Image.Image, threshold: int = 100, region_name: str = "unknown") -> Optional[int]:
    """OCR a single integer from a HUD region. Returns None on failure."""
    text = pytesseract.image_to_string(
        _preprocess(img, threshold),
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    ).strip()
    if text == '':
        return 0
    try:
        return int(text)
    except ValueError:
        logging.warning("OCR failed for %s (got %r)", region_name, text)
        return None


def ocr_supply(img: Image.Image, threshold: int = 100) -> tuple:
    """OCR supply region. Returns (used, max) or (None, None) on failure."""
    text = pytesseract.image_to_string(
        _preprocess(img, threshold),
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789/"
    ).strip()
    if "/" in text:
        parts = text.split("/")
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            logging.warning("OCR failed for supply (got %r)", text)
            return None, None
    logging.warning("OCR failed for supply — no '/' in %r", text)
    return None, None
