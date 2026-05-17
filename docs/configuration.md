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
