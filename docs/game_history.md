# Game History

`GameHistoryManager` records per-game warning counts to the `game_stats` table in `src/backend/db/sc2helper.db`.

| Column | Purpose |
|--------|---------|
| `game_id` | Unique game identifier (`game_YYYYMMDD_HHMMSS`) |
| `match_date` | ISO timestamp of game start |
| `game_duration` | Formatted duration (`MM:SS`), set on game end |
| `result` | Win / Loss / Tie / Unknown, set on game end |
| `race` | Player race, set on game end |
| `mineral_warnings` | Running count, incremented live |
| `gas_warnings` | Running count, incremented live |
| `supply_warnings` | Running count, incremented live |
| `idle_worker_warnings` | Running count, incremented live |
| `status` | `live` while game is active, `complete` after game end |

The DB file is not tracked by git.

## GUI — Game History tab

The **Game History** tab in the settings screen shows:

- **History list** — all completed games, newest first, colour-coded by result (Win/Loss/Tie)
- **Detail panel** — per-game breakdown of mineral/gas/supply/idle-worker warning counts, game duration, race, and result

## Record schema (service layer)

`service.get_stats_history()` and `service.get_live_stats()` return dicts in this shape:

```json
{
  "gameId": "game_20260516_231858",
  "matchDate": "2026-05-16T23:18:58",
  "gameDuration": "14:08",
  "result": "Win",
  "race": "Protoss",
  "gameStats": {
    "mineralWarningsCount": 3,
    "gasWarningsCount": 4,
    "supplyWarningsCount": 9,
    "idleWorkersWarningsCount": 15
  }
}
```
