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
import sys
import time
from pathlib import Path
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.detectors import check_idle_workers, check_resources, check_supply
from backend.game_api import _capture_hud, _filter_spikes, _poll_game
from backend.logger import setup_logging
from backend.ocr import _preprocess, capture_region, ocr_number, ocr_supply
from backend.stats import StatsManager
from backend.utils import _extract_race, _extract_result, _format_debug_state, load_config


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

def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return

    debug: bool = "--debug" in sys.argv
    setup_logging(debug)

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
    print("[STATE] game=idle", flush=True)
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
                print("[STATE] game=idle", flush=True)

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
                    def _v(val):
                        return '?' if val is None else str(val)
                    c = stats.counts
                    print(
                        f"[STATE] minerals={_v(state['minerals'])} gas={_v(state['gas'])}"
                        f" supply={_v(state['supply_used'])}/{_v(state['supply_max'])}"
                        f" idle={_v(state['idle_workers'])}"
                        f" mw={c.get('mineralWarningsCount', 0)}"
                        f" gw={c.get('gasWarningsCount', 0)}"
                        f" sw={c.get('supplyWarningsCount', 0)}"
                        f" iw={c.get('idleWorkersWarningsCount', 0)}",
                        flush=True,
                    )
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
