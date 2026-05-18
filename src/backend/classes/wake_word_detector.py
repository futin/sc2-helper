import logging
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)


class WakeWordDetector:
    def __init__(
        self,
        model_name: str,
        sensitivity: float,
        on_wake: Callable[[], None],
        chunk_ms: int = 80,
        refractory_s: float = 2.0,
    ):
        self._model_name = model_name
        self._sensitivity = sensitivity
        self._on_wake = on_wake
        self._chunk_ms = chunk_ms
        self._refractory_s = refractory_s
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._detect_loop, daemon=True, name="WakeWordDetector")
        self._thread.start()
        logger.info("WakeWordDetector started (model=%r, sensitivity=%.2f)", self._model_name, self._sensitivity)

    def stop(self) -> None:
        self._stop_event.set()

    def _detect_loop(self) -> None:
        try:
            import pyaudio
            from openwakeword.model import Model
            import numpy as np
        except ImportError as exc:
            logger.error(
                "Wake word detection unavailable: %s. Run: pip install openwakeword pyaudio numpy", exc
            )
            return

        model = Model(wakeword_models=[self._model_name], inference_framework="onnx")
        audio = pyaudio.PyAudio()
        sample_rate = 16000
        chunk_size = int(sample_rate * self._chunk_ms / 1000)

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size,
        )

        logger.info("WakeWordDetector listening for %r...", self._model_name)
        last_wake_at = 0.0
        try:
            while not self._stop_event.is_set():
                try:
                    chunk = stream.read(chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(chunk, dtype=np.int16)
                    prediction = model.predict(audio_data)
                    score = prediction.get(self._model_name, 0.0)
                    now = time.monotonic()
                    if score >= self._sensitivity and now - last_wake_at > self._refractory_s:
                        logger.info(
                            "WakeWordDetector: wake detected (model=%r, score=%.3f)",
                            self._model_name, score,
                        )
                        self._on_wake()
                        last_wake_at = now
                except Exception as exc:
                    logger.warning("WakeWordDetector: audio read error: %s", exc)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
