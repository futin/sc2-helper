# Project Architecture Docs

> 26 nodes · cohesion 0.50

## Key Concepts

- **detectors.py** (5 connections) — `docs/architecture.md`
- **service.py (Service Layer)** (5 connections) — `docs/architecture.md`
- **db/__init__.py (get_db context manager)** (4 connections) — `docs/architecture.md`
- **game_history.py (GameHistoryManager)** (4 connections) — `docs/architecture.md`
- **Custom Message Mode** (4 connections) — `docs/messages.md`
- **SC2 Helper** (3 connections) — `README.md`
- **Game History Tab (README)** (2 connections) — `README.md`
- **classes/speech_queue.py (SpeechQueue)** (2 connections) — `docs/architecture.md`
- **views/tabs/game_history_tab.py** (2 connections) — `docs/architecture.md`
- **logic/game_history_logic.py (GameHistoryLoader)** (2 connections) — `docs/architecture.md`
- **GameHistoryManager** (2 connections) — `docs/game_history.md`
- **config SQLite Table** (2 connections) — `docs/configuration.md`
- **Backend (src/backend/)** (1 connections) — `docs/architecture.md`
- **Frontend (src/frontend/)** (1 connections) — `docs/architecture.md`
- **classes/cooldown_tracker.py (CooldownTracker)** (1 connections) — `docs/architecture.md`
- **db/collection.py (Collection Query API)** (1 connections) — `docs/architecture.md`
- **db/schema.py (CREATE TABLE statements)** (1 connections) — `docs/architecture.md`
- **views/tabs/messages_tab.py** (1 connections) — `docs/architecture.md`
- **config_manager.py (Re-exports from service)** (1 connections) — `docs/architecture.md`
- **Game Lifecycle (start/end transitions)** (1 connections) — `docs/architecture.md`
- **TTS Priority Queue (supply > minerals > idle > gas)** (1 connections) — `docs/architecture.md`
- **Strict Message Mode** (1 connections) — `docs/messages.md`
- **Funny Message Mode** (1 connections) — `docs/messages.md`
- **game_stats SQLite Table** (1 connections) — `docs/game_history.md`
- **Service Layer Record Schema (get_stats_history)** (1 connections) — `docs/game_history.md`
- *... and 1 more nodes in this community*

## Relationships

- [[Config & Service Layer]] (50 shared connections)
- [[Game History Tracking]] (1 shared connections)

## Source Files

- `README.md`
- `docs/architecture.md`
- `docs/configuration.md`
- `docs/game_history.md`
- `docs/messages.md`

## Audit Trail

- EXTRACTED: 37 (73%)
- INFERRED: 14 (27%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*