# Graph Report - sc2-helper  (2026-05-18)

## Corpus Check
- 46 files · ~15,679 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 476 nodes · 616 edges · 69 communities (31 shown, 38 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 150 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3f35d9de`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Backend Core & Constants|Backend Core & Constants]]
- [[_COMMUNITY_Game State Detectors|Game State Detectors]]
- [[_COMMUNITY_Database Query Layer|Database Query Layer]]
- [[_COMMUNITY_Frontend Application|Frontend Application]]
- [[_COMMUNITY_Config & Service Layer|Config & Service Layer]]
- [[_COMMUNITY_Project Architecture Docs|Project Architecture Docs]]
- [[_COMMUNITY_Game API & HUD Capture|Game API & HUD Capture]]
- [[_COMMUNITY_Config UI Tab|Config UI Tab]]
- [[_COMMUNITY_Core Module Docs|Core Module Docs]]
- [[_COMMUNITY_Frontend Composition|Frontend Composition]]
- [[_COMMUNITY_Game History Tracking|Game History Tracking]]
- [[_COMMUNITY_Settings & Messages UI|Settings & Messages UI]]
- [[_COMMUNITY_History Dashboard|History Dashboard]]
- [[_COMMUNITY_TTS Speech Queue|TTS Speech Queue]]
- [[_COMMUNITY_Voice Listener|Voice Listener]]
- [[_COMMUNITY_Message Banks & Tests|Message Banks & Tests]]
- [[_COMMUNITY_Backend HUD Images|Backend HUD Images]]
- [[_COMMUNITY_Frontend HUD Images|Frontend HUD Images]]
- [[_COMMUNITY_Dev Hot-reload Runner|Dev Hot-reload Runner]]
- [[_COMMUNITY_Voice Command Parsing|Voice Command Parsing]]
- [[_COMMUNITY_HUD Coordinate Config|HUD Coordinate Config]]
- [[_COMMUNITY_Resource Detector Tests|Resource Detector Tests]]
- [[_COMMUNITY_Background Thread Classes|Background Thread Classes]]
- [[_COMMUNITY_HUD Element Model|HUD Element Model]]
- [[_COMMUNITY_DB Connector Abstraction|DB Connector Abstraction]]
- [[_COMMUNITY_App Entry Point|App Entry Point]]
- [[_COMMUNITY_Dev Mode Docs|Dev Mode Docs]]
- [[_COMMUNITY_Supply Detector Tests|Supply Detector Tests]]
- [[_COMMUNITY_Idle Worker Tests|Idle Worker Tests]]
- [[_COMMUNITY_Debug Format Tests|Debug Format Tests]]
- [[_COMMUNITY_Speech Queue Tests|Speech Queue Tests]]
- [[_COMMUNITY_Custom Message Tests|Custom Message Tests]]
- [[_COMMUNITY_Config Load Tests|Config Load Tests]]
- [[_COMMUNITY_Collection DB Bridge|Collection DB Bridge]]
- [[_COMMUNITY_Collection Query Methods|Collection Query Methods]]
- [[_COMMUNITY_Config Manager Module|Config Manager Module]]
- [[_COMMUNITY_Utilities Module|Utilities Module]]
- [[_COMMUNITY_Logger Module|Logger Module]]
- [[_COMMUNITY_Message Banks Module|Message Banks Module]]
- [[_COMMUNITY_HUD Calibration Script|HUD Calibration Script]]
- [[_COMMUNITY_Settings Screen Module|Settings Screen Module]]
- [[_COMMUNITY_Config Tab Module|Config Tab Module]]
- [[_COMMUNITY_Counter Test|Counter Test]]
- [[_COMMUNITY_Strict Mode Test|Strict Mode Test]]
- [[_COMMUNITY_Funny Mode Test|Funny Mode Test]]
- [[_COMMUNITY_Custom Mode Test|Custom Mode Test]]
- [[_COMMUNITY_Game History Manager|Game History Manager]]
- [[_COMMUNITY_HUD Element Class|HUD Element Class]]
- [[_COMMUNITY_HUD Element Keys|HUD Element Keys]]
- [[_COMMUNITY_Strict Message Bank|Strict Message Bank]]
- [[_COMMUNITY_Supply Message Bank|Supply Message Bank]]
- [[_COMMUNITY_Mineral Message Bank|Mineral Message Bank]]
- [[_COMMUNITY_Idle Worker Message Bank|Idle Worker Message Bank]]
- [[_COMMUNITY_Gas Message Bank|Gas Message Bank]]
- [[_COMMUNITY_Cooldown Remaining|Cooldown Remaining]]
- [[_COMMUNITY_DB Path|DB Path]]
- [[_COMMUNITY_Collection Create|Collection Create]]
- [[_COMMUNITY_Collection Update|Collection Update]]
- [[_COMMUNITY_Config Table Schema|Config Table Schema]]
- [[_COMMUNITY_Game Stats Table Schema|Game Stats Table Schema]]
- [[_COMMUNITY_Community 68|Community 68]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 19 edges
2. `ConfigTab` - 17 edges
3. `RunnerScreen` - 15 edges
4. `main` - 14 edges
5. `WakeWordDetector` - 13 edges
6. `GameHistoryManager` - 12 edges
7. `CooldownTracker` - 12 edges
8. `get_db` - 11 edges
9. `_make_listener()` - 10 edges
10. `VoiceListener` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Smarter Contextual Detection` --semantically_similar_to--> `_filter_spikes`  [INFERRED] [semantically similar]
  ideas/improvement-ideas.md → src/backend/game_api.py
- `Banking Mode Toggle` --conceptually_related_to--> `check_resources`  [INFERRED]
  ideas/improvement-ideas.md → src/backend/detectors.py
- `Warning Intensity Scaling` --conceptually_related_to--> `check_supply`  [INFERRED]
  ideas/improvement-ideas.md → src/backend/detectors.py
- `views/tabs/game_history_tab.py` --semantically_similar_to--> `Game History Tab (README)`  [INFERRED] [semantically similar]
  docs/architecture.md → README.md
- `RestartHandler` --semantically_similar_to--> `RunnerController`  [INFERRED] [semantically similar]
  dev.py → src/frontend/logic/runner_logic.py

## Hyperedges (group relationships)
- **OCR Pipeline: mss capture → pytesseract → spike filter → detector** — architecture_ocrpy, architecture_gameapipy, architecture_spikefilter, architecture_detectorspy [EXTRACTED 0.95]
- **SQLite Storage Layer: schema, connector, collection, service** — architecture_schemapy, architecture_sqliteconnectorpy, architecture_collectionpy, architecture_servicepy [EXTRACTED 0.95]
- **Debug HUD Feature: spec, plan, --debug flag, RunnerScreen checkbox** — spec_debughuds, plan_debughuds, running_debugmode, plan_debugcheckbox [EXTRACTED 0.95]
- **Frontend Tab Collect and Save Flow** — config_tab_configtab, messages_tab_messagestab, settings_view_settingsscreen, config_manager_module [EXTRACTED 0.95]
- **Runner Subprocess Lifecycle** — runner_view_runnerscreen, runner_logic_runnercontroller, app_sc2helperapp [EXTRACTED 0.95]
- **Detector Tests Suite** — test_detectors_test_check_resources_no_speak_below_threshold, test_detectors_test_check_supply_speaks_when_capped, test_detectors_test_check_idle_workers_speaks_when_idle [EXTRACTED 0.95]
- **Main Game Loop Pipeline** — index_main, game_api_pollgame, game_api_capturehud, game_api_filterspikes, detectors_checkresources, detectors_checksupply, detectors_checkidleworkers, speech_queue_speak [EXTRACTED 0.95]
- **Warning Detection and History Tracking** — detectors_checkresources, detectors_checksupply, detectors_checkidleworkers, game_history_gamehistorymanager, schema_gamestatstable [EXTRACTED 0.95]
- **Voice Control Command Flow** — voice_listener_voicelistener, voice_listener_voicecommand, index_handlevoicecommand, speech_queue_speak [EXTRACTED 0.95]

## Communities (69 total, 38 thin omitted)

### Community 0 - "Backend Core & Constants"
Cohesion: 0.05
Nodes (55): DBConnector, PRIORITY_GAS, PRIORITY_IDLE_WORKERS, PRIORITY_MINERALS, PRIORITY_SUPPLY, PRIORITY_VOICE_RESPONSE, _RACE_MAP, REQUEST_TIMEOUT (+47 more)

### Community 1 - "Game State Detectors"
Cohesion: 0.06
Nodes (13): get_config(), Service layer — the only entry point for frontend to access config and stats. Fr, save_config(), SC2HelperApp, main(), Entry point for the SC2 Helper UI., MessagesTab, Smoke tests for config get/save round-trips. (+5 more)

### Community 2 - "Database Query Layer"
Cohesion: 0.09
Nodes (26): check_idle_workers(), check_resources(), check_supply(), Track idle workers. Returns updated idle_onset (or None if busy)., _handle_voice_command(), main(), SC2 Helper — captures the StarCraft II HUD via screen OCR and speaks audio warni, setup_logging() (+18 more)

### Community 3 - "Frontend Application"
Cohesion: 0.09
Nodes (8): ABC, _build_set(), _build_where(), Collection, DBConnector, ensure_tables(), SQLiteConnector, DBConnector

### Community 4 - "Config & Service Layer"
Cohesion: 0.13
Nodes (3): Start the backend process. Returns False if already running., RunnerController, RunnerScreen

### Community 5 - "Project Architecture Docs"
Cohesion: 0.16
Nodes (12): Voice listener — background thread that listens for a wake word then transcribes, VoiceCommand, VoiceListener, _make_listener(), test_handle_wake_enqueues_command(), test_handle_wake_missing_import_does_not_raise(), test_handle_wake_timeout_does_not_enqueue(), test_parse_resources() (+4 more)

### Community 6 - "Game API & HUD Capture"
Cohesion: 0.1
Nodes (21): Backend (src/backend/), db/collection.py (Collection Query API), config_manager.py (Re-exports from service), db/__init__.py (get_db context manager), Frontend (src/frontend/), logic/game_history_logic.py (GameHistoryLoader), game_history.py (GameHistoryManager), views/tabs/game_history_tab.py (+13 more)

### Community 7 - "Config UI Tab"
Cohesion: 0.11
Nodes (21): classes/cooldown_tracker.py (CooldownTracker), detectors.py, game_api.py (SC2 API Polling), index.py (Backend Entry Point), ocr.py (Screen Capture + OCR), TTS Priority Queue (supply > minerals > idle > gas), logic/runner_logic.py (RunnerController), views/runner_view.py (RunnerScreen) (+13 more)

### Community 8 - "Core Module Docs"
Cohesion: 0.14
Nodes (14): WakeWordDetector, _make_detector_mocks(), Loop must not crash on stream.read raising an exception., Loop must not crash on stream.read raising an exception., Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo, Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo, Second above-threshold chunk within refractory_s must not trigger on_wake again., Second above-threshold chunk within refractory_s must not trigger on_wake again. (+6 more)

### Community 9 - "Frontend Composition"
Cohesion: 0.15
Nodes (18): _capture_hud(), fetch_game_state(), _filter_spikes(), is_game_running(), _poll_game(), Return (is_running, players). Single API call reused by main loop., Return True if SC2 is running and a game is in progress., Capture HUD via screen OCR. Assumes game is already confirmed running. (+10 more)

### Community 11 - "Settings & Messages UI"
Cohesion: 0.13
Nodes (16): SC2HelperApp, frontend/config_manager.py, ConfigTab, CoordsTab, dev.py __main__, RestartHandler, GameHistoryLoader, GameHistoryTab (+8 more)

### Community 12 - "History Dashboard"
Cohesion: 0.22
Nodes (3): _format_duration(), GameHistoryManager, get_db()

### Community 13 - "TTS Speech Queue"
Cohesion: 0.26
Nodes (3): get_stats_history(), GameHistoryLoader, GameHistoryTab

### Community 14 - "Voice Listener"
Cohesion: 0.22
Nodes (6): SpeechQueue, Smoke tests for SpeechQueue — no actual TTS subprocess spawned., Lower priority number = higher urgency = dequeued first., test_counter_increments(), test_priority_ordering(), test_speak_enqueues_without_error()

### Community 15 - "Message Banks & Tests"
Cohesion: 0.24
Nodes (3): get_mouse_pos(), Move mouse over each SC2 HUD element. Press Enter in terminal to record position, CoordsTab

### Community 16 - "Backend HUD Images"
Cohesion: 0.33
Nodes (7): get_message(), Smoke tests for message selection logic., test_custom_mode_falls_back_to_strict_when_empty(), test_custom_mode_falls_back_when_category_missing(), test_custom_mode_uses_custom_messages(), test_funny_mode_returns_non_empty(), test_strict_mode_returns_exact_string()

### Community 17 - "Frontend HUD Images"
Cohesion: 0.33
Nodes (9): Gas HUD Crop Processed (backend), Gas HUD Crop Raw (backend), Idle Workers HUD Crop Processed (backend), Idle Workers HUD Crop Raw (backend), Minerals HUD Crop Processed (backend), Minerals HUD Crop Raw (backend), OCR Module (backend), Supply HUD Crop Processed (backend) (+1 more)

### Community 18 - "Dev Hot-reload Runner"
Cohesion: 0.5
Nodes (8): Gas HUD Crop (Processed), Gas HUD Crop (Raw), Idle Workers HUD Crop (Processed), Idle Workers HUD Crop (Raw), Minerals HUD Crop (Processed), Minerals HUD Crop (Raw), Supply HUD Crop (Processed), Supply HUD Crop (Raw)

### Community 19 - "Voice Command Parsing"
Cohesion: 0.38
Nodes (3): FileSystemEventHandler, Dev runner: watches src/ for .py changes and auto-restarts the app., RestartHandler

### Community 20 - "HUD Coordinate Config"
Cohesion: 0.5
Nodes (4): VoiceListener._listen_loop, VoiceListener._parse_command, VoiceListener._transcribe, VoiceCommand

### Community 21 - "Resource Detector Tests"
Cohesion: 0.67
Nodes (3): views/tabs/coords_tab.py, hud_elements.py (HudElement + HUD_ELEMENTS), Screen Capture Regions Config

### Community 22 - "Background Thread Classes"
Cohesion: 0.67
Nodes (3): test_check_resources_cooldown_prevents_repeat, test_check_resources_no_speak_below_threshold, test_check_resources_speaks_when_over_threshold

### Community 23 - "HUD Element Model"
Cohesion: 0.67
Nodes (3): CooldownTracker, SpeechQueue, VoiceListener

## Knowledge Gaps
- **136 isolated node(s):** `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo`, `Second above-threshold chunk within refractory_s must not trigger on_wake again.`, `Loop must not crash on stream.read raising an exception.` (+131 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Database Query Layer` to `Game State Detectors`, `Project Architecture Docs`, `Core Module Docs`, `Frontend Composition`, `History Dashboard`, `Voice Listener`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Why does `get_config()` connect `Game State Detectors` to `Frontend Composition`, `Database Query Layer`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `GameHistoryManager` connect `History Dashboard` to `Database Query Layer`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `main()` (e.g. with `setup_logging()` and `get_config()`) actually correct?**
  _`main()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `RunnerScreen` (e.g. with `SC2HelperApp` and `RunnerController`) actually correct?**
  _`RunnerScreen` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `WakeWordDetector` (e.g. with `test_init_sets_attributes()` and `test_stop_sets_event()`) actually correct?**
  _`WakeWordDetector` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo` to the rest of the system?**
  _136 weakly-connected nodes found - possible documentation gaps or missing edges._