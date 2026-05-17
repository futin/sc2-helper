# HUD Coordinate Capture

> 10 nodes · cohesion 0.27

## Key Concepts

- **CoordsTab** (8 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._build()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._capture()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **._countdown()** (3 connections) — `src/frontend/views/tabs/coords_tab.py`
- **get_mouse_pos()** (2 connections) — `src/backend/find_coords.py`
- **find_coords.py** (2 connections) — `src/backend/find_coords.py`
- **.__init__()** (2 connections) — `src/frontend/views/tabs/coords_tab.py`
- **Move mouse over each SC2 HUD element. Press Enter in terminal to record position** (1 connections) — `src/backend/find_coords.py`
- **coords_tab.py** (1 connections) — `src/frontend/views/tabs/coords_tab.py`
- **.refresh()** (1 connections) — `src/frontend/views/tabs/coords_tab.py`

## Relationships

- [[App Root & Entry Points]] (1 shared connections)
- [[Service Layer]] (1 shared connections)

## Source Files

- `src/backend/find_coords.py`
- `src/frontend/views/tabs/coords_tab.py`

## Audit Trail

- EXTRACTED: 23 (88%)
- INFERRED: 3 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*