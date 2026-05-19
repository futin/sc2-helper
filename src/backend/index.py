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
import sys
import time
from pathlib import Path
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue, WakeWordDetector
from backend.classes.voice_listener import VoiceListener
from backend.constants import PRIORITY_VOICE_RESPONSE
from backend.detectors import check_idle_workers, check_resources, check_supply
from backend.game_api import _capture_hud, _filter_spikes, _poll_game
from backend.logger import setup_logging
from backend.ocr import _preprocess, capture_region, ocr_number, ocr_supply
from backend.game_history import GameHistoryManager
from backend.service import get_config
from backend.utils import _extract_race, _extract_result, _format_debug_state


# ---------------------------------------------------------------------------
# Test OCR mode
# ---------------------------------------------------------------------------

def test_ocr_mode() -> None:
    """Capture each configured region, save crops, print OCR results."""
    config = get_config()
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
    print("If processed image looks wrong, adjust ocr_threshold in Settings → Configuration.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return

    debug: bool = "--debug" in sys.argv
    setup_logging(debug)

    config = get_config()
    voice: str = config.get("tts_voice", "")
    mode: str = config.get("message_mode", "strict")
    custom_messages: dict = config.get("custom_messages", {})
    voice_cfg: dict = config.get("voice_control", {})
    cooldown = CooldownTracker()
    speech = SpeechQueue()
    stats = GameHistoryManager()
    idle_onset: Optional[float] = None
    game_active: bool = False
    prev_state: Optional[dict] = None
    silence_until: float = 0.0
    current_state: Optional[dict] = None

    voice_queue: queue.Queue = queue.Queue()
    voice_listener: Optional[VoiceListener] = None
    detector: Optional[WakeWordDetector] = None
    if voice_cfg.get("enabled", False):
        voice_listener = VoiceListener(
            stt_backend=voice_cfg.get("stt_backend", "google"),
            command_queue=voice_queue,
            pause_threshold=float(voice_cfg.get("pause_threshold", 1.2)),
            phrase_time_limit=int(voice_cfg.get("phrase_time_limit", 8)),
            silence_default=int(voice_cfg.get("silence_duration", 120)),
        )
        detector = WakeWordDetector(
            model_name=voice_cfg.get("wake_word_model", "alexa"),
            sensitivity=float(voice_cfg.get("wake_sensitivity", 0.6)),
            on_wake=voice_listener.handle_wake,
        )
        detector.start()

    label = ", debug" if debug else ""
    logging.info("SC2 Helper running [%s mode%s]. Press Ctrl+C to stop.", mode, label)
    voice_on = "on" if voice_listener else "off"
    print(f"[STATE] game=idle voice={voice_on}", flush=True)
    try:
        while True:
            # --- drain voice commands ---
            while not voice_queue.empty():
                try:
                    cmd = voice_queue.get_nowait()
                except queue.Empty:
                    break
                _handle_voice_command(cmd, current_state, speech, voice, config, cooldown)
                if cmd.intent == "silence":
                    silence_until = time.monotonic() + cmd.params["seconds"]

            running, players = _poll_game()

            if running and not game_active:
                game_active = True
                idle_onset = None
                prev_state = None
                current_state = None
                stats.on_game_start()

            elif not running and game_active:
                player_id = config.get("player_id", 1)
                result = _extract_result(players, player_id)
                race = _extract_race(players, player_id)
                stats.on_game_end(result, race)
                game_active = False
                idle_onset = None
                prev_state = None
                current_state = None
                voice_on = "on" if voice_listener else "off"
                print(f"[STATE] game=idle voice={voice_on}", flush=True)

            if running:
                state = _capture_hud(config)
                if state:
                    state = _filter_spikes(state, prev_state, config)
                    prev_state = state
                    current_state = state
                if debug:
                    if state:
                        print(_format_debug_state(state), flush=True)
                    else:
                        print("[DEBUG] no HUD state (OCR failed)", flush=True)
                if state:
                    def _v(val):
                        return '?' if val is None else str(val)
                    c = stats.counts
                    res_cfg = config["resources"]
                    sup_cfg = config["supply"]
                    wkr_cfg = config["workers"]
                    silence_remaining = max(0.0, silence_until - time.monotonic())
                    voice_on = "on" if voice_listener else "off"
                    print(
                        f"[STATE] minerals={_v(state['minerals'])} gas={_v(state['gas'])}"
                        f" supply={_v(state['supply_used'])}/{_v(state['supply_max'])}"
                        f" idle={_v(state['idle_workers'])}"
                        f" mw={c.get('mineralWarningsCount', 0)}"
                        f" gw={c.get('gasWarningsCount', 0)}"
                        f" sw={c.get('supplyWarningsCount', 0)}"
                        f" iw={c.get('idleWorkersWarningsCount', 0)}"
                        f" cd_minerals={int(cooldown.remaining('minerals', res_cfg['cooldown']))}"
                        f" cd_gas={int(cooldown.remaining('gas', res_cfg['cooldown']))}"
                        f" cd_supply={int(cooldown.remaining('supply', sup_cfg['cooldown']))}"
                        f" cd_workers={int(cooldown.remaining('workers', wkr_cfg['cooldown']))}"
                        f" voice={voice_on}"
                        f" silence_remaining={int(silence_remaining)}",
                        flush=True,
                    )
                    silenced = time.monotonic() < silence_until
                    if not silenced:
                        check_resources(state, config, cooldown, speech, voice, mode, custom_messages, stats)
                        check_supply(state, config, cooldown, speech, voice, mode, custom_messages, stats)
                        idle_onset = check_idle_workers(state, config, cooldown, speech, voice, idle_onset, mode, custom_messages, stats)
            elif debug:
                print("[DEBUG] no state (game not running)", flush=True)

            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        speech.stop()
        if detector:
            detector.stop()  # VoiceListener is stateless — no stop() needed


def _handle_voice_command(cmd, state: Optional[dict], speech: SpeechQueue, voice: str, config: dict, cooldown: CooldownTracker) -> None:
    if cmd.intent == "query_supply":
        if state:
            used = state.get("supply_used", "?")
            max_ = state.get("supply_max", "?")
            speech.speak(f"Supply is {used} of {max_}.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "query_resources":
        if state:
            minerals = state.get("minerals", "?")
            gas = state.get("gas", "?")
            speech.speak(f"You have {minerals} minerals and {gas} gas.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "silence":
        seconds = cmd.params["seconds"]
        mins = seconds // 60
        speech.speak(f"Going silent for {mins} minute{'s' if mins != 1 else ''}.", voice, PRIORITY_VOICE_RESPONSE)


if __name__ == "__main__":
    main()
