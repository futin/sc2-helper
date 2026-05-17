import logging
from typing import Optional

import requests

from backend.constants import SC2_BASE, REQUEST_TIMEOUT
from backend.ocr import capture_region, ocr_number, ocr_supply


def test_graphify() -> bool:
    return False

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
