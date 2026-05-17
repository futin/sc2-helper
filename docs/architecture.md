# Architecture

```
sc2-helper/
├── src/
│   ├── backend/
│   │   ├── index.py             # Entry point: test_ocr_mode + main loop
│   │   ├── constants.py         # SC2_BASE, REQUEST_TIMEOUT, PRIORITY_*, lookup maps
│   │   ├── utils.py             # load_config, _extract_result/_race, _format_debug_state
│   │   ├── logger.py            # setup_logging()
│   │   ├── ocr.py               # Screen capture + Tesseract OCR functions
│   │   ├── game_api.py          # SC2 API polling, HUD capture, spike filter
│   │   ├── detectors.py         # check_resources, check_supply, check_idle_workers
│   │   ├── classes/
│   │   │   ├── speech_queue.py  # SpeechQueue: priority TTS daemon thread
│   │   │   └── cooldown_tracker.py  # CooldownTracker
│   │   ├── messages.py          # Warning message banks (strict / funny / custom)
│   │   ├── stats.py             # StatsManager: per-game warning counts → JSON
│   │   ├── hud_elements.py      # HudElement dataclass + HUD_ELEMENTS list
│   │   ├── find_coords.py       # Interactive mouse-position calibration tool
│   │   └── config.yaml          # All runtime configuration
│   └── frontend/
│       ├── sc2_ui.py            # UI entry point
│       ├── app.py               # customtkinter root window
│       ├── config_manager.py    # YAML load/save helpers + default config
│       ├── views/
│       │   ├── runner_view.py       # RunnerScreen: Start/stop backend, live log
│       │   ├── settings_view.py     # SettingsScreen: tab container + Save All
│       │   └── tabs/
│       │       ├── config_tab.py    # Configuration tab (thresholds, tiers, OCR)
│       │       ├── messages_tab.py  # Message mode + custom message editor
│       │       ├── coords_tab.py    # HUD coordinate capture with countdown
│       │       └── stats_tab.py     # Game statistics dashboard
│       └── logic/
│           ├── runner_logic.py  # RunnerController: subprocess + thread management
│           └── stats_logic.py   # StatsLoader: reads game_stats*.json files
├── tests/
│   ├── test_config_manager.py
│   ├── test_debug.py
│   ├── test_detectors.py
│   ├── test_messages.py
│   └── test_speech_queue.py
├── dev.py                       # Hot-reload runner (watchdog) for development
└── requirements.txt
```

## How it works

1. **Backend** polls `http://localhost:6119/game` (`game_api.py`) every `poll_interval` seconds to detect whether a game is live.
2. Game lifecycle transitions trigger `StatsManager.on_game_start/on_game_end` (`stats.py`), recording result and race from the API response.
3. For each live game tick, `ocr.py` captures four screen regions via `mss`, scales them 3×, converts to greyscale/binary, and runs Tesseract OCR to read minerals, gas, supply, and idle-worker count. `game_api._filter_spikes` optionally suppresses OCR spikes by clamping values that jump more than a configured delta from the previous reading.
4. Three detectors in `detectors.py` compare values against configurable thresholds and, when a condition fires and its cooldown has elapsed, push a message onto a priority queue. Each warning also increments the in-progress game counter in `StatsManager`.
5. `SpeechQueue` (`classes/speech_queue.py`) drains the queue in a background TTS thread via macOS `say`, ordered: supply > minerals > idle workers > gas.
6. **Frontend** (`views/`) is a `customtkinter` wrapper. `RunnerController` (`logic/runner_logic.py`) spawns the backend as a subprocess and streams stdout into the log panel via a queue/thread pair. `StatsLoader` (`logic/stats_logic.py`) reads the stats JSON files for the Statistics tab.
