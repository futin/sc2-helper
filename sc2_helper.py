"""
SC2 Helper — captures the StarCraft II HUD via screen OCR and speaks audio warnings.

Endpoints used:
  GET http://localhost:6119/game   → game/player status only (no resource data)

Resource values (minerals, gas, supply, idle workers) are read via screen capture
and OCR from the HUD.

Run normally:
  python3 sc2_helper.py

Debug mode (prints raw JSON from /game endpoint and exits):
  python3 sc2_helper.py --debug

Calibrate mode (saves full screenshot to calibration.png for coordinate finding):
  python3 sc2_helper.py --calibrate
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import mss as _mss
import pytesseract
import requests
import yaml
from PIL import Image, ImageOps

SC2_BASE = "http://localhost:6119"
REQUEST_TIMEOUT = 1  # seconds


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------

def speak(message: str, voice: str = "") -> None:
    """Fire-and-forget macOS TTS. Non-blocking so the poll loop keeps running."""
    cmd = ["say", message]
    if voice:
        cmd = ["say", "-v", voice, message]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Game status check
# ---------------------------------------------------------------------------

def is_game_running() -> bool:
    """Return True if SC2 is running and a game is in progress."""
    try:
        resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return False
        data = resp.json()
        players = data.get("players", [])
        return any(p.get("result") == "Undecided" for p in players)
    except (requests.ConnectionError, requests.Timeout, ValueError):
        return False


# ---------------------------------------------------------------------------
# Screen capture helpers
# ---------------------------------------------------------------------------

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


def ocr_number(img: Image.Image, threshold: int = 100) -> Optional[int]:
    """OCR a single integer from a HUD region. Returns None on failure."""
    text = pytesseract.image_to_string(
        _preprocess(img, threshold),
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    ).strip()
    try:
        return int(text)
    except ValueError:
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
            return None, None
    return None, None


# ---------------------------------------------------------------------------
# Game state fetch
# ---------------------------------------------------------------------------

def fetch_game_state(config: dict) -> Optional[dict]:
    """Capture current game state via screen OCR. Returns None if game not running."""
    if not is_game_running():
        return None

    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)

    minerals = ocr_number(capture_region(sc["minerals"]), threshold)
    gas = ocr_number(capture_region(sc["gas"]), threshold)
    supply_used, supply_max = ocr_supply(capture_region(sc["supply"]), threshold)
    idle_workers = ocr_number(capture_region(sc["idle_workers"]), threshold) or 0
    print("minerals", minerals)
    print("gas", gas)
    print("supply_used", supply_used)
    print("supply_max", supply_max)
    print("idle_workers", idle_workers)
    # Skip this poll if any critical value failed OCR
    if any(v is None for v in [minerals, gas, supply_used, supply_max]):
        return None

    return {
        "minerals": minerals,
        "gas": gas,
        "supply_used": supply_used,
        "supply_max": supply_max,
        "idle_workers": idle_workers,
    }


# ---------------------------------------------------------------------------
# Cooldown tracker
# ---------------------------------------------------------------------------

class CooldownTracker:
    def __init__(self):
        self._last: dict = {}

    def ready(self, key: str, seconds: float) -> bool:
        """Return True (and record the time) if the cooldown has elapsed."""
        now = time.monotonic()
        if now - self._last.get(key, 0) >= seconds:
            self._last[key] = now
            return True
        return False


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

def check_resources(state: dict, config: dict, cooldown: CooldownTracker, voice: str) -> None:
    minerals = state["minerals"]
    gas = state["gas"]
    res_cfg = config["resources"]

    mineral_over = minerals > res_cfg["mineral_threshold"]
    gas_over = gas > res_cfg["gas_threshold"]

    if (mineral_over or gas_over) and cooldown.ready("resources", res_cfg["cooldown"]):
        if mineral_over:
            speak(f"Spend resources — minerals at {minerals}", voice)
        else:
            speak(f"Spend resources — gas at {gas}", voice)


def check_supply(state: dict, config: dict, cooldown: CooldownTracker, voice: str) -> None:
    supply_used = state["supply_used"]
    supply_max = state["supply_max"]

    if supply_max == 0:
        return  # avoid division by zero before game starts

    supply_cfg = config["supply"]
    if (supply_used / supply_max >= supply_cfg["threshold_pct"] and
            cooldown.ready("supply", supply_cfg["cooldown"])):
        speak(f"Supply almost full — {supply_used} of {supply_max}", voice)


def check_idle_workers(
    state: dict,
    config: dict,
    cooldown: CooldownTracker,
    voice: str,
    idle_onset: Optional[float],
) -> Optional[float]:
    """
    Track how long workers have been idle.

    Returns the updated idle_onset timestamp (or None if workers are busy).
    """
    idle_count = state["idle_workers"]
    workers_cfg = config["workers"]

    if idle_count == 0:
        return None  # reset onset

    # Workers are idle — record onset if not already tracking
    if idle_onset is None:
        idle_onset = time.monotonic()

    elapsed = time.monotonic() - idle_onset
    if elapsed >= workers_cfg["idle_seconds"] and cooldown.ready("workers", workers_cfg["cooldown"]):
        speak(f"{idle_count} idle workers", voice)

    return idle_onset


# ---------------------------------------------------------------------------
# Debug mode
# ---------------------------------------------------------------------------

def debug_mode() -> None:
    """Hit /game endpoint once, pretty-print the raw JSON, then exit."""
    print("=== DEBUG MODE ===")
    print(f"Hitting {SC2_BASE}/game ...\n")
    try:
        game_resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        print(f"Status: {game_resp.status_code}")
        print(json.dumps(game_resp.json(), indent=2))
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(f"Connection failed: {exc}")


# ---------------------------------------------------------------------------
# Calibrate mode
# ---------------------------------------------------------------------------

def _calculate_regions(w: int, h: int) -> dict:
    """
    Estimate SC2 HUD region positions from screen dimensions.
    Based on default UI scale layout ratios (1920x1080 reference).
    """
    bar_y = int(h * 0.950)
    bar_h = int(h * 0.026)
    reg_w = int(w * 0.047)
    return {
        "minerals":     [int(w * 0.711), bar_y, reg_w, bar_h],
        "gas":          [int(w * 0.759), bar_y, reg_w, bar_h],
        "supply":       [int(w * 0.807), bar_y, reg_w, bar_h],
        "idle_workers": [10, int(h * 0.898), 60, int(h * 0.032)],
        "ocr_threshold": 100,
    }


def _annotate(img: Image.Image, regions: dict) -> Image.Image:
    """Draw labelled rectangles on screenshot to show detected regions."""
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    colors = {
        "minerals": "#00BFFF",
        "gas":      "#00FF88",
        "supply":   "#FFAA00",
        "idle_workers": "#FF4444",
    }
    for name, region in regions.items():
        if name == "ocr_threshold":
            continue
        l, t, rw, rh = region
        color = colors.get(name, "#FFFFFF")
        draw.rectangle([l, t, l + rw, t + rh], outline=color, width=2)
        draw.text((l, t - 14), name, fill=color)
    return img


def calibrate_mode() -> None:
    """Auto-detect SC2 HUD regions from screen resolution and write to config.yaml."""
    print("Capturing screenshot...")
    with _mss.MSS() as sct:
        monitor = sct.monitors[1]
        raw = sct.grab(monitor)
        img = Image.frombytes("RGB", raw.size, raw.rgb)

    w, h = img.size
    print(f"Screen: {w}x{h}")

    regions = _calculate_regions(w, h)

    # Save annotated screenshot for verification
    annotated = _annotate(img.copy(), regions)
    cal_path = Path(__file__).parent / "calibration.png"
    annotated.save(cal_path)
    print(f"Saved annotated screenshot: {cal_path}")

    # Update config.yaml screen_capture section
    cfg_path = Path(__file__).parent / "config.yaml"
    config = load_config(cfg_path)
    config["screen_capture"] = regions
    with open(cfg_path, "w") as f:
        yaml.dump(config, f, default_flow_style=None, sort_keys=False)

    print("\nRegions written to config.yaml:")
    for name, val in regions.items():
        print(f"  {name}: {val}")
    print("\nOpen calibration.png to verify. Adjust config.yaml if boxes look off.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def test_ocr_mode() -> None:
    """Capture each configured region, save crops, print OCR results."""
    config = load_config(Path(__file__).parent / "config.yaml")
    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)
    out_dir = Path(__file__).parent / "ocr_debug"
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
    print("If processed image looks wrong, adjust ocr_threshold in config.yaml.")


def main() -> None:
    if "--debug" in sys.argv:
        debug_mode()
        return
    if "--calibrate" in sys.argv:
        calibrate_mode()
        return
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return

    config = load_config(Path(__file__).parent / "config.yaml")
    voice: str = config.get("tts_voice", "")
    cooldown = CooldownTracker()
    idle_onset: Optional[float] = None

    print("SC2 Helper running. Press Ctrl+C to stop.")
    try:
        while True:
            state = fetch_game_state(config)
            print(state)
            if state:
                check_resources(state, config, cooldown, voice)
                check_supply(state, config, cooldown, voice)
                idle_onset = check_idle_workers(state, config, cooldown, voice, idle_onset)
            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
