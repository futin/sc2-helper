from pathlib import Path

from backend.hud.ocr import capture_region, _preprocess, ocr_number, ocr_supply
from backend.service import get_config


def test_ocr_mode() -> None:
    """Capture each configured region, save crops, print OCR results."""
    config = get_config()
    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)
    out_dir = Path(__file__).parent.parent / "ocr_debug"
    out_dir.mkdir(exist_ok=True)

    names = ["minerals", "gas", "supply", "idle_workers"]
    for name in names:
        region = sc[name]
        raw = capture_region(region)
        raw.save(out_dir / f"{name}_raw.png")

        processed = _preprocess(raw, threshold)
        processed.save(out_dir / f"{name}_processed.png")

        if name == "supply":
            result = ocr_supply(raw, threshold)
        else:
            result = ocr_number(raw, threshold)

        print(f"{name:15} region={region}  ocr={result}")

    print(f"\nCrops saved to {out_dir}/")
    print("Check *_raw.png to verify region placement.")
    print("Check *_processed.png to see what Tesseract receives.")
    print("If processed image looks wrong, adjust ocr_threshold in Settings → Configuration.")
