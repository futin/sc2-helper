# Configuration

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
| `supply.cooldown` | `20` | Seconds between supply warnings |
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

```yaml
supply:
  tiers:
    - {max_cap: 25,  gap: 2}
    - {max_cap: 50,  gap: 4}
    - {max_cap: 200, gap: 10}
```

## Screen capture regions

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

## Anomaly filter

Suppresses OCR misreads by clamping values that jump more than `max_delta` from the previous reading. Disabled by default.

```yaml
anomaly_filter:
  enabled: true
  max_delta:
    minerals: 1000
    gas: 500
    supply_used: 10
    supply_max: 16
```
