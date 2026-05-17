"""
Game statistics tracker — records per-game warning counts to JSON.

Files written:
  game_stats.json       — append-only array of completed games
  game_stats_live.json  — current in-progress game counters (deleted on game end)

Both files are written atomically via os.replace to prevent partial reads.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class StatsManager:
    STATS_PATH: Path = Path(__file__).parent / "game_stats.json"
    LIVE_PATH: Path = Path(__file__).parent / "game_stats_live.json"

    def __init__(self) -> None:
        self._game_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._start_dt: Optional[datetime] = None
        self._counts: dict[str, int] = {}

    def on_game_start(self) -> None:
        now = datetime.now()
        self._game_id = "game_" + now.strftime("%Y%m%d_%H%M%S")
        self._start_time = time.monotonic()
        self._start_dt = now
        self._counts = {
            "mineralWarningsCount": 0,
            "gasWarningsCount": 0,
            "supplyWarningsCount": 0,
            "idleWorkersWarningsCount": 0,
        }

    def on_mineral_warning(self) -> None:
        if self._game_id:
            self._counts["mineralWarningsCount"] += 1
            self._write_live()

    def on_gas_warning(self) -> None:
        if self._game_id:
            self._counts["gasWarningsCount"] += 1
            self._write_live()

    def on_supply_warning(self) -> None:
        if self._game_id:
            self._counts["supplyWarningsCount"] += 1
            self._write_live()

    def on_idle_workers_warning(self) -> None:
        if self._game_id:
            self._counts["idleWorkersWarningsCount"] += 1
            self._write_live()

    def on_game_end(self, result: str, race: str = "Unknown") -> None:
        if not self._game_id:
            return
        elapsed = time.monotonic() - self._start_time
        record = {
            "gameId": self._game_id,
            "matchDate": self._start_dt.isoformat(timespec="seconds"),
            "gameDuration": self._format_duration(elapsed),
            "result": result,
            "race": race,
            "gameStats": dict(self._counts),
        }
        self._append_history(record)
        self.LIVE_PATH.unlink(missing_ok=True)
        self._game_id = None
        self._start_time = None
        self._start_dt = None
        self._counts = {}

    def _write_live(self) -> None:
        data = {
            "gameId": self._game_id,
            "matchDate": self._start_dt.isoformat(timespec="seconds"),
            "lastUpdated": datetime.now().isoformat(timespec="seconds"),
            "gameStats": dict(self._counts),
        }
        self._atomic_write(self.LIVE_PATH, data)

    def _append_history(self, record: dict) -> None:
        records = self._load_history()
        records.append(record)
        self._atomic_write(self.STATS_PATH, records)

    def _load_history(self) -> list:
        try:
            text = self.STATS_PATH.read_text()
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def _atomic_write(path: Path, data) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        os.replace(tmp, path)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total = int(seconds)
        return f"{total // 60}:{total % 60:02d}"
