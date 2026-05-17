# App Root & Entry Points

> 22 nodes · cohesion 0.12

## Key Concepts

- **SettingsScreen** (9 connections) — `src/frontend/views/settings_view.py`
- **SC2HelperApp** (8 connections) — `src/frontend/app.py`
- **MessagesTab** (6 connections) — `src/frontend/views/tabs/messages_tab.py`
- **._build()** (6 connections) — `src/frontend/views/settings_view.py`
- **._build()** (3 connections) — `src/frontend/app.py`
- **.__init__()** (3 connections) — `src/frontend/app.py`
- **._build()** (3 connections) — `src/frontend/views/tabs/messages_tab.py`
- **._save()** (3 connections) — `src/frontend/views/settings_view.py`
- **._open_runner()** (2 connections) — `src/frontend/app.py`
- **main()** (2 connections) — `src/frontend/sc2_ui.py`
- **sc2_ui.py** (2 connections) — `src/frontend/sc2_ui.py`
- **.__init__()** (2 connections) — `src/frontend/views/tabs/messages_tab.py`
- **._on_mode_change()** (2 connections) — `src/frontend/views/tabs/messages_tab.py`
- **._collect()** (2 connections) — `src/frontend/views/settings_view.py`
- **.__init__()** (2 connections) — `src/frontend/views/settings_view.py`
- **._on_tab_change()** (2 connections) — `src/frontend/views/settings_view.py`
- **.refresh()** (2 connections) — `src/frontend/views/settings_view.py`
- **Entry point for the SC2 Helper UI.** (1 connections) — `src/frontend/sc2_ui.py`
- **app.py** (1 connections) — `src/frontend/app.py`
- **settings_view.py** (1 connections) — `src/frontend/views/settings_view.py`
- **messages_tab.py** (1 connections) — `src/frontend/views/tabs/messages_tab.py`
- **.collect()** (1 connections) — `src/frontend/views/tabs/messages_tab.py`

## Relationships

- [[Service Layer]] (2 shared connections)
- [[Runner Controller]] (2 shared connections)
- [[Game API Polling]] (1 shared connections)
- [[Config UI]] (1 shared connections)
- [[HUD Coordinate Capture]] (1 shared connections)
- [[Game History UI]] (1 shared connections)

## Source Files

- `src/frontend/app.py`
- `src/frontend/sc2_ui.py`
- `src/frontend/views/settings_view.py`
- `src/frontend/views/tabs/messages_tab.py`

## Audit Trail

- EXTRACTED: 49 (77%)
- INFERRED: 15 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*