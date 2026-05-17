from __future__ import annotations

from pathlib import Path

import aiosqlite

from .connector import DBConnector
from .schema import ensure_tables


class SQLiteConnector(DBConnector):
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        await ensure_tables(self._conn)

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def fetch(self, query: str, params: tuple = ()) -> list[dict]:
        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def execute(self, query: str, params: tuple = ()) -> int:
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        return cursor.rowcount

    async def execute_returning_rowid(self, query: str, params: tuple = ()) -> int:
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        return cursor.lastrowid
