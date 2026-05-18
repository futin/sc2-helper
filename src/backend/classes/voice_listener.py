"""
Voice listener — background thread that listens for a wake word then transcribes
a follow-up command and enqueues a VoiceCommand for the main loop.

Requires: pip install SpeechRecognition pyaudio
Optional offline backend: pip install openai-whisper
"""

import logging
import queue
import re
import threading
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class VoiceCommand:
    intent: str
    params: dict = field(default_factory=dict)


class VoiceListener:
    def __init__(
        self,
        wake_word: str,
        stt_backend: str,
        command_queue: queue.Queue,
        pause_threshold: float = 1.2,
        phrase_threshold: float = 0.3,
        non_speaking_duration: float = 0.4,
        phrase_time_limit: int = 8,
    ):
        self._wake_word = wake_word.lower()
        self._stt_backend = stt_backend
        self._queue = command_queue
        self._pause_threshold = pause_threshold
        self._phrase_threshold = phrase_threshold
        self._non_speaking_duration = non_speaking_duration
        self._phrase_time_limit = phrase_time_limit
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="VoiceListener")
        self._thread.start()
        logger.info("VoiceListener started (wake_word=%r, backend=%s)", self._wake_word, self._stt_backend)

    def stop(self) -> None:
        self._stop_event.set()

    def _listen_loop(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio")
            return

        recognizer = sr.Recognizer()
        recognizer.pause_threshold = self._pause_threshold
        recognizer.phrase_threshold = self._phrase_threshold
        recognizer.non_speaking_duration = self._non_speaking_duration

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info(
                "VoiceListener ready, listening for %r (pause=%.1fs, phrase_limit=%ds)...",
                self._wake_word, self._pause_threshold, self._phrase_time_limit,
            )

            while not self._stop_event.is_set():
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=self._phrase_time_limit)
                    logger.info("VoiceListener: audio captured, transcribing...")
                    text = self._transcribe(recognizer, audio)
                    if text:
                        logger.info("VoiceListener heard: %r", text)
                        if self._wake_word in text.lower():
                            cmd = self._parse_command(text)
                            if cmd:
                                self._queue.put(cmd)
                                logger.info("VoiceCommand queued: intent=%s params=%s", cmd.intent, cmd.params)
                            else:
                                logger.info("VoiceListener: wake word detected but no matching command in %r", text)
                        else:
                            logger.info("VoiceListener: no wake word %r in transcript", self._wake_word)
                    else:
                        logger.info("VoiceListener: transcription returned nothing")
                except sr.WaitTimeoutError:
                    pass
                except Exception as exc:
                    logger.warning("VoiceListener error: %s", exc)

    def _transcribe(self, recognizer, audio) -> str | None:
        try:
            import speech_recognition as sr
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

        silence_match = re.search(r"silent?\s+(?:for\s+)?(?:next\s+)?(\d+)\s*(minute|min|second|sec)", t)
        if silence_match or any(kw in t for kw in ("silent", "silence", "quiet", "mute")):
            seconds = 120
            if silence_match:
                amount = int(silence_match.group(1))
                unit = silence_match.group(2)
                seconds = amount * 60 if unit.startswith("min") else amount
            return VoiceCommand(intent="silence", params={"seconds": seconds})

        logger.debug("No matching intent for: %r", text)
        return None
