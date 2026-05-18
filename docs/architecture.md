# Architecture

```
sc2-helper/
├── src/
│   ├── backend/
│   │   ├── index.py             # Entry point: test_ocr_mode + main loop
│   │   ├── constants.py         # SC2_BASE, REQUEST_TIMEOUT, PRIORITY_*, lookup maps
│   │   ├── utils.py             # _extract_result/_race, _format_debug_state
│   │   ├── logger.py            # setup_logging()
│   │   ├── ocr.py               # Screen capture + Tesseract OCR functions
│   │   ├── game_api.py          # SC2 API polling, HUD capture, spike filter
│   │   ├── detectors.py         # check_resources, check_supply, check_idle_workers
│   │   ├── service.py           # Service layer: get_config/save_config, get_stats_history/get_live_stats
│   │   ├── classes/
│   │   │   ├── speech_queue.py      # SpeechQueue: priority TTS daemon thread
│   │   │   ├── cooldown_tracker.py  # CooldownTracker
│   │   │   ├── wake_word_detector.py  # WakeWordDetector: always-on openwakeword thread
│   │   │   └── voice_listener.py    # VoiceListener: stateless two-phase command transcription
│   │   ├── db/
│   │   │   ├── __init__.py      # get_db() context manager, DB_PATH
│   │   │   ├── connector.py     # Database abstraction base
│   │   │   ├── sqlite_connector.py  # aiosqlite implementation
│   │   │   ├── collection.py    # Collection query API (find/findOne/create/update)
│   │   │   └── schema.py        # CREATE TABLE statements for config + game_stats
│   │   ├── messages.py          # Warning message banks (strict / funny / custom)
│   │   ├── game_history.py      # GameHistoryManager: per-game warning counts → SQLite
│   │   ├── hud_elements.py      # HudElement dataclass + HUD_ELEMENTS list
│   │   └── find_coords.py       # Interactive mouse-position calibration tool
│   └── frontend/
│       ├── sc2_ui.py            # UI entry point
│       ├── app.py               # customtkinter root window
│       ├── config_manager.py    # Re-exports get_config/save_config/DEFAULT_CONFIG from service
│       ├── views/
│       │   ├── runner_view.py       # RunnerScreen: Start/stop backend, live log
│       │   ├── settings_view.py     # SettingsScreen: tab container + Save All
│       │   └── tabs/
│       │       ├── config_tab.py    # Configuration tab (thresholds, tiers, OCR)
│       │       ├── messages_tab.py  # Message mode + custom message editor
│       │       ├── coords_tab.py    # HUD coordinate capture with countdown
│       │       └── game_history_tab.py  # Game History dashboard
│       └── logic/
│           ├── runner_logic.py  # RunnerController: subprocess + thread management
│           └── game_history_logic.py  # GameHistoryLoader: reads history via service.get_stats_history()
├── tests/
│   ├── test_config_manager.py
│   ├── test_debug.py
│   ├── test_detectors.py
│   ├── test_messages.py
│   ├── test_speech_queue.py
│   ├── test_wake_word_detector.py
│   └── test_voice_listener.py
├── dev.py                       # Hot-reload runner (watchdog) for development
└── requirements.txt
```

## How it works

1. **Backend** polls `http://localhost:6119/game` (`game_api.py`) every `poll_interval` seconds to detect whether a game is live.
2. Game lifecycle transitions trigger `GameHistoryManager.on_game_start/on_game_end` (`stats.py`), which writes rows to the `game_stats` SQLite table via `db/`. The row starts with `status='live'` and is updated to `status='complete'` on game end with result and race.
3. For each live game tick, `ocr.py` captures four screen regions via `mss`, scales them 3×, converts to greyscale/binary, and runs Tesseract OCR to read minerals, gas, supply, and idle-worker count. `game_api._filter_spikes` optionally suppresses OCR spikes by clamping values that jump more than a configured delta from the previous reading.
4. Three detectors in `detectors.py` compare values against configurable thresholds and, when a condition fires and its cooldown has elapsed, push a message onto a priority queue. Each warning also increments the in-progress game counter in `GameHistoryManager`.
5. `SpeechQueue` (`classes/speech_queue.py`) drains the queue in a background TTS thread via macOS `say`, ordered: supply > minerals > idle workers > gas.
6. **Voice control** (optional): when enabled, `WakeWordDetector` runs an always-on background thread that feeds 80ms raw audio chunks to an `openwakeword` ONNX model. On wake detection (score ≥ sensitivity, with a 2s refractory period), it calls `VoiceListener.handle_wake()`, which opens the microphone, transcribes speech via Google STT or Whisper, parses the command, and pushes a `VoiceCommand` onto a queue. The main loop drains this queue each tick and dispatches to `_handle_voice_command()`. Supported intents: `query_supply`, `query_resources`, `silence`.
7. **Frontend** (`views/`) is a `customtkinter` wrapper. `RunnerController` (`logic/runner_logic.py`) spawns the backend as a subprocess and streams stdout into the log panel via a queue/thread pair. `GameHistoryLoader` (`logic/game_history_logic.py`) calls `service.get_stats_history()` for the Game History tab. Config is read and saved via `service.get_config()`/`service.save_config()`, which reads from and writes to the `config` SQLite table.
