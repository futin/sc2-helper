# Runner Controller

> 21 nodes · cohesion 0.13

## Key Concepts

- **RunnerScreen** (15 connections) — `src/frontend/views/runner_view.py`
- **RunnerController** (8 connections) — `src/frontend/logic/runner_logic.py`
- **._append_log()** (4 connections) — `src/frontend/views/runner_view.py`
- **._build()** (3 connections) — `src/frontend/views/runner_view.py`
- **.__init__()** (3 connections) — `src/frontend/views/runner_view.py`
- **._update_status()** (3 connections) — `src/frontend/views/runner_view.py`
- **.start()** (2 connections) — `src/frontend/logic/runner_logic.py`
- **._build_tracking()** (2 connections) — `src/frontend/views/runner_view.py`
- **._reset_tracking()** (2 connections) — `src/frontend/views/runner_view.py`
- **._start()** (2 connections) — `src/frontend/views/runner_view.py`
- **._stop()** (2 connections) — `src/frontend/views/runner_view.py`
- **Start the backend process. Returns False if already running.** (1 connections) — `src/frontend/logic/runner_logic.py`
- **._check_queue()** (1 connections) — `src/frontend/logic/runner_logic.py`
- **.__init__()** (1 connections) — `src/frontend/logic/runner_logic.py`
- **._read_output()** (1 connections) — `src/frontend/logic/runner_logic.py`
- **.stop()** (1 connections) — `src/frontend/logic/runner_logic.py`
- **runner_logic.py** (1 connections) — `src/frontend/logic/runner_logic.py`
- **runner_view.py** (1 connections) — `src/frontend/views/runner_view.py`
- **._clear_log()** (1 connections) — `src/frontend/views/runner_view.py`
- **._on_close()** (1 connections) — `src/frontend/views/runner_view.py`
- **._update_tracking()** (1 connections) — `src/frontend/views/runner_view.py`

## Relationships

- [[App Root & Entry Points]] (2 shared connections)

## Source Files

- `src/frontend/logic/runner_logic.py`
- `src/frontend/views/runner_view.py`

## Audit Trail

- EXTRACTED: 50 (89%)
- INFERRED: 6 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*