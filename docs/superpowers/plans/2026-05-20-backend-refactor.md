# Backend Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize `src/backend/` into logical subdirectories (`hud/`, `warnings/`, `voice/`) and replace the procedural `main()` in `index.py` with a `GameRunner` class in `runner.py`.

**Architecture:** Files are moved into three new subpackages — `hud/` (OCR + screen capture), `warnings/` (detectors + messages), `voice/` (listener + wake word + command handling). A new `GameRunner` class in `runner.py` owns all game loop state; `index.py` shrinks to ~15 lines. Each new `__init__.py` re-exports the public API so callers outside `index.py`/`runner.py` need no changes.

**Tech Stack:** Python 3.11+, no new dependencies.

---

## File Map

**New files:**
- `src/backend/hud/__init__.py`
- `src/backend/hud/elements.py` ← `hud_elements.py`
- `src/backend/hud/ocr.py` ← `ocr.py`
- `src/backend/hud/api.py` ← `game_api.py`
- `src/backend/hud/debug.py` ← `test_ocr_mode()` from `index.py`
- `src/backend/warnings/__init__.py`
- `src/backend/warnings/messages.py` ← `messages.py`
- `src/backend/warnings/detectors.py` ← `detectors.py`
- `src/backend/voice/__init__.py`
- `src/backend/voice/listener.py` ← `classes/voice_listener.py`
- `src/backend/voice/wake_word.py` ← `classes/wake_word_detector.py`
- `src/backend/voice/commands.py` ← `_handle_voice_command()` from `index.py`
- `src/backend/runner.py` ← NEW

**Modified files:**
- `src/backend/index.py` — slimmed to ~15 lines
- `src/backend/classes/__init__.py` — remove voice re-exports
- `src/backend/service.py` — update `hud_elements` import
- `src/backend/find_coords.py` — update `hud_elements` import

**Deleted files (Task 11):**
- `src/backend/hud_elements.py`
- `src/backend/ocr.py`
- `src/backend/game_api.py`
- `src/backend/detectors.py`
- `src/backend/messages.py`
- `src/backend/classes/voice_listener.py`
- `src/backend/classes/wake_word_detector.py`

---

## Task 1: Create branch

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b refactor/backend-structure
```

Expected: `Switched to a new branch 'refactor/backend-structure'`

---

## Task 2: Create `hud/` package — elements, ocr, api

**Files:**
- Create: `src/backend/hud/__init__.py`
- Create: `src/backend/hud/elements.py`
- Create: `src/backend/hud/ocr.py`
- Create: `src/backend/hud/api.py`

- [ ] **Step 1: Create `hud/elements.py`**

```python
# src/backend/hud/elements.py
from dataclasses import dataclass


@dataclass(frozen=True)
class HudElement:
    key: str
    label: str
    default_size: tuple[int, int]  # (width, height) for OCR capture region


HUD_ELEMENTS: list[HudElement] = [
    HudElement("minerals",     "Minerals",     (80, 30)),
    HudElement("gas",          "Gas",          (80, 30)),
    HudElement("supply",       "Supply",       (100, 30)),
    HudElement("idle_workers", "Idle Workers", (60, 25)),
]

HUD_ELEMENT_KEYS: list[str] = [e.key for e in HUD_ELEMENTS]
```

- [ ] **Step 2: Create `hud/ocr.py`**

```python
# src/backend/hud/ocr.py
import logging
from typing import Optional

import mss as _mss
import pytesseract
from PIL import Image, ImageOps


def capture_region(region: list) -> Image.Image:
    """Capture a screen region. region = [left, top, width, height]."""
    left, top, width, height = region
    with _mss.MSS() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.rgb)


def _preprocess(img: Image.Image, threshold: int) -> Image.Image:
    img = img.resize((img.width * 3, img.height * 3), resample=Image.LANCZOS)
    img = ImageOps.grayscale(img)
    return img.point(lambda x: 255 if x > threshold else 0)


