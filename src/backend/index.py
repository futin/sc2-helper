"""
SC2 Helper — captures the StarCraft II HUD via screen OCR and speaks audio warnings.

Endpoints used:
  GET http://localhost:6119/game   → game/player status only (no resource data)

Resource values (minerals, gas, supply, idle workers) are read via screen capture
and OCR from the HUD.

Run normally:
  python3 -m backend.index

Debug mode (runs main loop and prints HUD state each interval):
  python3 -m backend.index --debug

Test OCR mode (saves crops and prints OCR results for each HUD region):
  python3 -m backend.index --test-ocr
"""

import logging
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import mss as _mss
import pytesseract
import requests
import yaml
from PIL import Image, ImageOps

from backend.messages import get_message
from backend.stats import StatsManager

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

PRIORITY_SUPPLY = 0
PRIORITY_MINERALS = 1
PRIORITY_IDLE_WORKERS = 2
PRIORITY_GAS = 3

class SpeechQueue:
    def __init__(self) -> None:
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._counter = 0
        self._lock = threading.Lock()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        while True:
            _, _, message, voice = self._queue.get()
            cmd = ["say", "-v", voice, message] if voice else ["say", message]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._queue.task_done()

    def speak(self, message: str, voice: str = "", priority: int = 99) -> None:
        with self._lock:
            self._counter += 1
            counter = self._counter
        self._queue.put((priority, counter, message, voice))


# ---------------------------------------------------------------------------
# Game status check
# ---------------------------------------------------------------------------

def _poll_game() -> tuple[bool, list]:
    """Return (is_running, players). Single API call reused by main loop."""
    try:
        resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return False, []
        data = resp.json()
        players = data.get("players", [])
        running = any(p.get("result") == "Undecided" for p in players)
        return running, players
    except (requests.ConnectionError, requests.Timeout, ValueError):
        return False, []


def is_game_running() -> bool:
    """Return True if SC2 is running and a game is in progress."""
    running, _ = _poll_game()
    return running


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


# ---------------------------------------------------------------------------
# Game state fetch
# ---------------------------------------------------------------------------

def _capture_hud(config: dict) -> Optional[dict]:
    """Capture HUD via screen OCR. Assumes game is already confirmed running."""
    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)

    minerals = ocr_number(capture_region(sc["minerals"]), threshold, "minerals")
    gas = ocr_number(capture_region(sc["gas"]), threshold, "gas")
    supply_used, supply_max = ocr_supply(capture_region(sc["supply"]), threshold)
    idle_workers = ocr_number(capture_region(sc["idle_workers"]), threshold, "idle_workers") or 0

    return {
        "minerals": minerals,
        "gas": gas,
        "supply_used": supply_used,
        "supply_max": supply_max,
        "idle_workers": idle_workers,
    }


def _filter_spikes(state: dict, prev: Optional[dict], config: dict) -> dict:
    af = config.get("anomaly_filter", {})
    if not af.get("enabled", False) or prev is None:
        return state
    max_delta = af.get("max_delta", {})
    filtered = dict(state)
    for key in ("minerals", "gas", "supply_used", "supply_max"):
        new_val = state.get(key)
        prev_val = prev.get(key)
        limit = max_delta.get(key)
        if new_val is not None and prev_val is not None and limit is not None:
            if abs(new_val - prev_val) > limit:
                logging.debug("Spike filtered %s: %s → %s", key, prev_val, new_val)
                filtered[key] = prev_val
    return filtered


def fetch_game_state(config: dict) -> Optional[dict]:
    """Capture current game state via screen OCR. Returns None if game not running."""
    if not is_game_running():
        return None
    return _capture_hud(config)


_RESULT_MAP = {
    "Win": "Win", "Victory": "Win",
    "Loss": "Loss", "Defeat": "Loss",
    "Tie": "Tie",
}

_RACE_MAP = {
    "Prot": "Protoss", "Protoss": "Protoss",
    "Terr": "Terran",  "Terran": "Terran",
    "Zerg": "Zerg",
    "random": "Random", "Random": "Random",
}


def _extract_result(players: list, player_id: int) -> str:
    """Extract Win/Loss/Tie for player_id from an already-fetched players list."""
    idx = player_id - 1
    if 0 <= idx < len(players):
        result = _RESULT_MAP.get(players[idx].get("result", ""))
        if result:
            return result
    for p in players:
        result = _RESULT_MAP.get(p.get("result", ""))
        if result:
            return result
    return "Unknown"


def _extract_race(players: list, player_id: int) -> str:
    """Extract the player's race from the players list."""
    idx = player_id - 1
    if 0 <= idx < len(players):
        return _RACE_MAP.get(players[idx].get("race", ""), "Unknown")
    return "Unknown"



# ---------------------------------------------------------------------------
# Cooldown tracker
# ---------------------------------------------------------------------------

