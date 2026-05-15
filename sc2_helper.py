"""
SC2 Helper — polls the StarCraft II game client API and speaks audio warnings.

Endpoints used:
  GET http://localhost:6119/game   → mineral/gas/supply data
  GET http://localhost:6119/ui     → idle worker alerts

Run normally:
  python3 sc2_helper.py

Debug mode (prints raw JSON from both endpoints and exits):
  python3 sc2_helper.py --debug
"""

import json
import subprocess
import sys
import time
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
    subprocess.Popen(cmd)


# ---------------------------------------------------------------------------
# Game state fetch
# ---------------------------------------------------------------------------

def fetch_game_state(player_id: int) -> Optional[dict]:
    """
    Poll /game and /ui endpoints.

    Returns a dict with:
        minerals, gas, supply_used, supply_max  (from /game)
        idle_workers                             (from /ui)

    Returns None if SC2 is not running or either endpoint fails.

    NOTE on SC2 API schema:
      /game  — resource data lives under players[player_id - 1].  Known keys
               include "minerals" and "vespene" (gas).  Supply is typically
               "food_used" / "food_cap" (Blizzard API names).  We try both
               common variants and fall back to 0 so the script doesn't crash
               if field names differ.
      /ui    — idle worker count is reported in activeAlerts as an alert with
               workerType set.  A simpler shortcut is the top-level
               "activeAlerts" list; we look for any entry with a numeric count.
               The value may also appear directly as "idleWorkerCount" on the
               root object depending on API version.
    """
    try:
        game_resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        ui_resp = requests.get(f"{SC2_BASE}/ui", timeout=REQUEST_TIMEOUT)
    except (requests.ConnectionError, requests.Timeout):
        return None

    if game_resp.status_code != 200 or ui_resp.status_code != 200:
        return None

    game_data = game_resp.json()
    ui_data = ui_resp.json()

    # --- /game: resource and supply ---
    # Player list is 0-indexed; player_id is 1-indexed.
    players = game_data.get("players", [])
    player_index = player_id - 1
    player = players[player_index] if player_index < len(players) else {}

    minerals = int(player.get("minerals", 0))
    # "vespene" is the canonical Blizzard name; fall back to "gas"
    gas = int(player.get("vespene", player.get("gas", 0)))
    # Blizzard uses "foodUsed"/"foodCap"; community APIs sometimes use
    # "supply_used"/"supply_max" — try both.
    supply_used = int(
        player.get("foodUsed", player.get("food_used", player.get("supply_used", 0)))
    )
    supply_max = int(
        player.get("foodCap", player.get("food_cap", player.get("supply_max", 0)))
    )

    # --- /ui: idle workers ---
    # Strategy 1: top-level "idleWorkerCount" field (some API versions)
    idle_workers = int(ui_data.get("idleWorkerCount", 0))

    # Strategy 2: scan activeAlerts for a worker-idle entry
    if idle_workers == 0:
        for alert in ui_data.get("activeAlerts", []):
            # Alert objects vary; look for a numeric "count" on worker alerts.
            if isinstance(alert, dict) and alert.get("alertType", "").lower() in (
                "idleworker", "idle_worker", "worker"
            ):
                idle_workers = int(alert.get("count", 1))
                break

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
    """Hit both endpoints once, pretty-print the raw JSON, then exit."""
    print("=== DEBUG MODE ===")
    print(f"Hitting {SC2_BASE}/game ...\n")
    try:
        game_resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        print(f"Status: {game_resp.status_code}")
        print(json.dumps(game_resp.json(), indent=2))
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(f"Connection failed: {exc}")

    print(f"\nHitting {SC2_BASE}/ui ...\n")
    try:
        ui_resp = requests.get(f"{SC2_BASE}/ui", timeout=REQUEST_TIMEOUT)
        print(f"Status: {ui_resp.status_code}")
        print(json.dumps(ui_resp.json(), indent=2))
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(f"Connection failed: {exc}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    if "--debug" in sys.argv:
        debug_mode()
        return

    config = load_config("config.yaml")
    voice: str = config.get("tts_voice", "")
    cooldown = CooldownTracker()
    idle_onset: Optional[float] = None

    print("SC2 Helper running. Press Ctrl+C to stop.")
    try:
        while True:
            state = fetch_game_state(config["player_id"])
            if state:
                check_resources(state, config, cooldown, voice)
                check_supply(state, config, cooldown, voice)
                idle_onset = check_idle_workers(state, config, cooldown, voice, idle_onset)
            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")


if __name__ == "__main__":
    main()
