# Config & Service Layer

> 27 nodes · cohesion 0.50

## Key Concepts

- **service.py** (9 connections) — `src/backend/service.py`
- **CoordsTab** (8 connections) — `src/frontend/views/tabs/coords_tab.py`
- **test_config_manager.py** (5 connections) — `tests/test_config_manager.py`
- **save_config()** (5 connections) — `src/backend/service.py`
- **get_config()** (4 connections) — `src/backend/service.py`
- **._build()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._capture()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._countdown()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **test_save_and_load_roundtrip()** (2 connections) — `tests/test_config_manager.py`
- **._handle_save()** (2 connections) — `src/frontend/app.py`
- **.__init__()** (2 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._save_coords()** (2 connections) — `src/frontend/views/tabs/coords_tab.py`
- **find_coords.py** (2 connections) — `src/backend/find_coords.py`
- **get_mouse_pos()** (2 connections) — `src/backend/find_coords.py`
- **test_load_config_returns_defaults_on_missing_file()** (1 connections) — `tests/test_config_manager.py`
- **test_default_screen_capture_has_all_hud_elements()** (1 connections) — `tests/test_config_manager.py`
- **test_load_config_returns_default_on_empty_file()** (1 connections) — `tests/test_config_manager.py`
- **Smoke tests for config load/save round-trips.** (1 connections) — `tests/test_config_manager.py`
- **coords_tab.py** (1 connections) — `src/frontend/views/tabs/coords_tab.py`
- **.refresh()** (1 connections) — `src/frontend/views/tabs/coords_tab.py`
- **_row_to_config()** (1 connections) — `src/backend/service.py`
- **_config_to_row()** (1 connections) — `src/backend/service.py`
- **_row_to_record()** (1 connections) — `src/backend/service.py`
- **_row_to_live()** (1 connections) — `src/backend/service.py`
- **get_live_stats()** (1 connections) — `src/backend/service.py`
- *... and 2 more nodes in this community*

## Relationships

- [[Frontend Application]] (2 shared connections)
- [[Settings & Messages UI]] (2 shared connections)
- [[History Dashboard]] (1 shared connections)
- [[Game API & HUD Capture]] (1 shared connections)
- [[Game State Detectors]] (1 shared connections)

## Source Files

- `src/backend/find_coords.py`
- `src/backend/service.py`
- `src/frontend/app.py`
- `src/frontend/views/tabs/coords_tab.py`
- `tests/test_config_manager.py`

## Audit Trail

- EXTRACTED: 52 (80%)
- INFERRED: 13 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*