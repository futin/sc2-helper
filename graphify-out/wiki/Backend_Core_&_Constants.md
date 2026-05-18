# Backend Core & Constants

> 55 nodes · cohesion 0.50

## Key Concepts

- **main** (14 connections) — `src/backend/index.py`
- **get_db** (11 connections) — `src/backend/db/__init__.py`
- **check_resources** (9 connections) — `src/backend/detectors.py`
- **check_supply** (7 connections) — `src/backend/detectors.py`
- **check_idle_workers** (6 connections) — `src/backend/detectors.py`
- **get_config** (5 connections) — `src/backend/service.py`
- **SpeechQueue.speak** (5 connections) — `src/backend/classes/speech_queue.py`
- **get_message** (4 connections) — `src/backend/messages.py`
- **_poll_game** (4 connections) — `src/backend/game_api.py`
- **get_stats_history** (3 connections) — `src/backend/service.py`
- **DEFAULT_CONFIG** (3 connections) — `src/backend/service.py`
- **_handle_voice_command** (3 connections) — `src/backend/index.py`
- **GameHistoryManager.on_game_end** (3 connections) — `src/backend/game_history.py`
- **_extract_race** (3 connections) — `src/backend/utils.py`
- **_capture_hud** (3 connections) — `src/backend/game_api.py`
- **CooldownTracker.ready** (3 connections) — `src/backend/classes/cooldown_tracker.py`
- **SQLiteConnector** (3 connections) — `src/backend/db/sqlite_connector.py`
- **save_config** (2 connections) — `src/backend/service.py`
- **get_live_stats** (2 connections) — `src/backend/service.py`
- **_config_to_row** (2 connections) — `src/backend/service.py`
- **GameHistoryManager.on_game_start** (2 connections) — `src/backend/game_history.py`
- **GameHistoryManager.on_mineral_warning** (2 connections) — `src/backend/game_history.py`
- **GameHistoryManager.on_gas_warning** (2 connections) — `src/backend/game_history.py`
- **GameHistoryManager.on_supply_warning** (2 connections) — `src/backend/game_history.py`
- **GameHistoryManager.on_idle_workers_warning** (2 connections) — `src/backend/game_history.py`
- *... and 30 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `ideas/improvement-ideas.md`
- `src/backend/classes/cooldown_tracker.py`
- `src/backend/classes/speech_queue.py`
- `src/backend/constants.py`
- `src/backend/db/__init__.py`
- `src/backend/db/connector.py`
- `src/backend/db/schema.py`
- `src/backend/db/sqlite_connector.py`
- `src/backend/detectors.py`
- `src/backend/find_coords.py`
- `src/backend/game_api.py`
- `src/backend/game_history.py`
- `src/backend/hud_elements.py`
- `src/backend/index.py`
- `src/backend/logger.py`
- `src/backend/messages.py`
- `src/backend/service.py`
- `src/backend/utils.py`

## Audit Trail

- EXTRACTED: 114 (79%)
- INFERRED: 30 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*