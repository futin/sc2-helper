# Architecture

```
sc2-helper/
├── src/
│   ├── backend/
│   │   ├── index.py           # Core loop: OCR → detect → TTS
│   │   ├── messages.py        # Warning message banks (strict / funny / custom)
│   │   ├── stats.py           # StatsManager: per-game warning counts → JSON
│   │   └── config.yaml        # All runtime configuration
│   └── frontend/
│       ├── app.py             # customtkinter root window
│       ├── sc2_ui.py          # UI entry point
│       ├── runner_screen.py   # Start/stop backend process, live log view
│       ├── settings_screen.py # Config editor (4 tabs: Config / Messages / Coords / Statistics)
│       └── config_manager.py  # YAML load/save helpers
├── dev.py                     # Hot-reload runner (watchdog) for development
└── requirements.txt
```

## How it works

1. **Backend** polls `http://localhost:6119/game` (SC2 client API) every `poll_interval` seconds to detect whether a game is live.
2. Game lifecycle transitions (not-running → running, running → not-running) trigger `StatsManager.on_game_start/on_game_end`, which records result and race from the API response.
3. For each live game tick it captures four screen regions via `mss`, scales them 3×, converts to greyscale/binary, and runs Tesseract OCR to read minerals, gas, supply, and idle-worker count. An optional anomaly filter suppresses OCR spikes by clamping values that jump more than a configured delta from the previous reading.
4. Three detectors (`check_resources`, `check_supply`, `check_idle_workers`) compare values against configurable thresholds and, when a condition fires and its cooldown has elapsed, push a message onto a priority queue. Each warning also increments the in-progress game counter in `StatsManager`.
5. A background TTS thread drains the queue via macOS `say`, ordered: supply > minerals > idle workers > gas.
6. **Frontend** is a `customtkinter` wrapper that edits `config.yaml` and spawns the backend script as a subprocess, streaming its stdout into a log panel. A **Debug** checkbox in the runner toolbar passes `--debug` to the backend.