def ocr_number(img: Image.Image, threshold: int = 100, region_name: str = "unknown") -> Optional[int]:
    """OCR a single integer from a HUD region. Returns None on failure."""
    text = pytesseract.image_to_string(
        _preprocess(img, threshold),
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    ).strip()
    if text == '':
        return 0
    try:
        return int(text)
    except ValueError:
        logging.warning("OCR failed for %s (got %r)", region_name, text)
        return None


def ocr_supply(img: Image.Image, threshold: int = 100) -> tuple:
    """OCR supply region. Returns (used, max) or (None, None) on failure."""
    text = pytesseract.image_to_string(
        _preprocess(img, threshold),
        config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789/"
    ).strip()
    if "/" in text:
        parts = text.split("/")
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            logging.warning("OCR failed for supply (got %r)", text)
            return None, None
    logging.warning("OCR failed for supply — no '/' in %r", text)
    return None, None
```

- [ ] **Step 3: Create `hud/api.py`**

```python
# src/backend/hud/api.py
import logging
from typing import Optional

import requests

from backend.constants import SC2_BASE, REQUEST_TIMEOUT
from backend.hud.ocr import capture_region, ocr_number, ocr_supply


def _poll_game() -> tuple[bool, list]:
    """Return (is_running, players). Single API call reused by main loop."""
    try:
        resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return False, []
        data = resp.json()
        players = data.get("players", [])
        running = any(p.get("result") == "Undecided" for p in players)
        return running, players
    except (requests.ConnectionError, requests.Timeout, ValueError):
        return False, []


def is_game_running() -> bool:
    """Return True if SC2 is running and a game is in progress."""
    running, _ = _poll_game()
    return running


def _capture_hud(config: dict) -> Optional[dict]:
    """Capture HUD via screen OCR. Assumes game is already confirmed running."""
    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)

    minerals = ocr_number(capture_region(sc["minerals"]), threshold, "minerals")
    gas = ocr_number(capture_region(sc["gas"]), threshold, "gas")
    supply_used, supply_max = ocr_supply(capture_region(sc["supply"]), threshold)
    idle_workers = ocr_number(capture_region(sc["idle_workers"]), threshold, "idle_workers") or 0

    return {
        "minerals": minerals,
        "gas": gas,
        "supply_used": supply_used,
        "supply_max": supply_max,
        "idle_workers": idle_workers,
    }


def _filter_spikes(state: dict, prev: Optional[dict], config: dict) -> dict:
    af = config.get("anomaly_filter", {})
    if not af.get("enabled", False) or prev is None:
        return state
    max_delta = af.get("max_delta", {})
    filtered = dict(state)
    for key in ("minerals", "gas", "supply_used", "supply_max"):
        new_val = state.get(key)
        prev_val = prev.get(key)
        limit = max_delta.get(key)
        if new_val is not None and prev_val is not None and limit is not None:
            if abs(new_val - prev_val) > limit:
                logging.debug("Spike filtered %s: %s → %s", key, prev_val, new_val)
                filtered[key] = prev_val
    return filtered


def fetch_game_state(config: dict) -> Optional[dict]:
    """Capture current game state via screen OCR. Returns None if game not running."""
    if not is_game_running():
        return None
    return _capture_hud(config)
```

- [ ] **Step 4: Create `hud/__init__.py`**

```python
# src/backend/hud/__init__.py
from backend.hud.elements import HudElement, HUD_ELEMENTS, HUD_ELEMENT_KEYS
from backend.hud.ocr import capture_region, ocr_number, ocr_supply
from backend.hud.api import (
    _poll_game, is_game_running, _capture_hud, _filter_spikes, fetch_game_state,
)

