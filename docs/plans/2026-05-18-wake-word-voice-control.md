# Wake-Word Voice Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace single-phase voice transcription loop with two-phase wake-word detection (openwakeword "alexa" model) + command transcription (SpeechRecognition).

**Architecture:** `WakeWordDetector` runs a pyaudio stream through openwakeword ONNX model; on threshold hit it calls `VoiceListener.handle_wake()` which opens mic, transcribes one command, parses intent, enqueues `VoiceCommand`. `index.py` owns both instances.

**Tech Stack:** `openwakeword`, `pyaudio`, `SpeechRecognition`, `numpy`, existing `pytest` + `unittest.mock`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `src/backend/service.py` | Update `DEFAULT_CONFIG` `voice_control` keys |
| Create | `src/backend/classes/wake_word_detector.py` | Always-on wake-word detection thread |
| Modify | `src/backend/classes/voice_listener.py` | Two-phase: remove loop, add `handle_wake()` |
| Modify | `src/backend/classes/__init__.py` | Export `WakeWordDetector` |
| Modify | `src/backend/index.py` | Wire `WakeWordDetector` + `VoiceListener` |
| Create | `tests/test_wake_word_detector.py` | Unit tests for `WakeWordDetector` |
| Modify | `tests/test_voice_listener.py` | Tests for refactored `VoiceListener` (new file) |

---

## Task 1: Update DEFAULT_CONFIG

**Files:**
- Modify: `src/backend/service.py:52-61`

- [ ] **Step 1: Update `voice_control` block in `DEFAULT_CONFIG`**

Replace lines 52–61 in `src/backend/service.py`:

```python
    "voice_control": {
        "enabled": False,
        "wake_word_model": "alexa",
        "wake_sensitivity": 0.5,
        "stt_backend": "google",
        "silence_duration": 120,
        "pause_threshold": 1.2,
        "phrase_time_limit": 8,
    },
```

Removed: `wake_word`, `phrase_threshold`, `non_speaking_duration`
Added: `wake_word_model`, `wake_sensitivity`

- [ ] **Step 2: Commit**

```bash
git add src/backend/service.py
git commit -m "config: update voice_control defaults for wake-word detection"
```

---

## Task 2: Create `WakeWordDetector`

**Files:**
- Create: `src/backend/classes/wake_word_detector.py`
- Create: `tests/test_wake_word_detector.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_wake_word_detector.py`:

```python
import queue
import threading
from unittest.mock import MagicMock, patch

import pytest

from backend.classes.wake_word_detector import WakeWordDetector


def test_init_sets_attributes():
    called = []
    detector = WakeWordDetector(
        model_name="alexa",
        sensitivity=0.7,
        on_wake=lambda: called.append(1),
        chunk_ms=80,
    )
    assert detector._model_name == "alexa"
    assert detector._sensitivity == 0.7
    assert detector._chunk_ms == 80
    assert not detector._stop_event.is_set()


def test_stop_sets_event():
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: None)
    detector.stop()
    assert detector._stop_event.is_set()


def test_detect_loop_logs_error_on_missing_import():
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: None)
    with patch.dict("sys.modules", {"pyaudio": None, "openwakeword": None, "openwakeword.model": None}):
        # Should return without raising
        detector._detect_loop()


def test_detect_loop_calls_on_wake_when_threshold_met():
    called = []
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: called.append(1))

    mock_model = MagicMock()
    mock_model.predict.return_value = {"alexa": 0.9}

    mock_stream = MagicMock()
    import numpy as np
    mock_stream.read.side_effect = [
        np.zeros(1280, dtype=np.int16).tobytes(),
        StopIteration,  # exit loop after one iteration
    ]

    mock_audio = MagicMock()
    mock_audio.open.return_value = mock_stream

    mock_pyaudio = MagicMock()
    mock_pyaudio.PyAudio.return_value = mock_audio
    mock_pyaudio.paInt16 = 8

    mock_oww_model = MagicMock()
    mock_oww_model.Model.return_value = mock_model

    detector._stop_event.set()  # stop after first chunk

    with patch.dict("sys.modules", {"pyaudio": mock_pyaudio, "openwakeword": MagicMock(), "openwakeword.model": mock_oww_model}):
        with patch("numpy.frombuffer", return_value=np.zeros(1280, dtype=np.int16)):
            detector._stop_event.clear()
            # Run one iteration by patching stop_event to stop after on_wake
            original_on_wake = detector._on_wake
            def stopping_on_wake():
                original_on_wake()
                detector._stop_event.set()
            detector._on_wake = stopping_on_wake
            detector._detect_loop()

    assert len(called) == 1
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /path/to/sc2-helper
pytest tests/test_wake_word_detector.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `wake_word_detector` doesn't exist yet.

- [ ] **Step 3: Create `WakeWordDetector`**

Create `src/backend/classes/wake_word_detector.py`:

```python
import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)


