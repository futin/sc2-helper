import logging
import queue
import re
import threading
from dataclasses import dataclass, field

from backend.sounds import play_boop

logger = logging.getLogger(__name__)


@dataclass
class VoiceCommand:
    intent: str
    params: dict = field(default_factory=dict)


class VoiceListener:
    def __init__(
        self,
        stt_backend: str,
        command_queue: queue.Queue,
        pause_threshold: float = 1.2,
        phrase_time_limit: int = 8,
        silence_default: int = 120,
        recalibrate_interval_s: float = 300.0,
        calibration_duration_s: float = 0.5,
    ):
        self._stt_backend = stt_backend
        self._queue = command_queue
        self._pause_threshold = pause_threshold
        self._phrase_time_limit = phrase_time_limit
        self._silence_default = silence_default
        self._recalibrate_interval_s = recalibrate_interval_s
        self._calibration_duration_s = calibration_duration_s
        self._recognizer = None
        self._mic_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._recalibrate_thread: threading.Thread | None = None

    def start(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
            return

        recognizer = sr.Recognizer()
        recognizer.pause_threshold = self._pause_threshold
        recognizer.dynamic_energy_threshold = False
        recognizer.non_speaking_duration = 0.2
        self._recognizer = recognizer
        self._calibrate()

        self._recalibrate_thread = threading.Thread(
            target=self._recalibrate_loop, daemon=True, name="VoiceListenerRecalibrate"
        )
        self._recalibrate_thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _calibrate(self) -> None:
        import speech_recognition as sr

        with self._mic_lock:
            try:
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(
                        source, duration=self._calibration_duration_s
                    )
                logger.debug(
                    "VoiceListener: calibrated energy_threshold=%.1f",
                    self._recognizer.energy_threshold,
                )
            except Exception as exc:
                logger.warning("VoiceListener: calibration failed: %s", exc)

    def _recalibrate_loop(self) -> None:
        while not self._stop_event.wait(self._recalibrate_interval_s):
            self._calibrate()

    def handle_wake(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
            return

        if self._recognizer is None:
            logger.error("VoiceListener: start() not called before handle_wake")
            return

        with self._mic_lock:
            with sr.Microphone() as source:
                logger.debug("VoiceListener: wake detected, listening for command...")
                try:
                    audio = self._recognizer.listen(
                        source, timeout=5, phrase_time_limit=self._phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    logger.debug("VoiceListener: no command heard after wake word")
                    play_boop()
                    return

        text = self._transcribe(self._recognizer, audio)
        if not text:
            play_boop()
            return

        logger.debug("VoiceListener heard: %r", text)
        cmd = self._parse_command(text)
        if cmd:
            self._queue.put(cmd)
            logger.debug("VoiceCommand queued: intent=%s params=%s", cmd.intent, cmd.params)
        else:
            logger.debug("VoiceListener: no matching command in %r", text)
            play_boop()

    def _transcribe(self, recognizer, audio) -> str | None:
        try:
            if self._stt_backend == "whisper":
                return recognizer.recognize_whisper(audio, language="english")
            return recognizer.recognize_google(audio)
        except Exception as exc:
            logger.warning("Transcription failed: %s", exc)
            return None

    def _parse_command(self, text: str) -> VoiceCommand | None:
        t = text.lower()

        if re.search(r"\bsupply\b", t):
            return VoiceCommand(intent="query_supply")

        if re.search(r"\b(resources|minerals|gas|enough)\b", t):
            return VoiceCommand(intent="query_resources")

        if re.search(r"\b(work|workers|idle workers)\b", t):
            return VoiceCommand(intent="query_workers")

        if re.search(r"\b(unmute|speak|enable sound)\b", t):
            return VoiceCommand(intent="unmute")

        silence_match = re.search(r"\bsilen(?:t|ce)\s+(?:for\s+)?(?:next\s+)?(\d+)\s*(minute|min|second|sec)", t)
        if silence_match or re.search(r"\b(silent|silence|quiet|mute)\b", t):
            seconds = self._silence_default
            if silence_match:
                amount = int(silence_match.group(1))
                unit = silence_match.group(2)
                seconds = amount * 60 if unit.startswith("min") else amount
            return VoiceCommand(intent="silence", params={"seconds": seconds})

        logger.debug("No matching intent for: %r", text)
        return None