class CooldownTracker:
    def __init__(self):
        self._last: dict = {}

    def ready(self, key: str, seconds: float) -> bool:
        """Return True (and record the time) if the cooldown has elapsed."""
        now = time.monotonic()
        if key not in self._last or now - self._last[key] >= seconds:
            self._last[key] = now
            return True
        return False


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

def check_resources(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "StatsManager | None" = None,
) -> None:
    minerals = state["minerals"]
    gas = state["gas"]
    res_cfg = config["resources"]

    if minerals is not None and minerals > res_cfg["mineral_threshold"] and cooldown.ready("minerals", res_cfg["cooldown"]):
        speech.speak(get_message("minerals", mode, custom_messages), voice, PRIORITY_MINERALS)
        if stats:
            stats.on_mineral_warning()
    if gas is not None and gas > res_cfg["gas_threshold"] and cooldown.ready("gas", res_cfg["cooldown"]):
        speech.speak(get_message("gas", mode, custom_messages), voice, PRIORITY_GAS)
        if stats:
            stats.on_gas_warning()


def check_supply(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "StatsManager | None" = None,
) -> None:
    supply_used = state["supply_used"]
    supply_max = state["supply_max"]

    if supply_used is None or supply_max is None or supply_max == 0:
        return

    supply_cfg = config["supply"]
    gap = supply_max - supply_used

    warn_gap = None
    for tier in supply_cfg["tiers"]:
        if supply_max <= tier["max_cap"]:
            warn_gap = tier["gap"]
            break

    if warn_gap is not None and gap <= warn_gap and cooldown.ready("supply", supply_cfg["cooldown"]):
        speech.speak(get_message("supply", mode, custom_messages), voice, PRIORITY_SUPPLY)
        if stats:
            stats.on_supply_warning()


def check_idle_workers(
    state: dict,
    config: dict,
    cooldown: CooldownTracker,
    speech: SpeechQueue,
    voice: str,
    idle_onset: Optional[float],
    mode: str = "strict",
    custom_messages: dict | None = None,
    stats: "StatsManager | None" = None,
) -> Optional[float]:
    """Track idle workers. Returns updated idle_onset (or None if busy)."""
    idle_count = state["idle_workers"]
    workers_cfg = config["workers"]

    if idle_count is None or idle_count == 0:
        return None

    if idle_onset is None:
        idle_onset = time.monotonic()

    elapsed = time.monotonic() - idle_onset
    if elapsed >= workers_cfg["idle_seconds"] and cooldown.ready("workers", workers_cfg["cooldown"]):
        speech.speak(get_message("idle_workers", mode, custom_messages), voice, PRIORITY_IDLE_WORKERS)
        if stats:
            stats.on_idle_workers_warning()

    return idle_onset


# ---------------------------------------------------------------------------
# Test OCR mode
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


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def _format_debug_state(state: dict) -> str:
    def _v(val) -> str:
        return '?' if val is None else str(val)

    return (
        f"[DEBUG] minerals={_v(state['minerals'])}  gas={_v(state['gas'])}  "
        f"supply={_v(state['supply_used'])}/{_v(state['supply_max'])}  "
        f"idle_workers={_v(state['idle_workers'])}"
    )


def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return

    debug: bool = "--debug" in sys.argv

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    config = load_config(Path(__file__).parent / "config.yaml")
    voice: str = config.get("tts_voice", "")
    mode: str = config.get("message_mode", "strict")
    custom_messages: dict = config.get("custom_messages", {})
    cooldown = CooldownTracker()
    speech = SpeechQueue()
    stats = StatsManager()
    idle_onset: Optional[float] = None
    game_active: bool = False
    prev_state: Optional[dict] = None

    label = ", debug" if debug else ""
    logging.info("SC2 Helper running [%s mode%s]. Press Ctrl+C to stop.", mode, label)
    try:
        while True:
            running, players = _poll_game()

            if running and not game_active:
                game_active = True
                idle_onset = None
                prev_state = None
                stats.on_game_start()

            elif not running and game_active:
                player_id = config.get("player_id", 1)
                result = _extract_result(players, player_id)
                race = _extract_race(players, player_id)
                stats.on_game_end(result, race)
                game_active = False
                idle_onset = None
                prev_state = None

            if running:
                state = _capture_hud(config)
                if state:
                    state = _filter_spikes(state, prev_state, config)
                    prev_state = state
                if debug:
                    if state:
                        print(_format_debug_state(state), flush=True)
                    else:
                        print("[DEBUG] no HUD state (OCR failed)", flush=True)
                if state:
                    check_resources(state, config, cooldown, speech, voice, mode, custom_messages, stats)
                    check_supply(state, config, cooldown, speech, voice, mode, custom_messages, stats)
                    idle_onset = check_idle_workers(state, config, cooldown, speech, voice, idle_onset, mode, custom_messages, stats)
            elif debug:
                print("[DEBUG] no state (game not running)", flush=True)

            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