__all__ = [
    "HudElement", "HUD_ELEMENTS", "HUD_ELEMENT_KEYS",
    "capture_region", "ocr_number", "ocr_supply",
    "_poll_game", "is_game_running", "_capture_hud", "_filter_spikes", "fetch_game_state",
]
```

- [ ] **Step 5: Verify imports**

Run from repo root:
```bash
cd /path/to/sc2-helper
python3 -c "from backend.hud import HUD_ELEMENTS, capture_region, _poll_game; print('hud OK')"
```

Expected output: `hud OK`

---

## Task 3: Create `hud/debug.py`

**Files:**
- Create: `src/backend/hud/debug.py`

- [ ] **Step 1: Create `hud/debug.py`**

```python
# src/backend/hud/debug.py
from pathlib import Path

from backend.hud.ocr import capture_region, _preprocess, ocr_number, ocr_supply
from backend.service import get_config


def test_ocr_mode() -> None:
    """Capture each configured region, save crops, print OCR results."""
    config = get_config()
    sc = config["screen_capture"]
    threshold = sc.get("ocr_threshold", 100)
    out_dir = Path(__file__).parent.parent / "ocr_debug"
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
```

- [ ] **Step 2: Verify import**

```bash
python3 -c "from backend.hud.debug import test_ocr_mode; print('hud.debug OK')"
```

Expected: `hud.debug OK`

---

## Task 4: Create `warnings/` package

**Files:**
- Create: `src/backend/warnings/__init__.py`
- Create: `src/backend/warnings/messages.py`
- Create: `src/backend/warnings/detectors.py`

- [ ] **Step 1: Create `warnings/messages.py`**

```python
# src/backend/warnings/messages.py
import random

STRICT_MESSAGES = {
    "supply":       "Check supply.",
    "minerals":     "Check minerals.",
    "gas":          "Check gas.",
    "idle_workers": "Check lazy workers.",
}

SUPPLY_MESSAGES = [
    "Supply blocked incoming! Build something or cry later.",
    "You're capped. Your army is waiting. Are you waiting too?",
    "Supply is full. Your units are unionizing outside the barracks.",
    "No more room! Did you forget depots are a thing?",
    "Supply cap hit. Congratulations, you've built a very cozy base.",
    "Your production is on strike. Build more supply. Now.",
    "Almost capped. This is not a drill. Build. Depots. Now.",
    "Supply critical. Your opponent is laughing. Don't let them.",
    "Capped again? Incredible. Truly a signature move.",
    "Max supply approaching. Overlords don't build themselves. Actually they do. Use them.",
]

MINERAL_MESSAGES = [
    "Minerals piling up. Spend them. They're not a savings account.",
    "You have enough minerals to build a small moon. Please don't.",
    "Your bank account is full. Your army is not. Fix that.",
    "Stop hoarding. This isn't Minecraft.",
    "Minerals overflowing. Your economy weeps for efficiency.",
    "Rich and doing nothing. Very impressive. Very bad.",
    "That's a lot of blue crystals just sitting there judging you.",
    "Spend the minerals. Your workers mined them for a reason.",
    "Mineral surplus detected. Your macro just rolled its eyes.",
    "You're swimming in minerals. Build something before you drown.",
]

IDLE_WORKER_MESSAGES = [
    "Workers on vacation. Unpaid. Fix this immediately.",
    "Idle workers detected. They are deeply disappointed in you.",
    "Your workers are standing around like lost tourists. Send them somewhere.",
    "Those workers didn't sign up to watch the game. Put them to work.",
    "Idle workers! They have families to feed. Metaphorically.",
    "Workers sitting idle. This is the macro crime of the century.",
    "Your probes are having an existential crisis. Give them purpose.",
    "Lazy workers alert. They didn't choose this life. You did.",
    "Idle SCVs detected. They built this base and now you ignore them?",
    "Workers sleeping on the job. You're paying for this.",
]

