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

import requests
import yaml

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

def capture_region(region: list) -> "PIL.Image.Image":
    """Capture a screen region. region = [left, top, width, height]."""
    import mss
    from PIL import Image
    left, top, width, height = region
    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def ocr_number(img: "PIL.Image.Image") -> Optional[int]:
    """OCR a single integer from a HUD region. Returns None on failure."""
    import pytesseract
    from PIL import Image, ImageOps
    # Upscale 3x for better accuracy on small HUD text
    img = img.resize((img.width * 3, img.height * 3), resample=Image.LANCZOS)
    img = ImageOps.grayscale(img)
    # Threshold: HUD numbers are bright on dark background
    img = img.point(lambda x: 255 if x > 100 else 0)
    text = pytesseract.image_to_string(
        img,
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    ).strip()
    try:
        return int(text)
    except ValueError:
        return None


def ocr_supply(img: "PIL.Image.Image") -> tuple:
    """OCR supply region. Returns (used, max) or (None, None) on failure."""
    import pytesseract
    from PIL import Image, ImageOps
    img = img.resize((img.width * 3, img.height * 3), resample=Image.LANCZOS)
    img = ImageOps.grayscale(img)
    img = img.point(lambda x: 255 if x > 100 else 0)
    text = pytesseract.image_to_string(
        img,
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

    minerals = ocr_number(capture_region(sc["minerals"]))
    gas = ocr_number(capture_region(sc["gas"]))
    supply_used, supply_max = ocr_supply(capture_region(sc["supply"]))
    idle_workers = ocr_number(capture_region(sc["idle_workers"])) or 0

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

def calibrate_mode() -> None:
    """Take a full screenshot and save it for HUD coordinate identification."""
    import mss
    from PIL import Image
    print("Capturing full screenshot...")
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        raw = sct.grab(monitor)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    path = Path(__file__).parent / "calibration.png"
    img.save(path)
    print(f"Saved: {path}")
    print()
    print("Open calibration.png in Preview (Tools > Show Inspector shows pixel coords).")
    print("Find each HUD element and update screen_capture regions in config.yaml:")
    print("  minerals:     [left, top, width, height]")
    print("  gas:          [left, top, width, height]")
    print("  supply:       [left, top, width, height]   # shows 'used/max'")
    print("  idle_workers: [left, top, width, height]   # bottom-left icon area")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    if "--debug" in sys.argv:
        debug_mode()
        return
    if "--calibrate" in sys.argv:
        calibrate_mode()
        return

    config = load_config(Path(__file__).parent / "config.yaml")
    voice: str = config.get("tts_voice", "")
    cooldown = CooldownTracker()
    idle_onset: Optional[float] = None

    print("SC2 Helper running. Press Ctrl+C to stop.")
    try:
        while True:
            state = fetch_game_state(config)
            if state:
                check_resources(state, config, cooldown, voice)
                check_supply(state, config, cooldown, voice)
                idle_onset = check_idle_workers(state, config, cooldown, voice, idle_onset)
            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
