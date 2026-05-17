# Game API Polling

> 35 nodes · cohesion 0.09

## Key Concepts

- **main()** (16 connections) — `src/backend/index.py`
- **test_ocr_mode()** (8 connections) — `src/backend/index.py`
- **_capture_hud()** (7 connections) — `src/backend/game_api.py`
- **ocr_number()** (5 connections) — `src/backend/ocr.py`
- **ocr_supply()** (5 connections) — `src/backend/ocr.py`
- **game_api.py** (5 connections) — `src/backend/game_api.py`
- **fetch_game_state()** (4 connections) — `src/backend/game_api.py`
- **is_game_running()** (4 connections) — `src/backend/game_api.py`
- **_poll_game()** (4 connections) — `src/backend/game_api.py`
- **capture_region()** (4 connections) — `src/backend/ocr.py`
- **_preprocess()** (4 connections) — `src/backend/ocr.py`
- **get_config()** (4 connections) — `src/backend/service.py`
- **ocr.py** (4 connections) — `src/backend/ocr.py`
- **_extract_race()** (3 connections) — `src/backend/utils.py`
- **_extract_result()** (3 connections) — `src/backend/utils.py`
- **_format_debug_state()** (3 connections) — `src/backend/utils.py`
- **index.py** (3 connections) — `src/backend/index.py`
- **utils.py** (3 connections) — `src/backend/utils.py`
- **_filter_spikes()** (2 connections) — `src/backend/game_api.py`
- **setup_logging()** (2 connections) — `src/backend/logger.py`
- **test_debug.py** (2 connections) — `tests/test_debug.py`
- **test_debug_line_format()** (2 connections) — `tests/test_debug.py`
- **Return (is_running, players). Single API call reused by main loop.** (1 connections) — `src/backend/game_api.py`
- **Return True if SC2 is running and a game is in progress.** (1 connections) — `src/backend/game_api.py`
- **Capture HUD via screen OCR. Assumes game is already confirmed running.** (1 connections) — `src/backend/game_api.py`
- *... and 10 more nodes in this community*

## Relationships

- [[Game Detectors & Alerts]] (4 shared connections)
- [[TTS Speech Queue]] (1 shared connections)
- [[Game History DB]] (1 shared connections)
- [[App Root & Entry Points]] (1 shared connections)
- [[Service Layer]] (1 shared connections)

## Source Files

- `src/backend/game_api.py`
- `src/backend/index.py`
- `src/backend/logger.py`
- `src/backend/ocr.py`
- `src/backend/service.py`
- `src/backend/utils.py`
- `tests/test_debug.py`

## Audit Trail

- EXTRACTED: 69 (63%)
- INFERRED: 41 (37%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*