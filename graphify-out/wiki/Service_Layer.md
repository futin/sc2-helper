# Service Layer

> 16 nodes · cohesion 0.12

## Key Concepts

- **service.py** (9 connections) — `src/backend/service.py`
- **save_config()** (5 connections) — `src/backend/service.py`
- **test_config_manager.py** (5 connections) — `tests/test_config_manager.py`
- **._handle_save()** (2 connections) — `src/frontend/app.py`
- **._save_coords()** (2 connections) — `src/frontend/views/tabs/coords_tab.py`
- **test_save_and_load_roundtrip()** (2 connections) — `tests/test_config_manager.py`
- **_config_to_row()** (1 connections) — `src/backend/service.py`
- **get_live_stats()** (1 connections) — `src/backend/service.py`
- **Service layer — the only entry point for frontend to access config and stats. Fr** (1 connections) — `src/backend/service.py`
- **_row_to_config()** (1 connections) — `src/backend/service.py`
- **_row_to_live()** (1 connections) — `src/backend/service.py`
- **_row_to_record()** (1 connections) — `src/backend/service.py`
- **Smoke tests for config load/save round-trips.** (1 connections) — `tests/test_config_manager.py`
- **test_default_screen_capture_has_all_hud_elements()** (1 connections) — `tests/test_config_manager.py`
- **test_load_config_returns_default_on_empty_file()** (1 connections) — `tests/test_config_manager.py`
- **test_load_config_returns_defaults_on_missing_file()** (1 connections) — `tests/test_config_manager.py`

## Relationships

- [[App Root & Entry Points]] (2 shared connections)
- [[Game API Polling]] (1 shared connections)
- [[Game History UI]] (1 shared connections)
- [[HUD Coordinate Capture]] (1 shared connections)

## Source Files

- `src/backend/service.py`
- `src/frontend/app.py`
- `src/frontend/views/tabs/coords_tab.py`
- `tests/test_config_manager.py`

## Audit Trail

- EXTRACTED: 28 (80%)
- INFERRED: 7 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*