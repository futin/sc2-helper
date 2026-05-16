# Statistics

`StatsManager` records per-game warning counts to two JSON files in `src/backend/`:

| File | Purpose |
|------|---------|
| `game_stats.json` | Append-only history of completed games |
| `game_stats_live.json` | In-progress game counters, deleted on game end |

Both are written atomically. Neither is tracked by git.

## GUI — Statistics tab

The **Statistics** tab in the settings screen shows:

- **History list** — all completed games, newest first, colour-coded by result (Win/Loss/Tie)
- **Live game banner** — warning counts for the current game, refreshes every 5 seconds
- **Detail panel** — per-game breakdown of mineral/gas/supply/idle-worker warning counts, game duration, race, and result

## Record schema

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
