# Dev Hot-reload Runner

> 7 nodes · cohesion 0.50

## Key Concepts

- **RestartHandler** (5 connections) — `dev.py`
- **.start()** (3 connections) — `dev.py`
- **dev.py** (2 connections) — `dev.py`
- **.__init__()** (2 connections) — `dev.py`
- **.on_modified()** (2 connections) — `dev.py`
- **FileSystemEventHandler** (1 connections)
- **Dev runner: watches src/ for .py changes and auto-restarts the app.** (1 connections) — `dev.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `dev.py`

## Audit Trail

- EXTRACTED: 16 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*