GAS_MESSAGES = [
    "Gas overflowing. Build something gassy. Like a roach warren.",
    "Too much gas. Are you even teching? What is the plan here?",
    "Gas surplus. Your vespene geysers are personally offended.",
    "Drowning in gas. Either you're turtling or you forgot tech exists.",
    "Gas piling up. Your refineries are working harder than your brain.",
    "That's a lot of gas. Your units are still not upgraded. Interesting.",
    "Gas capped. Spend it or explain yourself to your future self.",
    "Vespene everywhere and nothing to show for it. Classic.",
    "Gas overload. The geysers are giving you everything. Give something back.",
    "Too much gas detected. Somewhere a Hydralisk is crying.",
]


def get_message(category: str, mode: str = "strict", custom_messages: dict | None = None) -> str:
    if mode == "custom":
        msgs = (custom_messages or {}).get(category, [])
        if msgs:
            return random.choice(msgs) if isinstance(msgs, list) else msgs
        return STRICT_MESSAGES.get(category, "")
    if mode == "funny":
        messages = {
            "supply":       SUPPLY_MESSAGES,
            "minerals":     MINERAL_MESSAGES,
            "idle_workers": IDLE_WORKER_MESSAGES,
            "gas":          GAS_MESSAGES,
        }
        return random.choice(messages[category])
    return STRICT_MESSAGES[category]
```

- [ ] **Step 2: Create `warnings/detectors.py`**

```python
# src/backend/warnings/detectors.py
import time
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.constants import (
    PRIORITY_MINERALS, PRIORITY_GAS, PRIORITY_SUPPLY, PRIORITY_IDLE_WORKERS,
)
from backend.warnings.messages import get_message


