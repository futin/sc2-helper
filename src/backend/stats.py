import asyncio
import time
from datetime import datetime
from typing import Optional

from backend.db import get_db


class StatsManager:
    def __init__(self) -> None:
        self._game_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._start_dt: Optional[datetime] = None
        self._mineral_warnings: int = 0
        self._gas_warnings: int = 0
        self._supply_warnings: int = 0
        self._idle_worker_warnings: int = 0

    @property
    def counts(self) -> dict[str, int]:
        return {
            "mineralWarningsCount":     self._mineral_warnings,
            "gasWarningsCount":         self._gas_warnings,
            "supplyWarningsCount":      self._supply_warnings,
            "idleWorkersWarningsCount": self._idle_worker_warnings,
        }

    def on_game_start(self) -> None:
        now = datetime.now()
        self._game_id = "game_" + now.strftime("%Y%m%d_%H%M%S")
        self._start_time = time.monotonic()
        self._start_dt = now
        self._mineral_warnings = 0
        self._gas_warnings = 0
        self._supply_warnings = 0
        self._idle_worker_warnings = 0
        asyncio.run(self._db_create_game())

    def on_mineral_warning(self) -> None:
        if self._game_id:
            self._mineral_warnings += 1
            asyncio.run(self._db_update_warnings())

    def on_gas_warning(self) -> None:
        if self._game_id:
            self._gas_warnings += 1
            asyncio.run(self._db_update_warnings())

    def on_supply_warning(self) -> None:
        if self._game_id:
            self._supply_warnings += 1
            asyncio.run(self._db_update_warnings())

    def on_idle_workers_warning(self) -> None:
        if self._game_id:
            self._idle_worker_warnings += 1
            asyncio.run(self._db_update_warnings())

    def on_game_end(self, result: str, race: str = "Unknown") -> None:
        if not self._game_id:
            return
        elapsed = time.monotonic() - self._start_time
        duration = self._format_duration(elapsed)
        asyncio.run(self._db_end_game(result, race, duration))
        self._game_id = None
        self._start_time = None
        self._start_dt = None
        self._mineral_warnings = 0
        self._gas_warnings = 0
        self._supply_warnings = 0
        self._idle_worker_warnings = 0

    async def _db_create_game(self) -> None:
        async with get_db() as db:
            col = db.collection("game_stats")
            await col.create({
                "game_id": self._game_id,
                "match_date": self._start_dt.isoformat(timespec="seconds"),
                "game_duration": None,
                "result": None,
                "race": None,
                "mineral_warnings": 0,
                "gas_warnings": 0,
                "supply_warnings": 0,
                "idle_worker_warnings": 0,
                "status": "live",
                "last_updated": self._start_dt.isoformat(timespec="seconds"),
            })

    async def _db_update_warnings(self) -> None:
        async with get_db() as db:
            col = db.collection("game_stats")
            await col.updateOne(
                {"game_id": self._game_id},
                {
                    "mineral_warnings": self._mineral_warnings,
                    "gas_warnings": self._gas_warnings,
                    "supply_warnings": self._supply_warnings,
                    "idle_worker_warnings": self._idle_worker_warnings,
                    "last_updated": datetime.now().isoformat(timespec="seconds"),
                },
            )

    async def _db_end_game(self, result: str, race: str, duration: str) -> None:
        async with get_db() as db:
            col = db.collection("game_stats")
            await col.updateOne(
                {"game_id": self._game_id},
                {
                    "game_duration": duration,
                    "result": result,
                    "race": race,
                    "status": "complete",
                    "last_updated": datetime.now().isoformat(timespec="seconds"),
                },
            )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total = int(seconds)
        return f"{total // 60}:{total % 60:02d}"