class WakeWordDetector:
    def __init__(
        self,
        model_name: str,
        sensitivity: float,
        on_wake: Callable[[], None],
        chunk_ms: int = 80,
    ):
        self._model_name = model_name
        self._sensitivity = sensitivity
        self._on_wake = on_wake
        self._chunk_ms = chunk_ms
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
        try:
            while not self._stop_event.is_set():
                chunk = stream.read(chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(chunk, dtype=np.int16)
                prediction = model.predict(audio_data)
                score = prediction.get(self._model_name, 0.0)
                if score >= self._sensitivity:
                    logger.info(
                        "WakeWordDetector: wake detected (model=%r, score=%.3f)",
                        self._model_name, score,
                    )
                    self._on_wake()
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_wake_word_detector.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/backend/classes/wake_word_detector.py tests/test_wake_word_detector.py
git commit -m "feat(voice): add WakeWordDetector with openwakeword"
```

---

## Task 3: Refactor `VoiceListener`

**Files:**
- Modify: `src/backend/classes/voice_listener.py`
- Create: `tests/test_voice_listener.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_voice_listener.py`:

```python
import queue
from unittest.mock import MagicMock, patch

import pytest

from backend.classes.voice_listener import VoiceCommand, VoiceListener


def _make_listener(q=None):
    return VoiceListener(
        stt_backend="google",
        command_queue=q or queue.Queue(),
        pause_threshold=1.2,
        phrase_time_limit=8,
    )


# --- _parse_command ---

def test_parse_supply():
    listener = _make_listener()
    cmd = listener._parse_command("alexa supply status")
    assert cmd is not None
    assert cmd.intent == "query_supply"


def test_parse_resources():
    listener = _make_listener()
    cmd = listener._parse_command("alexa how many minerals")
    assert cmd is not None
    assert cmd.intent == "query_resources"


def test_parse_silence_minutes():
    listener = _make_listener()
    cmd = listener._parse_command("alexa silent for 3 minutes")
    assert cmd is not None
    assert cmd.intent == "silence"
    assert cmd.params["seconds"] == 180


def test_parse_silence_seconds():
    listener = _make_listener()
    cmd = listener._parse_command("alexa silence for 30 seconds")
    assert cmd is not None
    assert cmd.intent == "silence"
    assert cmd.params["seconds"] == 30


def test_parse_unknown_returns_none():
    listener = _make_listener()
    cmd = listener._parse_command("alexa what is the weather")
    assert cmd is None


# --- handle_wake ---

def test_handle_wake_enqueues_command():
    q = queue.Queue()
    listener = _make_listener(q)

    mock_sr = MagicMock()
    mock_recognizer = MagicMock()
    mock_recognizer.recognize_google.return_value = "supply status"
    mock_sr.Recognizer.return_value = mock_recognizer
    mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=False)
    mock_sr.WaitTimeoutError = TimeoutError

    with patch.dict("sys.modules", {"speech_recognition": mock_sr}):
        listener.handle_wake()

    assert not q.empty()
    cmd = q.get_nowait()
    assert cmd.intent == "query_supply"


def test_handle_wake_timeout_does_not_enqueue():
    q = queue.Queue()
    listener = _make_listener(q)

    mock_sr = MagicMock()
    mock_recognizer = MagicMock()
    mock_sr.WaitTimeoutError = TimeoutError
    mock_recognizer.listen.side_effect = TimeoutError
    mock_sr.Recognizer.return_value = mock_recognizer
    mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("sys.modules", {"speech_recognition": mock_sr}):
        listener.handle_wake()

    assert q.empty()


def test_handle_wake_missing_import_does_not_raise():
    listener = _make_listener()
    with patch.dict("sys.modules", {"speech_recognition": None}):
        listener.handle_wake()  # should return cleanly
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_voice_listener.py -v
```

Expected: failures due to missing `handle_wake` and wrong constructor signature.

- [ ] **Step 3: Rewrite `VoiceListener`**

Replace entire content of `src/backend/classes/voice_listener.py`:

```python
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
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_voice_listener.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 5: Run full test suite — verify no regressions**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/backend/classes/voice_listener.py tests/test_voice_listener.py
git commit -m "feat(voice): refactor VoiceListener to two-phase handle_wake()"
```

---

## Task 4: Export `WakeWordDetector` from `__init__.py`

**Files:**
- Modify: `src/backend/classes/__init__.py`

- [ ] **Step 1: Add export**

Replace entire content of `src/backend/classes/__init__.py`:

```python
from backend.classes.speech_queue import SpeechQueue
from backend.classes.cooldown_tracker import CooldownTracker
from backend.classes.wake_word_detector import WakeWordDetector

