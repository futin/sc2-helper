# Game Detectors & Alerts

> 29 nodes · cohesion 0.13

## Key Concepts

- **CooldownTracker** (11 connections) — `src/backend/classes/cooldown_tracker.py`
- **get_message()** (9 connections) — `src/backend/messages.py`
- **_make_speech()** (9 connections) — `tests/test_detectors.py`
- **test_detectors.py** (9 connections) — `tests/test_detectors.py`
- **check_idle_workers()** (6 connections) — `src/backend/detectors.py`
- **check_resources()** (6 connections) — `src/backend/detectors.py`
- **test_messages.py** (6 connections) — `tests/test_messages.py`
- **check_supply()** (5 connections) — `src/backend/detectors.py`
- **test_check_idle_workers_resets_on_zero()** (4 connections) — `tests/test_detectors.py`
- **test_check_idle_workers_speaks_when_idle()** (4 connections) — `tests/test_detectors.py`
- **test_check_resources_cooldown_prevents_repeat()** (4 connections) — `tests/test_detectors.py`
- **test_check_resources_no_speak_below_threshold()** (4 connections) — `tests/test_detectors.py`
- **test_check_resources_speaks_when_over_threshold()** (4 connections) — `tests/test_detectors.py`
- **test_check_supply_silent_when_ok()** (4 connections) — `tests/test_detectors.py`
- **test_check_supply_speaks_when_capped()** (4 connections) — `tests/test_detectors.py`
- **detectors.py** (3 connections) — `src/backend/detectors.py`
- **.ready()** (2 connections) — `src/backend/classes/cooldown_tracker.py`
- **test_custom_mode_falls_back_to_strict_when_empty()** (2 connections) — `tests/test_messages.py`
- **test_custom_mode_falls_back_when_category_missing()** (2 connections) — `tests/test_messages.py`
- **test_custom_mode_uses_custom_messages()** (2 connections) — `tests/test_messages.py`
- **test_funny_mode_returns_non_empty()** (2 connections) — `tests/test_messages.py`
- **test_strict_mode_returns_exact_string()** (2 connections) — `tests/test_messages.py`
- **Track idle workers. Returns updated idle_onset (or None if busy).** (1 connections) — `src/backend/detectors.py`
- **.__init__()** (1 connections) — `src/backend/classes/cooldown_tracker.py`
- **Return True (and record the time) if the cooldown has elapsed.** (1 connections) — `src/backend/classes/cooldown_tracker.py`
- *... and 4 more nodes in this community*

## Relationships

- [[Game API Polling]] (4 shared connections)
- [[TTS Speech Queue]] (1 shared connections)

## Source Files

- `src/backend/classes/cooldown_tracker.py`
- `src/backend/detectors.py`
- `src/backend/messages.py`
- `tests/test_detectors.py`
- `tests/test_messages.py`

## Audit Trail

- EXTRACTED: 62 (56%)
- INFERRED: 49 (44%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*