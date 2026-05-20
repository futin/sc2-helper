# Backend Refactor Design

**Date:** 2026-05-20  
**Scope:** `src/backend/` — structural reorganization + `GameRunner` class extraction  
**Branch:** new feature branch off `main`

---

## Goals

1. Group flat backend files into logical subdirectories (`hud/`, `warnings/`, `voice/`)
2. Reduce `index.py` to a thin entry point (~15 lines)
3. Replace procedural `main()` with a `GameRunner` class that owns all game loop state

## Non-Goals

- No logic changes (detector thresholds, cooldown behavior, voice handling logic)
- No changes to `detectors.py` function signatures
- No changes to `src/frontend/`
- No changes to `db/`

---

## New Directory Layout

```
src/backend/
├── index.py              # ~15 lines: parse args → GameRunner.run()
├── runner.py             # NEW: GameRunner class
├── constants.py          # unchanged
├── logger.py             # unchanged
├── utils.py              # unchanged
├── service.py            # unchanged
├── game_history.py       # unchanged
├── sounds.py             # unchanged
├── find_coords.py        # unchanged (standalone calibration script)
│
├── hud/
│   ├── __init__.py       # re-exports: poll_game, capture_hud, filter_spikes, HUD_ELEMENTS
│   ├── elements.py       # moved from hud_elements.py
│   ├── ocr.py            # moved from ocr.py
│   ├── api.py            # moved from game_api.py
│   └── debug.py          # test_ocr_mode() extracted from index.py
│
├── warnings/
│   ├── __init__.py       # re-exports: check_resources, check_supply, check_idle_workers, get_message
│   ├── detectors.py      # moved from detectors.py
│   └── messages.py       # moved from messages.py
│
├── voice/
│   ├── __init__.py       # re-exports: setup_voice, handle_command
│   ├── listener.py       # moved from classes/voice_listener.py
│   ├── wake_word.py      # moved from classes/wake_word_detector.py
│   └── commands.py       # _handle_voice_command extracted from index.py
│
├── classes/              # retained for SpeechQueue, CooldownTracker
│   ├── __init__.py
│   ├── cooldown_tracker.py
│   └── speech_queue.py
│
└── db/                   # unchanged
```

---

## GameRunner Class (`runner.py`)

Owns all game loop state. No global variables.

### State fields

| Field | Type | Purpose |
|---|---|---|
| `config` | `dict` | loaded config |
| `debug` | `bool` | debug flag |
| `cooldown` | `CooldownTracker` | per-resource cooldowns |
| `speech` | `SpeechQueue` | TTS daemon |
| `stats` | `GameHistoryManager` | per-game warning counts |
| `game_active` | `bool` | tracks game lifecycle |
| `prev_state` | `Optional[dict]` | spike filter input |
| `current_state` | `Optional[dict]` | latest HUD state |
| `silence_until` | `float` | monotonic timestamp |
| `idle_onset` | `Optional[float]` | idle worker onset time |
| `voice_queue` | `Queue` | inter-thread command queue |
| `voice_listener` | `Optional[VoiceListener]` | |
| `detector` | `Optional[WakeWordDetector]` | |

### Methods

```
setup_voice()            → init VoiceListener + WakeWordDetector from config
_drain_voice_commands()  → consume voice_queue each tick, delegate to voice/commands.py
_on_game_start()         → reset per-game state, stats.on_game_start()
_on_game_end(players)    → extract result/race, stats.on_game_end(), print [STATE] idle
_tick()                  → capture HUD, filter spikes, print [STATE], run detectors
run()                    → main while loop + KeyboardInterrupt + finally stop()
stop()                   → speech.stop(), detector.stop()
```

### index.py after refactor

```python
def main():
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return
    debug = "--debug" in sys.argv
    setup_logging(debug)
    GameRunner(get_config(), debug).run()
```

---

## voice/commands.py

Extracts `_handle_voice_command` from `index.py`. Single function, no class needed.

```python
def handle_command(cmd, state, speech, voice, config, cooldown) -> None:
    # existing if/elif logic for query_supply, query_resources, query_workers, silence, unmute
```

`GameRunner._drain_voice_commands()` calls this, then updates `silence_until` for silence/unmute intents.

---

## Import Compatibility

Each new `__init__.py` re-exports the public symbols previously importable at the old path. This ensures any existing callers (tests, frontend subprocess, find_coords.py) continue to work without changes.

Examples:
- `from backend.hud import poll_game` ✓
- `from backend.warnings import check_resources` ✓  
- `from backend.voice import handle_command` ✓

Old direct imports (`from backend.game_api import _poll_game`) will break — these are internal, prefixed with `_`, and only used in `index.py` / `runner.py` which we're rewriting anyway.

---

## Migration Steps (high-level)

1. Create new branch
2. Create `hud/`, `warnings/`, `voice/` subdirs with `__init__.py` stubs
3. Move files into subdirs (rename as needed)
4. Update all intra-backend imports
5. Extract `test_ocr_mode` → `hud/debug.py`
6. Extract `_handle_voice_command` → `voice/commands.py`
7. Write `runner.py` with `GameRunner`
8. Slim down `index.py`
9. Smoke-test: `python3 -m backend.index --test-ocr`
10. Update `CLAUDE.md` project structure table
