# Configuration

All settings are stored in the `config` table in `src/backend/db/sc2helper.db`. They can be edited via the GUI **Configuration** tab or by calling `service.save_config()` directly.

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

## Supply tiers

Supply warnings use a gap system: warn when `supply_max - supply_used <= gap`. Tiers are matched by `max_cap` (first tier where `supply_max <= max_cap` wins):

```json
"supply": {
  "tiers": [
    {"max_cap": 25,  "gap": 3},
    {"max_cap": 50,  "gap": 5},
    {"max_cap": 200, "gap": 10}
  ]
}
```

## Screen capture regions

Each region is `[left, top, width, height]` in screen pixels. Use the **Coords Selection** tab in the GUI to set these.

```json
"screen_capture": {
  "minerals":     [2026, 30, 80, 30],
  "gas":          [2193, 30, 80, 30],
  "supply":       [2358, 30, 100, 30],
  "idle_workers": [65, 999, 60, 25],
  "ocr_threshold": 100
}
```

## Voice control

Enable wake-word voice commands. Requires `openwakeword`, `pyaudio`, `numpy`, and `SpeechRecognition` installed.

```json
"voice_control": {
  "enabled": false,
  "wake_word_model": "alexa",
  "wake_sensitivity": 0.5,
  "stt_backend": "google",
  "silence_duration": 120,
  "pause_threshold": 1.2,
  "phrase_time_limit": 8
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `enabled` | `false` | Enable/disable the voice system |
| `wake_word_model` | `"alexa"` | openwakeword model name (downloads ~2 MB on first run) |
| `wake_sensitivity` | `0.5` | Wake detection threshold 0.0–1.0 (higher = less sensitive) |
| `stt_backend` | `"google"` | Command transcription: `"google"` or `"whisper"` |
| `silence_duration` | `120` | Default seconds to silence warnings when "mute" command spoken |
| `pause_threshold` | `1.2` | Seconds of silence that ends a voice command |
| `phrase_time_limit` | `8` | Max seconds to listen for a command after wake |

Supported voice commands (say the wake word first):
- **"supply"** / **"supply status"** → reads current supply aloud
- **"resources"** / **"minerals"** / **"gas"** → reads mineral and gas counts aloud
- **"silence for N minutes"** / **"mute"** / **"quiet"** → suppresses warnings for N minutes (default 2)

## Anomaly filter

Suppresses OCR misreads by clamping values that jump more than `max_delta` from the previous reading. Enabled by default.

```json
"anomaly_filter": {
  "enabled": true,
  "max_delta": {
    "minerals": 1000,
    "gas": 500,
    "supply_used": 10,
    "supply_max": 16
  }
}
```
