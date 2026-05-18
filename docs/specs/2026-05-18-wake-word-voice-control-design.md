# Wake-Word Voice Control — Design Spec

**Date:** 2026-05-18  
**Branch:** feature/voice-control  
**Status:** Approved

---

## Problem

Current `VoiceListener` uses single-phase detection: captures audio, transcribes everything via Google STT or Whisper, then checks if the wake word appears in the transcript. This burns API calls (Google STT) or CPU (Whisper) on all ambient sound.

True wake-word pattern: lightweight always-on detector → only transcribe after wake word confirmed.

---

## Approach

Option B: two separate classes with single responsibilities, wired in `index.py`.

---

## Components

### `WakeWordDetector` (new — `src/backend/classes/wake_word_detector.py`)

- Opens raw `pyaudio` stream
- Feeds 80ms chunks to `openwakeword` model (`alexa`)
- On score above `sensitivity` threshold → calls `on_wake()` callback
- Runs in daemon thread, stoppable via `threading.Event`
- Config: `model_name`, `sensitivity` (float 0.0–1.0), `chunk_ms` (int, default 80)

### `VoiceListener` (refactored — `src/backend/classes/voice_listener.py`)

- No longer owns microphone or always-on detection loop
- Exposes `handle_wake()` — invoked by `WakeWordDetector` callback
- `handle_wake()`: opens mic → `SpeechRecognition.listen()` → `_transcribe()` → `_parse_command()` → puts `VoiceCommand` in queue
- `_transcribe()` and `_parse_command()` unchanged
- Constructor no longer starts a thread; `handle_wake()` runs inline on the detector's thread

### `index.py` (wiring change)

```python
voice_listener = VoiceListener(
    stt_backend=voice_cfg.get("stt_backend", "google"),
    command_queue=voice_queue,
    pause_threshold=...,
    phrase_time_limit=...,
)
detector = WakeWordDetector(
    model_name=voice_cfg.get("wake_word_model", "alexa"),
    sensitivity=float(voice_cfg.get("wake_sensitivity", 0.5)),
    on_wake=voice_listener.handle_wake,
)
detector.start()
```

Stop both on exit.

### `src/backend/classes/__init__.py`

Export `WakeWordDetector`.

---

## Data Flow

```
pyaudio chunks (80ms)
  → WakeWordDetector (openwakeword score)
  → threshold hit → voice_listener.handle_wake()
    → SpeechRecognition.listen()
    → _transcribe() [google or whisper]
    → _parse_command()
    → VoiceCommand → command_queue
      → index.py _handle_voice_command()
```

---

## Config Schema

New keys under `voice_control`:

```json
"voice_control": {
  "enabled": true,
  "wake_word_model": "alexa",
  "wake_sensitivity": 0.5,
  "stt_backend": "google",
  "pause_threshold": 1.2,
  "phrase_time_limit": 8
}
```

`wake_sensitivity`: 0.5 default. Raise to reduce false positives; lower to catch quieter triggers.

Old keys removed: `wake_word` (string), `phrase_threshold`, `non_speaking_duration` — replaced by model-based detection.

---

## Error Handling

| Failure | Behaviour |
|---------|-----------|
| `openwakeword` not installed | Log error, skip detector init, voice stays disabled |
| `pyaudio` not installed | Same |
| Wake detected, mic capture fails | Log warning, return from `handle_wake()`, detector resumes |
| `_transcribe()` returns `None` | Log warning, no queue put (existing behaviour) |
| No matching intent | Log debug, no queue put (existing behaviour) |

No crash propagation to main loop in any case.

---

## Dependencies

```
openwakeword
pyaudio          # already required by SpeechRecognition
SpeechRecognition  # unchanged
```

`openwakeword` auto-downloads ONNX model on first run (~2 MB for `alexa`).

---

## Testing

Audio I/O not unit-testable. Manual integration test:

1. Run `python3 -m backend.index --debug`
2. Say "alexa supply"
3. Verify log: `WakeWordDetector: wake detected (score=X)` then `VoiceListener heard: "alexa supply"` then `VoiceCommand queued: intent=query_supply`
