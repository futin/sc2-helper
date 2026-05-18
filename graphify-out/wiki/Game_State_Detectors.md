# Game State Detectors

> 37 nodes · cohesion 0.50

## Key Concepts

- **main()** (18 connections) — `src/backend/index.py`
- **CooldownTracker** (12 connections) — `src/backend/classes/cooldown_tracker.py`
- **test_detectors.py** (9 connections) — `tests/test_detectors.py`
- **_make_speech()** (9 connections) — `tests/test_detectors.py`
- **check_resources()** (6 connections) — `src/backend/detectors.py`
- **check_idle_workers()** (6 connections) — `src/backend/detectors.py`
- **check_supply()** (5 connections) — `src/backend/detectors.py`
- **test_check_resources_no_speak_below_threshold()** (4 connections) — `tests/test_detectors.py`
- **test_check_resources_speaks_when_over_threshold()** (4 connections) — `tests/test_detectors.py`
- **test_check_resources_cooldown_prevents_repeat()** (4 connections) — `tests/test_detectors.py`
- **test_check_supply_speaks_when_capped()** (4 connections) — `tests/test_detectors.py`
- **test_check_supply_silent_when_ok()** (4 connections) — `tests/test_detectors.py`
- **test_check_idle_workers_speaks_when_idle()** (4 connections) — `tests/test_detectors.py`
- **test_check_idle_workers_resets_on_zero()** (4 connections) — `tests/test_detectors.py`
- **index.py** (4 connections) — `src/backend/index.py`
- **utils.py** (3 connections) — `src/backend/utils.py`
- **_extract_result()** (3 connections) — `src/backend/utils.py`
- **_extract_race()** (3 connections) — `src/backend/utils.py`
- **_format_debug_state()** (3 connections) — `src/backend/utils.py`
- **detectors.py** (3 connections) — `src/backend/detectors.py`
- **test_debug.py** (2 connections) — `tests/test_debug.py`
- **test_debug_line_format()** (2 connections) — `tests/test_debug.py`
- **_handle_voice_command()** (2 connections) — `src/backend/index.py`
- **setup_logging()** (2 connections) — `src/backend/logger.py`
- **.ready()** (2 connections) — `src/backend/classes/cooldown_tracker.py`
- *... and 12 more nodes in this community*

## Relationships

- [[Game API & HUD Capture]] (5 shared connections)
- [[Message Banks & Tests]] (3 shared connections)
- [[TTS Speech Queue]] (2 shared connections)
- [[Config & Service Layer]] (1 shared connections)
- [[Game History Tracking]] (1 shared connections)
- [[Voice Listener]] (1 shared connections)

## Source Files

- `src/backend/classes/cooldown_tracker.py`
- `src/backend/detectors.py`
- `src/backend/index.py`
- `src/backend/logger.py`
- `src/backend/utils.py`
- `tests/test_debug.py`
- `tests/test_detectors.py`

## Audit Trail

- EXTRACTED: 78 (58%)
- INFERRED: 57 (42%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*