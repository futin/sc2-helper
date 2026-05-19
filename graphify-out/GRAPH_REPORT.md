# Graph Report - sc2-helper  (2026-05-19)

## Corpus Check
- 46 files · ~15,679 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 276 nodes · 423 edges · 24 communities (21 shown, 3 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a7bde92`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 19 edges
2. `ConfigTab` - 17 edges
3. `RunnerScreen` - 15 edges
4. `GameHistoryManager` - 12 edges
5. `CooldownTracker` - 12 edges
6. `WakeWordDetector` - 12 edges
7. `_make_listener()` - 10 edges
8. `SQLiteConnector` - 10 edges
9. `Collection` - 10 edges
10. `_make_speech()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `_make_speech()` --calls--> `SpeechQueue`  [INFERRED]
  tests/test_detectors.py → src/backend/classes/speech_queue.py
- `test_init_sets_attributes()` --calls--> `WakeWordDetector`  [INFERRED]
  tests/test_wake_word_detector.py → src/backend/classes/wake_word_detector.py
- `test_stop_sets_event()` --calls--> `WakeWordDetector`  [INFERRED]
  tests/test_wake_word_detector.py → src/backend/classes/wake_word_detector.py
- `test_detect_loop_logs_error_on_missing_import()` --calls--> `WakeWordDetector`  [INFERRED]
  tests/test_wake_word_detector.py → src/backend/classes/wake_word_detector.py
- `test_speak_enqueues_without_error()` --calls--> `SpeechQueue`  [INFERRED]
  tests/test_speech_queue.py → src/backend/classes/speech_queue.py

## Communities (24 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (26): check_idle_workers(), check_resources(), check_supply(), Track idle workers. Returns updated idle_onset (or None if busy)., _handle_voice_command(), main(), SC2 Helper — captures the StarCraft II HUD via screen OCR and speaks audio warni, setup_logging() (+18 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (6): _format_duration(), GameHistoryManager, get_db(), ensure_tables(), SQLiteConnector, DBConnector

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (10): get_config(), Service layer — the only entry point for frontend to access config and stats. Fr, save_config(), SC2HelperApp, main(), Entry point for the SC2 Helper UI., Smoke tests for config get/save round-trips., test_get_config_returns_defaults_on_empty_db() (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (3): Start the backend process. Returns False if already running., RunnerController, RunnerScreen

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (5): ABC, _build_set(), _build_where(), Collection, DBConnector

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (18): _capture_hud(), fetch_game_state(), _filter_spikes(), is_game_running(), _poll_game(), Return (is_running, players). Single API call reused by main loop., Return True if SC2 is running and a game is in progress., Capture HUD via screen OCR. Assumes game is already confirmed running. (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (11): WakeWordDetector, _make_detector_mocks(), Loop must not crash on stream.read raising an exception., Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo, Second above-threshold chunk within refractory_s must not trigger on_wake again., test_detect_loop_calls_on_wake_when_threshold_met(), test_detect_loop_logs_error_on_missing_import(), test_detect_loop_recovers_from_audio_read_error() (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (11): VoiceCommand, VoiceListener, _make_listener(), test_handle_wake_enqueues_command(), test_handle_wake_missing_import_does_not_raise(), test_handle_wake_timeout_does_not_enqueue(), test_parse_resources(), test_parse_silence_minutes() (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.26
Nodes (3): get_stats_history(), GameHistoryLoader, GameHistoryTab

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (6): SpeechQueue, Smoke tests for SpeechQueue — no actual TTS subprocess spawned., Lower priority number = higher urgency = dequeued first., test_counter_increments(), test_priority_ordering(), test_speak_enqueues_without_error()

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (3): get_mouse_pos(), Move mouse over each SC2 HUD element. Press Enter in terminal to record position, CoordsTab

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (7): get_message(), Smoke tests for message selection logic., test_custom_mode_falls_back_to_strict_when_empty(), test_custom_mode_falls_back_when_category_missing(), test_custom_mode_uses_custom_messages(), test_funny_mode_returns_non_empty(), test_strict_mode_returns_exact_string()

### Community 14 - "Community 14"
Cohesion: 0.38
Nodes (3): FileSystemEventHandler, Dev runner: watches src/ for .py changes and auto-restarts the app., RestartHandler

## Knowledge Gaps
- **28 isolated node(s):** `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo`, `Second above-threshold chunk within refractory_s must not trigger on_wake again.`, `Loop must not crash on stream.read raising an exception.` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 0` to `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 8`, `Community 11`?**
  _High betweenness centrality (0.661) - this node is a cross-community bridge._
- **Why does `get_config()` connect `Community 2` to `Community 0`, `Community 5`?**
  _High betweenness centrality (0.430) - this node is a cross-community bridge._
- **Why does `GameHistoryManager` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.268) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `main()` (e.g. with `setup_logging()` and `get_config()`) actually correct?**
  _`main()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `RunnerScreen` (e.g. with `SC2HelperApp` and `RunnerController`) actually correct?**
  _`RunnerScreen` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `CooldownTracker` (e.g. with `test_check_resources_no_speak_below_threshold()` and `test_check_resources_speaks_when_over_threshold()`) actually correct?**
  _`CooldownTracker` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dev runner: watches src/ for .py changes and auto-restarts the app.`, `Smoke tests for detector logic — no TTS subprocess spawned.`, `Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loo` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._