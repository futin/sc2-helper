# Graph Report - sc2-helper  (2026-05-17)

## Corpus Check
- 42 files · ~10,931 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 320 nodes · 442 edges · 38 communities (27 shown, 11 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd202129`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Game API Polling|Game API Polling]]
- [[_COMMUNITY_DB Collection Layer|DB Collection Layer]]
- [[_COMMUNITY_Game Detectors & Alerts|Game Detectors & Alerts]]
- [[_COMMUNITY_Architecture Overview|Architecture Overview]]
- [[_COMMUNITY_App Root & Entry Points|App Root & Entry Points]]
- [[_COMMUNITY_Runner Controller|Runner Controller]]
- [[_COMMUNITY_Module Documentation|Module Documentation]]
- [[_COMMUNITY_Service Layer|Service Layer]]
- [[_COMMUNITY_Config UI|Config UI]]
- [[_COMMUNITY_Game History DB|Game History DB]]
- [[_COMMUNITY_Game History UI|Game History UI]]
- [[_COMMUNITY_TTS Speech Queue|TTS Speech Queue]]
- [[_COMMUNITY_HUD Coordinate Capture|HUD Coordinate Capture]]
- [[_COMMUNITY_Backend OCR Debug Images|Backend OCR Debug Images]]
- [[_COMMUNITY_OCR Debug Images|OCR Debug Images]]
- [[_COMMUNITY_Dev Hot-Reload|Dev Hot-Reload]]
- [[_COMMUNITY_Dev Mode Docs|Dev Mode Docs]]
- [[_COMMUNITY_UI Entry Point|UI Entry Point]]
- [[_COMMUNITY_DB Connectors|DB Connectors]]
- [[_COMMUNITY_HUD Element Config|HUD Element Config]]
- [[_COMMUNITY_HudElement Dataclass|HudElement Dataclass]]
- [[_COMMUNITY_HTTP Dependency|HTTP Dependency]]
- [[_COMMUNITY_Test Dependency|Test Dependency]]
- [[_COMMUNITY_Constants Module|Constants Module]]
- [[_COMMUNITY_Utils Module|Utils Module]]
- [[_COMMUNITY_Logger Module|Logger Module]]
- [[_COMMUNITY_Message Banks Docs|Message Banks Docs]]
- [[_COMMUNITY_Calibration Script Docs|Calibration Script Docs]]
- [[_COMMUNITY_Settings View Docs|Settings View Docs]]
- [[_COMMUNITY_Config Tab Docs|Config Tab Docs]]

## God Nodes (most connected - your core abstractions)
1. `ConfigTab` - 16 edges
2. `main()` - 16 edges
3. `RunnerScreen` - 15 edges
4. `GameHistoryManager` - 12 edges
5. `CooldownTracker` - 11 edges
6. `SQLiteConnector` - 10 edges
7. `Collection` - 10 edges
8. `_make_speech()` - 9 edges
9. `SettingsScreen` - 9 edges
10. `GameHistoryTab` - 9 edges

## Surprising Connections (you probably didn't know these)
- `views/tabs/game_history_tab.py` --semantically_similar_to--> `Game History Tab (README)`  [INFERRED] [semantically similar]
  docs/architecture.md → README.md
- `_make_speech()` --calls--> `SpeechQueue`  [INFERRED]
  tests/test_detectors.py → src/backend/classes/speech_queue.py
- `test_speak_enqueues_without_error()` --calls--> `SpeechQueue`  [INFERRED]
  tests/test_speech_queue.py → src/backend/classes/speech_queue.py
- `test_counter_increments()` --calls--> `SpeechQueue`  [INFERRED]
  tests/test_speech_queue.py → src/backend/classes/speech_queue.py
- `test_strict_mode_returns_exact_string()` --calls--> `get_message()`  [INFERRED]
  tests/test_messages.py → src/backend/messages.py

## Hyperedges (group relationships)
- **OCR Pipeline: mss capture → pytesseract → spike filter → detector** — architecture_ocrpy, architecture_gameapipy, architecture_spikefilter, architecture_detectorspy [EXTRACTED 0.95]
- **SQLite Storage Layer: schema, connector, collection, service** — architecture_schemapy, architecture_sqliteconnectorpy, architecture_collectionpy, architecture_servicepy [EXTRACTED 0.95]
- **Debug HUD Feature: spec, plan, --debug flag, RunnerScreen checkbox** — spec_debughuds, plan_debughuds, running_debugmode, plan_debugcheckbox [EXTRACTED 0.95]

## Communities (38 total, 11 thin omitted)

### Community 0 - "Game API Polling"
Cohesion: 0.09
Nodes (28): _capture_hud(), fetch_game_state(), _filter_spikes(), is_game_running(), _poll_game(), Return (is_running, players). Single API call reused by main loop., Return True if SC2 is running and a game is in progress., Capture HUD via screen OCR. Assumes game is already confirmed running. (+20 more)

### Community 1 - "DB Collection Layer"
Cohesion: 0.09
Nodes (8): ABC, _build_set(), _build_where(), Collection, DBConnector, ensure_tables(), SQLiteConnector, DBConnector

### Community 2 - "Game Detectors & Alerts"
Cohesion: 0.13
Nodes (22): check_idle_workers(), check_resources(), check_supply(), Track idle workers. Returns updated idle_onset (or None if busy)., get_message(), CooldownTracker, Return True (and record the time) if the cooldown has elapsed., _make_speech() (+14 more)

### Community 3 - "Architecture Overview"
Cohesion: 0.08
Nodes (26): Backend (src/backend/), db/collection.py (Collection Query API), config_manager.py (Re-exports from service), classes/cooldown_tracker.py (CooldownTracker), db/__init__.py (get_db context manager), detectors.py, Frontend (src/frontend/), logic/game_history_logic.py (GameHistoryLoader) (+18 more)

### Community 4 - "App Root & Entry Points"
Cohesion: 0.12
Nodes (5): SC2HelperApp, main(), Entry point for the SC2 Helper UI., MessagesTab, SettingsScreen

### Community 5 - "Runner Controller"
Cohesion: 0.13
Nodes (3): Start the backend process. Returns False if already running., RunnerController, RunnerScreen

### Community 6 - "Module Documentation"
Cohesion: 0.13
Nodes (19): game_api.py (SC2 API Polling), index.py (Backend Entry Point), ocr.py (Screen Capture + OCR), logic/runner_logic.py (RunnerController), views/runner_view.py (RunnerScreen), Spike Filter (OCR Anomaly Suppression), Anomaly Filter Config, Debug Mode Checkbox (RunnerScreen) (+11 more)

### Community 7 - "Service Layer"
Cohesion: 0.12
Nodes (4): Service layer — the only entry point for frontend to access config and stats. Fr, save_config(), Smoke tests for config load/save round-trips., test_save_and_load_roundtrip()

### Community 9 - "Game History DB"
Cohesion: 0.22
Nodes (3): _format_duration(), GameHistoryManager, get_db()

### Community 10 - "Game History UI"
Cohesion: 0.26
Nodes (3): get_stats_history(), GameHistoryLoader, GameHistoryTab

### Community 11 - "TTS Speech Queue"
Cohesion: 0.22
Nodes (6): SpeechQueue, Smoke tests for SpeechQueue — no actual TTS subprocess spawned., Lower priority number = higher urgency = dequeued first., test_counter_increments(), test_priority_ordering(), test_speak_enqueues_without_error()

### Community 12 - "HUD Coordinate Capture"
Cohesion: 0.27
Nodes (3): get_mouse_pos(), Move mouse over each SC2 HUD element. Press Enter in terminal to record position, CoordsTab

### Community 13 - "Backend OCR Debug Images"
Cohesion: 0.33
Nodes (9): Gas HUD Crop Processed (backend), Gas HUD Crop Raw (backend), Idle Workers HUD Crop Processed (backend), Idle Workers HUD Crop Raw (backend), Minerals HUD Crop Processed (backend), Minerals HUD Crop Raw (backend), OCR Module (backend), Supply HUD Crop Processed (backend) (+1 more)

### Community 14 - "OCR Debug Images"
Cohesion: 0.5
Nodes (8): Gas HUD Crop (Processed), Gas HUD Crop (Raw), Idle Workers HUD Crop (Processed), Idle Workers HUD Crop (Raw), Minerals HUD Crop (Processed), Minerals HUD Crop (Raw), Supply HUD Crop (Processed), Supply HUD Crop (Raw)

### Community 15 - "Dev Hot-Reload"
Cohesion: 0.38
Nodes (3): FileSystemEventHandler, Dev runner: watches src/ for .py changes and auto-restarts the app., RestartHandler

### Community 16 - "Dev Mode Docs"
Cohesion: 1.0
Nodes (3): dev.py (Hot-reload runner), watchdog (dependency), Dev Mode (hot-reload via dev.py)

### Community 17 - "UI Entry Point"
Cohesion: 0.67
Nodes (3): app.py (SC2HelperApp Root Window), sc2_ui.py (UI Entry Point), customtkinter (dependency)

### Community 18 - "DB Connectors"
Cohesion: 0.67
Nodes (3): db/connector.py (DB Abstraction Base), db/sqlite_connector.py (aiosqlite impl), aiosqlite (dependency)

### Community 19 - "HUD Element Config"
Cohesion: 0.67
Nodes (3): views/tabs/coords_tab.py, hud_elements.py (HudElement + HUD_ELEMENTS), Screen Capture Regions Config

## Knowledge Gaps
- **61 isolated node(s):** `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Smoke tests for SpeechQueue — no actual TTS subprocess spawned.`, `Lower priority number = higher urgency = dequeued first.`, `Smoke tests for message selection logic.` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Game API Polling` to `Game History DB`, `Game Detectors & Alerts`, `TTS Speech Queue`?**
  _High betweenness centrality (0.319) - this node is a cross-community bridge._
- **Why does `get_config()` connect `Game API Polling` to `App Root & Entry Points`, `Service Layer`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Why does `GameHistoryManager` connect `Game History DB` to `Game API Polling`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `main()` (e.g. with `setup_logging()` and `get_config()`) actually correct?**
  _`main()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `RunnerScreen` (e.g. with `SC2HelperApp` and `RunnerController`) actually correct?**
  _`RunnerScreen` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `CooldownTracker` (e.g. with `test_check_resources_no_speak_below_threshold()` and `test_check_resources_speaks_when_over_threshold()`) actually correct?**
  _`CooldownTracker` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Smoke tests for SpeechQueue — no actual TTS subprocess spawned.` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._