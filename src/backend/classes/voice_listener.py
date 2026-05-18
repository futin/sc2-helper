import logging
import queue
import re
from dataclasses import dataclass, field

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
    ):
        self._stt_backend = stt_backend
        self._queue = command_queue
        self._pause_threshold = pause_threshold
        self._phrase_time_limit = phrase_time_limit

    def handle_wake(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
            return

        recognizer = sr.Recognizer()
        recognizer.pause_threshold = self._pause_threshold

        with sr.Microphone() as source:
            logger.info("VoiceListener: wake detected, listening for command...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=self._phrase_time_limit)
            except sr.WaitTimeoutError:
                logger.info("VoiceListener: no command heard after wake word")
                return

        text = self._transcribe(recognizer, audio)
        if not text:
            return

        logger.info("VoiceListener heard: %r", text)
        cmd = self._parse_command(text)
        if cmd:
            self._queue.put(cmd)
            logger.info("VoiceCommand queued: intent=%s params=%s", cmd.intent, cmd.params)
        else:
            logger.info("VoiceListener: no matching command in %r", text)

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

        if any(kw in t for kw in ("supply", "supply status", "supply cap")):
            return VoiceCommand(intent="query_supply")

        if any(kw in t for kw in ("resources", "minerals", "gas", "enough")):
            return VoiceCommand(intent="query_resources")

        silence_match = re.search(r"silen(?:t|ce)\s+(?:for\s+)?(?:next\s+)?(\d+)\s*(minute|min|second|sec)", t)
        if silence_match or any(kw in t for kw in ("silent", "silence", "quiet", "mute")):
            seconds = 120
            if silence_match:
                amount = int(silence_match.group(1))
                unit = silence_match.group(2)
                seconds = amount * 60 if unit.startswith("min") else amount
            return VoiceCommand(intent="silence", params={"seconds": seconds})

        logger.debug("No matching intent for: %r", text)
        return None