def check_resources(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> None:
    minerals = state["minerals"]
    gas = state["gas"]
    res_cfg = config["resources"]

    if minerals is not None and minerals > res_cfg["mineral_threshold"] and cooldown.ready("minerals", res_cfg["cooldown"]):
        speech.speak(get_message("minerals", mode, custom_messages), voice, PRIORITY_MINERALS)
        if stats:
            stats.on_mineral_warning()
    if gas is not None and gas > res_cfg["gas_threshold"] and cooldown.ready("gas", res_cfg["cooldown"]):
        speech.speak(get_message("gas", mode, custom_messages), voice, PRIORITY_GAS)
        if stats:
            stats.on_gas_warning()


def check_supply(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> None:
    supply_used = state["supply_used"]
    supply_max = state["supply_max"]

    if supply_used is None or supply_max is None or supply_max == 0:
        return

    supply_cfg = config["supply"]
    gap = supply_max - supply_used

    warn_gap = None
    for tier in supply_cfg["tiers"]:
        if supply_max <= tier["max_cap"]:
            warn_gap = tier["gap"]
            break

    if warn_gap is not None and gap <= warn_gap and cooldown.ready("supply", supply_cfg["cooldown"]):
        speech.speak(get_message("supply", mode, custom_messages), voice, PRIORITY_SUPPLY)
        if stats:
            stats.on_supply_warning()


def check_idle_workers(
    state: dict,
    config: dict,
    cooldown: CooldownTracker,
    speech: SpeechQueue,
    voice: str,
    idle_onset: Optional[float],
    mode: str = "strict",
    custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> Optional[float]:
    """Track idle workers. Returns updated idle_onset (or None if busy)."""
    idle_count = state["idle_workers"]
    workers_cfg = config["workers"]

    if idle_count is None or idle_count == 0:
        return None

    if idle_onset is None:
        idle_onset = time.monotonic()

    elapsed = time.monotonic() - idle_onset
    if elapsed >= workers_cfg["idle_seconds"] and cooldown.ready("workers", workers_cfg["cooldown"]):
        speech.speak(get_message("idle_workers", mode, custom_messages), voice, PRIORITY_IDLE_WORKERS)
        if stats:
            stats.on_idle_workers_warning()

    return idle_onset
```

- [ ] **Step 3: Create `warnings/__init__.py`**

```python
# src/backend/warnings/__init__.py
from backend.warnings.messages import get_message
from backend.warnings.detectors import check_resources, check_supply, check_idle_workers

__all__ = ["get_message", "check_resources", "check_supply", "check_idle_workers"]
```

- [ ] **Step 4: Verify imports**

```bash
python3 -c "from backend.warnings import check_resources, check_supply, check_idle_workers, get_message; print('warnings OK')"
```

Expected: `warnings OK`

---

## Task 5: Create `voice/` package

**Files:**
- Create: `src/backend/voice/__init__.py`
- Create: `src/backend/voice/listener.py`
- Create: `src/backend/voice/wake_word.py`
- Create: `src/backend/voice/commands.py`

- [ ] **Step 1: Create `voice/listener.py`**

```python
# src/backend/voice/listener.py
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
                logger.info(
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
                logger.info("VoiceListener: wake detected, listening for command...")
                try:
                    audio = self._recognizer.listen(
                        source, timeout=5, phrase_time_limit=self._phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    logger.info("VoiceListener: no command heard after wake word")
                    play_boop()
                    return

        text = self._transcribe(self._recognizer, audio)
        if not text:
            play_boop()
            return

        logger.info("VoiceListener heard: %r", text)
        cmd = self._parse_command(text)
        if cmd:
            self._queue.put(cmd)
            logger.info("VoiceCommand queued: intent=%s params=%s", cmd.intent, cmd.params)
        else:
            logger.info("VoiceListener: no matching command in %r", text)
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
```

- [ ] **Step 2: Create `voice/wake_word.py`**

```python
# src/backend/voice/wake_word.py
import logging
import threading
import time
from typing import Callable

from backend.sounds import play_beep

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

        try:
            model = Model(wakeword_models=[self._model_name], inference_framework="onnx")
        except Exception as exc:
            logger.error(
                "WakeWordDetector: failed to load model %r: %s. "
                "Download models with: python -c \"from openwakeword.utils import download_models; download_models()\"",
                self._model_name, exc,
            )
            return
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
                except OSError as exc:
                    logger.warning("WakeWordDetector: audio read error: %s", exc)
                    continue
                audio_data = np.frombuffer(chunk, dtype=np.int16)
                prediction = model.predict(audio_data)
                score = prediction.get(self._model_name, 0.0)
                now = time.monotonic()
                if score >= self._sensitivity and now - last_wake_at > self._refractory_s:
                    logger.info(
                        "WakeWordDetector: wake detected (model=%r, score=%.3f)",
                        self._model_name, score,
                    )
                    threading.Thread(target=play_beep, daemon=True).start()
                    self._on_wake()
                    last_wake_at = time.monotonic()
                    available = stream.get_read_available()
                    if available > 0:
                        stream.read(available, exception_on_overflow=False)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
```

- [ ] **Step 3: Create `voice/commands.py`**

```python
# src/backend/voice/commands.py
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.constants import PRIORITY_VOICE_RESPONSE


def handle_command(
    cmd,
    state: Optional[dict],
    speech: SpeechQueue,
    voice: str,
    config: dict,
    cooldown: CooldownTracker,
) -> None:
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
    elif cmd.intent == "query_workers":
        if state:
            idle_workers = state.get("idle_workers", "?")
            speech.speak(f"You have {idle_workers} idle workers.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "silence":
        seconds = cmd.params["seconds"]
        mins = seconds // 60
        speech.speak(f"Going silent for {mins} minute{'s' if mins != 1 else ''}.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "unmute":
        speech.speak("Sound enabled.", voice, PRIORITY_VOICE_RESPONSE)
```

- [ ] **Step 4: Create `voice/__init__.py`**

```python
# src/backend/voice/__init__.py
from backend.voice.listener import VoiceListener, VoiceCommand
from backend.voice.wake_word import WakeWordDetector
from backend.voice.commands import handle_command

__all__ = ["VoiceListener", "VoiceCommand", "WakeWordDetector", "handle_command"]
```

- [ ] **Step 5: Verify imports**

```bash
python3 -c "from backend.voice import VoiceListener, VoiceCommand, WakeWordDetector, handle_command; print('voice OK')"
```

Expected: `voice OK`

---

## Task 6: Update `classes/__init__.py`

**Files:**
- Modify: `src/backend/classes/__init__.py`

- [ ] **Step 1: Remove voice class re-exports (they now live in `voice/`)**

Replace the entire file with:

```python
# src/backend/classes/__init__.py
from backend.classes.speech_queue import SpeechQueue
from backend.classes.cooldown_tracker import CooldownTracker

__all__ = ["SpeechQueue", "CooldownTracker"]
```

- [ ] **Step 2: Verify**

```bash
python3 -c "from backend.classes import SpeechQueue, CooldownTracker; print('classes OK')"
```

Expected: `classes OK`

---

## Task 7: Update callers of `hud_elements`

**Files:**
- Modify: `src/backend/service.py:11`
- Modify: `src/backend/find_coords.py:15`

- [ ] **Step 1: Update `service.py` import**

In `src/backend/service.py`, change line 11:

```python
# Before
from backend.hud_elements import HUD_ELEMENTS

# After
from backend.hud.elements import HUD_ELEMENTS
```

- [ ] **Step 2: Update `find_coords.py` import**

In `src/backend/find_coords.py`, change the import inside `__main__`:

```python
# Before
from backend.hud_elements import HUD_ELEMENTS

# After
from backend.hud.elements import HUD_ELEMENTS
```

- [ ] **Step 3: Verify**

```bash
python3 -c "from backend.service import get_config; print('service OK')"
python3 -c "import ast, sys; ast.parse(open('src/backend/find_coords.py').read()); print('find_coords parse OK')"
```

Expected: both lines print OK

---

## Task 8: Write `runner.py`

**Files:**
- Create: `src/backend/runner.py`

- [ ] **Step 1: Create `runner.py`**

```python
# src/backend/runner.py
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
```

- [ ] **Step 2: Verify import**

```bash
python3 -c "from backend.runner import GameRunner; print('runner OK')"
```

Expected: `runner OK`

---

## Task 9: Slim down `index.py`

**Files:**
- Modify: `src/backend/index.py`

- [ ] **Step 1: Replace `index.py` with thin entry point**

Replace entire file contents with:

```python
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

import sys

from backend.hud.debug import test_ocr_mode
from backend.logger import setup_logging
from backend.runner import GameRunner
from backend.service import get_config


def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return
    debug: bool = "--debug" in sys.argv
    setup_logging(debug)
    GameRunner(get_config(), debug).run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify import**

```bash
python3 -c "from backend.index import main; print('index OK')"
```

Expected: `index OK`

---

## Task 10: Delete old files

**Warning:** Only do this after all previous tasks pass their import checks.

- [ ] **Step 1: Delete moved files**

```bash
git rm src/backend/hud_elements.py \
       src/backend/ocr.py \
       src/backend/game_api.py \
       src/backend/detectors.py \
       src/backend/messages.py \
       src/backend/classes/voice_listener.py \
       src/backend/classes/wake_word_detector.py
```

- [ ] **Step 2: Verify no broken imports**

```bash
python3 -c "
from backend.hud import HUD_ELEMENTS, capture_region, _poll_game
from backend.warnings import check_resources, check_supply, check_idle_workers, get_message
from backend.voice import VoiceListener, WakeWordDetector, handle_command
from backend.runner import GameRunner
from backend.index import main
print('all imports OK')
"
```

Expected: `all imports OK`

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor(backend): reorganize into hud/, warnings/, voice/ + GameRunner"
```

---

## Task 11: Smoke test

- [ ] **Step 1: Run test-ocr mode**

```bash
python3 -m backend.index --test-ocr
```

Expected: prints OCR results for minerals, gas, supply, idle_workers and reports crops saved (or OCR errors if SC2 not running — that's fine, the important thing is no `ImportError` or `ModuleNotFoundError`).

- [ ] **Step 2: Verify frontend still starts**

```bash
python3 -m frontend.sc2_ui &
sleep 3
kill %1
```

Expected: process starts without `ImportError`.

---

## Task 12: Update `CLAUDE.md` project structure table

**Files:**
- Modify: `.claude/CLAUDE.md`

- [ ] **Step 1: Update the Backend table in `.claude/CLAUDE.md`**

Replace the Backend section's file table with:

```markdown
### Backend (`src/backend/`)

| File | Responsibility |
|------|---------------|
| `index.py` | Entry point — parse args, call `GameRunner.run()` |
| `runner.py` | `GameRunner` class — owns all game loop state |
| `constants.py` | `SC2_BASE`, `REQUEST_TIMEOUT`, `PRIORITY_*`, `_RESULT_MAP`, `_RACE_MAP` |
| `utils.py` | `_extract_result`, `_extract_race`, `_format_debug_state` |
| `logger.py` | `setup_logging()` |
| `service.py` | Service layer — `get_config`, `save_config`, `get_stats_history`, `get_live_stats` |
| `game_history.py` | `GameHistoryManager` — per-game warning counts → SQLite |
| `sounds.py` | Audio cue helpers |
| `find_coords.py` | Standalone calibration script (macOS, `__main__` block) |
| `hud/elements.py` | `HudElement` dataclass + `HUD_ELEMENTS` list |
| `hud/ocr.py` | Screen capture (`mss`) + Tesseract OCR functions |
| `hud/api.py` | SC2 API polling, HUD capture, spike filter |
| `hud/debug.py` | `test_ocr_mode()` — OCR debug helper |
| `warnings/detectors.py` | `check_resources`, `check_supply`, `check_idle_workers` |
| `warnings/messages.py` | Warning message banks + `get_message()` |
| `voice/listener.py` | `VoiceListener` + `VoiceCommand` |
| `voice/wake_word.py` | `WakeWordDetector` |
| `voice/commands.py` | `handle_command()` — voice intent → TTS response |
| `classes/speech_queue.py` | `SpeechQueue` — priority TTS daemon thread |
| `classes/cooldown_tracker.py` | `CooldownTracker` |
| `db/__init__.py` | `get_db()` context manager, `DB_PATH` |
| `db/connector.py` | Database abstraction base |
| `db/sqlite_connector.py` | `aiosqlite` implementation |
| `db/collection.py` | Collection query API (`find`/`findOne`/`create`/`updateOne`) |
| `db/schema.py` | `CREATE TABLE` statements for `config` + `game_stats` |
```

- [ ] **Step 2: Commit**

```bash
git add .claude/CLAUDE.md
git commit -m "docs(claude): update backend structure table after refactor"
```

---

## Self-Review

**Spec coverage check:**
- ✅ `hud/` subpackage with elements, ocr, api, debug — Tasks 2–3
- ✅ `warnings/` subpackage — Task 4
- ✅ `voice/` subpackage with listener, wake_word, commands — Task 5
- ✅ `classes/` retains SpeechQueue, CooldownTracker — Task 6
- ✅ `service.py` + `find_coords.py` import updates — Task 7
- ✅ `GameRunner` class with all specified methods — Task 8
- ✅ `index.py` slimmed to ~15 lines — Task 9
- ✅ Old files deleted — Task 10
- ✅ Smoke test — Task 11
- ✅ CLAUDE.md updated — Task 12
- ✅ New branch created — Task 1

**No placeholders found.**

**Type consistency:** `handle_command` signature in `voice/commands.py` (Task 5 Step 3) matches usage in `runner.py` `_drain_voice_commands` (Task 8 Step 1). `GameRunner` method signatures consistent throughout.
