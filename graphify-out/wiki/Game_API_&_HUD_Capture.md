# Game API & HUD Capture

> 20 nodes · cohesion 0.50

## Key Concepts

- **test_ocr_mode()** (8 connections) — `src/backend/index.py`
- **_capture_hud()** (7 connections) — `src/backend/game_api.py`
- **ocr_number()** (5 connections) — `src/backend/ocr.py`
- **ocr_supply()** (5 connections) — `src/backend/ocr.py`
- **game_api.py** (5 connections) — `src/backend/game_api.py`
- **ocr.py** (4 connections) — `src/backend/ocr.py`
- **capture_region()** (4 connections) — `src/backend/ocr.py`
- **_preprocess()** (4 connections) — `src/backend/ocr.py`
- **_poll_game()** (4 connections) — `src/backend/game_api.py`
- **is_game_running()** (4 connections) — `src/backend/game_api.py`
- **fetch_game_state()** (4 connections) — `src/backend/game_api.py`
- **_filter_spikes()** (2 connections) — `src/backend/game_api.py`
- **Capture each configured region, save crops, print OCR results.** (1 connections) — `src/backend/index.py`
- **Capture a screen region. region = [left, top, width, height].** (1 connections) — `src/backend/ocr.py`
- **OCR a single integer from a HUD region. Returns None on failure.** (1 connections) — `src/backend/ocr.py`
- **OCR supply region. Returns (used, max) or (None, None) on failure.** (1 connections) — `src/backend/ocr.py`
- **Return (is_running, players). Single API call reused by main loop.** (1 connections) — `src/backend/game_api.py`
- **Return True if SC2 is running and a game is in progress.** (1 connections) — `src/backend/game_api.py`
- **Capture HUD via screen OCR. Assumes game is already confirmed running.** (1 connections) — `src/backend/game_api.py`
- **Capture current game state via screen OCR. Returns None if game not running.** (1 connections) — `src/backend/game_api.py`

## Relationships

- [[Core Module Docs]] (58 shared connections)
- [[Game State Detectors]] (5 shared connections)
- [[Database Query Layer]] (1 shared connections)

## Source Files

- `src/backend/game_api.py`
- `src/backend/index.py`
- `src/backend/ocr.py`

## Audit Trail

- EXTRACTED: 46 (72%)
- INFERRED: 18 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*