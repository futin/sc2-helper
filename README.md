# SC2 Helper

Real-time StarCraft II assistant. Monitors your HUD via screen OCR and fires spoken warnings when you're floating resources, getting supply-capped, or leaving workers idle.

---

## Architecture

```
sc2-helper/
├── src/
│   ├── backend/
│   │   ├── index.py           # Core loop: OCR → detect → TTS
│   │   ├── messages.py        # Warning message banks (strict / funny / custom)
│   │   └── config.yaml        # All runtime configuration
│   └── frontend/
│       ├── app.py             # customtkinter root window
│       ├── sc2_ui.py          # UI entry point
│       ├── runner_screen.py   # Start/stop backend process, live log view
│       ├── settings_screen.py # Config editor (3 tabs: Config / Messages / Coords)
│       └── config_manager.py  # YAML load/save helpers
├── dev.py                     # Hot-reload runner (watchdog) for development
└── requirements.txt
```

### How it works

1. **Backend** polls `http://localhost:6119/game` (SC2 client API) every `poll_interval` seconds to detect whether a game is live.
2. For each live game tick it captures four screen regions via `mss`, scales them 3×, converts to greyscale/binary, and runs Tesseract OCR to read minerals, gas, supply, and idle-worker count.
3. Three detectors (`check_resources`, `check_supply`, `check_idle_workers`) compare the values against configurable thresholds and, when a condition fires and its cooldown has elapsed, push a message onto a priority queue.
4. A background TTS thread drains the queue via macOS `say`, ordered: supply > minerals > idle workers > gas.
5. **Frontend** is a `customtkinter` wrapper that edits `config.yaml` and spawns the backend script as a subprocess, streaming its stdout into a log panel.

---

## Requirements

- Python 3.11+
- macOS (TTS uses the `say` command)
- Tesseract OCR installed: `brew install tesseract`
- StarCraft II running with the client API enabled (port 6119)
- `customtkinter` — installed via `pip install -r requirements.txt`

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Running

### GUI (recommended)

```bash
python src/frontend/sc2_ui.py
```

Opens the settings window. Click **▶ Run Script** to open the runner panel, then **▶ Start**.

### Backend only

```bash
python -m backend.index
```

### Debug mode — inspect the SC2 client API response and exit

```bash
python -m backend.index --debug
```

### Test OCR mode — verify OCR is reading each region correctly

```bash
python -m backend.index --test-ocr
```

Saves raw and pre-processed crops to `src/backend/ocr_debug/` and prints OCR results. Useful for tuning `ocr_threshold`.

### Dev mode — hot-reload on file changes

```bash
python dev.py
```

Watches `src/` for `.py` changes and auto-restarts the UI. Requires `watchdog` (included in `requirements.txt`).

---

## Configuration

All settings live in `src/backend/config.yaml`. They can also be edited via the GUI **Configuration** tab.

| Key | Default | Description |
|-----|---------|-------------|
| `poll_interval` | `2.5` | Seconds between game state polls |
| `player_id` | `1` | Your player slot in the game |
| `tts_voice` | `Moira` | macOS `say` voice name |
| `message_mode` | `strict` | `strict` / `funny` / `custom` |
| `resources.mineral_threshold` | `600` | Warn when minerals exceed this |
| `resources.gas_threshold` | `600` | Warn when gas exceeds this |
| `resources.cooldown` | `30` | Seconds between resource warnings |
| `supply.cooldown` | `10` | Seconds between supply warnings |
| `supply.tiers` | see below | Gap-based warning tiers |
| `workers.idle_seconds` | `10` | Seconds before idle worker warning fires |
| `workers.cooldown` | `30` | Seconds between idle worker warnings |
| `screen_capture.*` | see below | Pixel regions for each HUD element |
| `custom_messages.supply` | `[]` | Custom TTS lines for supply warnings |
| `custom_messages.minerals` | `[]` | Custom TTS lines for mineral warnings |
| `custom_messages.gas` | `[]` | Custom TTS lines for gas warnings |
| `custom_messages.idle_workers` | `[]` | Custom TTS lines for idle worker warnings |

### Supply tiers

Supply warnings use a gap system: warn when `supply_max - supply_used <= gap`. Tiers are matched by `max_cap` (first tier where `supply_max <= max_cap` wins):

```yaml
supply:
  tiers:
    - {max_cap: 25,  gap: 3}
    - {max_cap: 50,  gap: 5}
    - {max_cap: 200, gap: 10}
```

### Screen capture regions

Each region is `[left, top, width, height]` in screen pixels:

```yaml
screen_capture:
  minerals:     [2026, 30, 80, 30]
  gas:          [2193, 30, 80, 30]
  supply:       [2358, 30, 100, 30]
  idle_workers: [65, 999, 60, 25]
  ocr_threshold: 100
```

Use the **Coords Selection** tab in the GUI to set these, or edit `config.yaml` manually.

---

## Message modes

| Mode | Behaviour |
|------|-----------|
| `strict` | Short, direct: "Check supply." |
| `funny` | Random snarky message from a built-in bank |
| `custom` | Your own messages from `config.yaml → custom_messages`, falls back to strict |

Custom messages are configured per category (`supply`, `minerals`, `gas`, `idle_workers`) as a list of strings. The GUI **Messages** tab exposes this when `custom` mode is selected.
