import logging
import queue
import time
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.game_history import GameHistoryManager
from backend.hud.api import _capture_hud, _filter_spikes, _poll_game
from backend.utils import _extract_race, _extract_result, _format_debug_state
from backend.voice.commands import handle_command
from backend.voice.listener import VoiceListener
from backend.voice.wake_word import WakeWordDetector
from backend.warnings.detectors import check_idle_workers, check_resources, check_supply


class GameRunner:
    def __init__(self, config: dict, debug: bool) -> None:
        self.config = config
        self.debug = debug
        self.cooldown = CooldownTracker()
        self.speech = SpeechQueue()
        self.stats = GameHistoryManager()
        self.game_active: bool = False
        self.prev_state: Optional[dict] = None
        self.current_state: Optional[dict] = None
        self.silence_until: float = 0.0
        self.idle_onset: Optional[float] = None
        self.voice_queue: queue.Queue = queue.Queue()
        self.voice_listener: Optional[VoiceListener] = None
        self.detector: Optional[WakeWordDetector] = None

    def setup_voice(self) -> None:
        voice_cfg = self.config.get("voice_control", {})
        if not voice_cfg.get("enabled", False):
            return
        self.voice_listener = VoiceListener(
            stt_backend=voice_cfg.get("stt_backend", "google"),
            command_queue=self.voice_queue,
            pause_threshold=float(voice_cfg.get("pause_threshold", 1.2)),
            phrase_time_limit=int(voice_cfg.get("phrase_time_limit", 8)),
            silence_default=int(voice_cfg.get("silence_duration", 120)),
        )
        self.voice_listener.start()
        self.detector = WakeWordDetector(
            model_name=voice_cfg.get("wake_word_model", "alexa"),
            sensitivity=float(voice_cfg.get("wake_sensitivity", 0.6)),
            on_wake=self.voice_listener.handle_wake,
        )
        self.detector.start()

    def _drain_voice_commands(self) -> None:
        voice = self.config.get("tts_voice", "")
        while not self.voice_queue.empty():
            try:
                cmd = self.voice_queue.get_nowait()
            except queue.Empty:
                break
            handle_command(cmd, self.current_state, self.speech, voice, self.config, self.cooldown)
            if cmd.intent == "silence":
                self.silence_until = time.monotonic() + cmd.params["seconds"]
            elif cmd.intent == "unmute":
                self.silence_until = 0.0

    def _on_game_start(self) -> None:
        self.game_active = True
        self.idle_onset = None
        self.prev_state = None
        self.current_state = None
        self.stats.on_game_start()

    def _on_game_end(self, players: list) -> None:
        player_id = self.config.get("player_id", 1)
        result = _extract_result(players, player_id)
        race = _extract_race(players, player_id)
        self.stats.on_game_end(result, race)
        self.game_active = False
        self.idle_onset = None
        self.prev_state = None
        self.current_state = None
        voice_on = "on" if self.voice_listener else "off"
        print(f"[STATE] game=idle voice={voice_on}", flush=True)

    def _tick(self, running: bool) -> None:
        if not running:
            if self.debug:
                print("[DEBUG] no state (game not running)", flush=True)
            return

        state = _capture_hud(self.config)
        if state:
            state = _filter_spikes(state, self.prev_state, self.config)
            self.prev_state = state
            self.current_state = state

        if self.debug:
            if state:
                print(_format_debug_state(state), flush=True)
            else:
                print("[DEBUG] no HUD state (OCR failed)", flush=True)

        if not state:
            return

        def _v(val):
            return '?' if val is None else str(val)

        c = self.stats.counts
        res_cfg = self.config["resources"]
        sup_cfg = self.config["supply"]
        wkr_cfg = self.config["workers"]
        silence_remaining = max(0.0, self.silence_until - time.monotonic())
        voice_on = "on" if self.voice_listener else "off"
        print(
            f"[STATE] minerals={_v(state['minerals'])} gas={_v(state['gas'])}"
            f" supply={_v(state['supply_used'])}/{_v(state['supply_max'])}"
            f" idle={_v(state['idle_workers'])}"
            f" mw={c.get('mineralWarningsCount', 0)}"
            f" gw={c.get('gasWarningsCount', 0)}"
            f" sw={c.get('supplyWarningsCount', 0)}"
            f" iw={c.get('idleWorkersWarningsCount', 0)}"
            f" cd_minerals={int(self.cooldown.remaining('minerals', res_cfg['cooldown']))}"
            f" cd_gas={int(self.cooldown.remaining('gas', res_cfg['cooldown']))}"
            f" cd_supply={int(self.cooldown.remaining('supply', sup_cfg['cooldown']))}"
            f" cd_workers={int(self.cooldown.remaining('workers', wkr_cfg['cooldown']))}"
            f" voice={voice_on}"
            f" silence_remaining={int(silence_remaining)}",
            flush=True,
        )

        silenced = time.monotonic() < self.silence_until
        if not silenced:
            voice = self.config.get("tts_voice", "")
            mode = self.config.get("message_mode", "strict")
            custom_messages = self.config.get("custom_messages", {})
            check_resources(state, self.config, self.cooldown, self.speech, voice, mode, custom_messages, self.stats)
            check_supply(state, self.config, self.cooldown, self.speech, voice, mode, custom_messages, self.stats)
            self.idle_onset = check_idle_workers(
                state, self.config, self.cooldown, self.speech, voice, self.idle_onset, mode, custom_messages, self.stats
            )

    def run(self) -> None:
        self.setup_voice()
        mode = self.config.get("message_mode", "strict")
        label = ", debug" if self.debug else ""
        logging.info("SC2 Helper running [%s mode%s]. Press Ctrl+C to stop.", mode, label)
        voice_on = "on" if self.voice_listener else "off"
        print(f"[STATE] game=idle voice={voice_on}", flush=True)
        try:
            while True:
                self._drain_voice_commands()
                running, players = _poll_game()
                if running and not self.game_active:
                    self._on_game_start()
                elif not running and self.game_active:
                    self._on_game_end(players)
                self._tick(running)
                time.sleep(self.config["poll_interval"])
        except KeyboardInterrupt:
            print("Stopping.")
        finally:
            self.stop()

    def stop(self) -> None:
        self.speech.stop()
        if self.detector:
            self.detector.stop()