__all__ = ["SpeechQueue", "CooldownTracker", "WakeWordDetector"]
```

- [ ] **Step 2: Verify import works**

```bash
python3 -c "from backend.classes import WakeWordDetector; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/backend/classes/__init__.py
git commit -m "feat(voice): export WakeWordDetector from classes package"
```

---

## Task 5: Wire `index.py`

**Files:**
- Modify: `src/backend/index.py`

- [ ] **Step 1: Update imports**

At top of `src/backend/index.py`, replace:

```python
from backend.classes import CooldownTracker, SpeechQueue
from backend.classes.voice_listener import VoiceListener
```

with:

```python
from backend.classes import CooldownTracker, SpeechQueue, WakeWordDetector
from backend.classes.voice_listener import VoiceListener
```

- [ ] **Step 2: Replace voice init block in `main()`**

Find this block (around line 99–111):

```python
    voice_queue: queue.Queue = queue.Queue()
    voice_listener: Optional[VoiceListener] = None
    if voice_cfg.get("enabled", False):
        voice_listener = VoiceListener(
            wake_word=voice_cfg.get("wake_word", "zag"),
            stt_backend=voice_cfg.get("stt_backend", "google"),
            command_queue=voice_queue,
            pause_threshold=float(voice_cfg.get("pause_threshold", 1.2)),
            phrase_threshold=float(voice_cfg.get("phrase_threshold", 0.3)),
            non_speaking_duration=float(voice_cfg.get("non_speaking_duration", 0.4)),
            phrase_time_limit=int(voice_cfg.get("phrase_time_limit", 8)),
        )
        voice_listener.start()
```

Replace with:

```python
    voice_queue: queue.Queue = queue.Queue()
    voice_listener: Optional[VoiceListener] = None
    detector: Optional[WakeWordDetector] = None
    if voice_cfg.get("enabled", False):
        voice_listener = VoiceListener(
            stt_backend=voice_cfg.get("stt_backend", "google"),
            command_queue=voice_queue,
            pause_threshold=float(voice_cfg.get("pause_threshold", 1.2)),
            phrase_time_limit=int(voice_cfg.get("phrase_time_limit", 8)),
        )
        detector = WakeWordDetector(
            model_name=voice_cfg.get("wake_word_model", "alexa"),
            sensitivity=float(voice_cfg.get("wake_sensitivity", 0.5)),
            on_wake=voice_listener.handle_wake,
        )
        detector.start()
```

- [ ] **Step 3: Add `detector` type annotation near top of `main()`**

Add `from typing import Optional` is already imported. Add `detector` to the variable declarations:

```python
    detector: Optional[WakeWordDetector] = None
```

(This is already included in the block above — just ensure it's present.)

- [ ] **Step 4: Update `finally` block to stop detector**

Find:

```python
    finally:
        if voice_listener:
            voice_listener.stop()
```

Replace with:

```python
    finally:
        if detector:
            detector.stop()
```

(`VoiceListener` no longer has `stop()` — only `WakeWordDetector` does.)

- [ ] **Step 5: Update voice_on checks**

`voice_on` is set based on `voice_listener`. This still works — no change needed since `voice_listener` is still `None` when disabled.

- [ ] **Step 6: Run full test suite**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 7: Smoke test — verify backend starts without error**

```bash
python3 -m backend.index --debug
```

Expected: starts without `ImportError`, prints `[STATE] game=idle voice=off` (voice off because `enabled=False` in default config).

- [ ] **Step 8: Commit**

```bash
git add src/backend/index.py
git commit -m "feat(voice): wire WakeWordDetector + VoiceListener in main loop"
```

---

## Manual Integration Test

To verify end-to-end with voice enabled:

1. Enable voice in config (via Settings UI or edit DB directly): `"enabled": true`
2. Run: `python3 -m backend.index --debug`
3. Verify log: `WakeWordDetector started (model='alexa', sensitivity=0.50)`
4. Say "alexa supply"
5. Verify logs in order:
   - `WakeWordDetector: wake detected (model='alexa', score=X.XXX)`
   - `VoiceListener: wake detected, listening for command...`
   - `VoiceListener heard: "alexa supply"`
   - `VoiceCommand queued: intent=query_supply params={}`
6. Verify TTS speaks supply count

**First run note:** `openwakeword` auto-downloads `alexa` ONNX model (~2 MB) on first call to `Model(wakeword_models=["alexa"])`.
