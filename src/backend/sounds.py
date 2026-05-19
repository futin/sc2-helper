import logging

logger = logging.getLogger(__name__)


def _play_tone(freq: float, duration_s: float = 0.15, volume: float = 0.4) -> None:
    try:
        import numpy as np
        import pyaudio
    except ImportError:
        return

    sample_rate = 44100
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
    tone = (np.sin(2 * np.pi * freq * t) * volume * 32767).astype(np.int16)
    try:
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
        stream.write(tone.tobytes())
        stream.stop_stream()
        stream.close()
        pa.terminate()
    except Exception as exc:
        logger.debug("sounds: could not play tone: %s", exc)


def play_beep() -> None:
    """Short high tone — wake word confirmed, speak now."""
    _play_tone(880.0, duration_s=0.12)


def play_boop() -> None:
    """Short low tone — command not understood or failed."""
    _play_tone(440.0, duration_s=0.18)
