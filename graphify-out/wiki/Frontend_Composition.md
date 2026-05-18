# Frontend Composition

> 16 nodes · cohesion 0.50

## Key Concepts

- **SettingsScreen** (5 connections) — `src/frontend/views/settings_view.py`
- **frontend/config_manager.py** (4 connections) — `src/frontend/config_manager.py`
- **SC2HelperApp** (4 connections) — `src/frontend/app.py`
- **RestartHandler** (2 connections) — `dev.py`
- **RunnerController** (2 connections) — `src/frontend/logic/runner_logic.py`
- **RunnerScreen** (2 connections) — `src/frontend/views/runner_view.py`
- **CoordsTab** (2 connections) — `src/frontend/views/tabs/coords_tab.py`
- **ConfigTab** (2 connections) — `src/frontend/views/tabs/config_tab.py`
- **GameHistoryTab** (2 connections) — `src/frontend/views/tabs/game_history_tab.py`
- **dev.py __main__** (1 connections) — `dev.py`
- **test_save_and_load_roundtrip** (1 connections) — `tests/test_config_manager.py`
- **test_default_screen_capture_has_all_hud_elements** (1 connections) — `tests/test_config_manager.py`
- **sc2_ui main** (1 connections) — `src/frontend/sc2_ui.py`
- **GameHistoryLoader** (1 connections) — `src/frontend/logic/game_history_logic.py`
- **MessagesTab** (1 connections) — `src/frontend/views/tabs/messages_tab.py`
- **Voice Control Configuration Design** (1 connections) — `src/frontend/views/tabs/config_tab.py`

## Relationships

- [[Game History Tracking]] (32 shared connections)

## Source Files

- `dev.py`
- `src/frontend/app.py`
- `src/frontend/config_manager.py`
- `src/frontend/logic/game_history_logic.py`
- `src/frontend/logic/runner_logic.py`
- `src/frontend/sc2_ui.py`
- `src/frontend/views/runner_view.py`
- `src/frontend/views/settings_view.py`
- `src/frontend/views/tabs/config_tab.py`
- `src/frontend/views/tabs/coords_tab.py`
- `src/frontend/views/tabs/game_history_tab.py`
- `src/frontend/views/tabs/messages_tab.py`
- `tests/test_config_manager.py`

## Audit Trail

- EXTRACTED: 20 (62%)
- INFERRED: 12 (38%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*