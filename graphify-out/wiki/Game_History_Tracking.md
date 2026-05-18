# Game History Tracking

> 15 nodes · cohesion 0.50

## Key Concepts

- **GameHistoryManager** (12 connections) — `src/backend/game_history.py`
- **._db_update_warnings()** (6 connections) — `src/backend/game_history.py`
- **get_db()** (5 connections) — `src/backend/db/__init__.py`
- **game_history.py** (3 connections) — `src/backend/game_history.py`
- **.on_game_end()** (3 connections) — `src/backend/game_history.py`
- **._db_create_game()** (3 connections) — `src/backend/game_history.py`
- **._db_end_game()** (3 connections) — `src/backend/game_history.py`
- **.on_game_start()** (2 connections) — `src/backend/game_history.py`
- **.on_mineral_warning()** (2 connections) — `src/backend/game_history.py`
- **.on_gas_warning()** (2 connections) — `src/backend/game_history.py`
- **.on_supply_warning()** (2 connections) — `src/backend/game_history.py`
- **.on_idle_workers_warning()** (2 connections) — `src/backend/game_history.py`
- **_format_duration()** (2 connections) — `src/backend/game_history.py`
- **.__init__()** (1 connections) — `src/backend/game_history.py`
- **counts()** (1 connections) — `src/backend/game_history.py`

## Relationships

- [[Settings & Messages UI]] (46 shared connections)
- [[Frontend Application]] (2 shared connections)
- [[Game State Detectors]] (1 shared connections)

## Source Files

- `src/backend/db/__init__.py`
- `src/backend/game_history.py`

## Audit Trail

- EXTRACTED: 41 (84%)
- INFERRED: 8 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*