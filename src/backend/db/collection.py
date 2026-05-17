from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connector import DBConnector


def _build_where(filter: dict | None) -> tuple[str, tuple]:
    if not filter:
        return "", ()
    clauses = " AND ".join(f"{k} = ?" for k in filter)
    return f" WHERE {clauses}", tuple(filter.values())


def _build_set(data: dict) -> tuple[str, tuple]:
    clauses = ", ".join(f"{k} = ?" for k in data)
    return clauses, tuple(data.values())


class Collection:
    def __init__(self, connector: DBConnector, table: str) -> None:
        self._connector = connector
        self._table = table

    async def find(
        self,
        filter: dict | None = None,
        *,
        sort: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        where, params = _build_where(filter)
        query = f"SELECT * FROM {self._table}{where}"
        if sort:
            query += f" ORDER BY {sort}"
        if limit is not None:
            query += f" LIMIT {limit}"
        return await self._connector.fetch(query, params)

    async def findOne(self, filter: dict | None = None) -> dict | None:
        rows = await self.find(filter, limit=1)
        return rows[0] if rows else None

    async def create(self, document: dict) -> dict:
        cols = ", ".join(document.keys())
        placeholders = ", ".join("?" * len(document))
        query = f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})"
        rowid = await self._connector.execute_returning_rowid(query, tuple(document.values()))
        rows = await self._connector.fetch(
            f"SELECT * FROM {self._table} WHERE rowid = ?", (rowid,)
        )
        return rows[0] if rows else document

    async def update(self, filter: dict, data: dict) -> int:
        where, where_params = _build_where(filter)
        set_clause, set_params = _build_set(data)
        query = f"UPDATE {self._table} SET {set_clause}{where}"
        return await self._connector.execute(query, (*set_params, *where_params))

    async def updateOne(self, filter: dict, data: dict) -> bool:
        where, where_params = _build_where(filter)
        set_clause, set_params = _build_set(data)
        query = (
            f"UPDATE {self._table} SET {set_clause} "
            f"WHERE rowid IN (SELECT rowid FROM {self._table}{where} LIMIT 1)"
        )
        affected = await self._connector.execute(query, (*set_params, *where_params))
        return affected > 0

    async def delete(self, filter: dict) -> int:
        where, params = _build_where(filter)
        query = f"DELETE FROM {self._table}{where}"
        return await self._connector.execute(query, params)

    async def count(self, filter: dict | None = None) -> int:
        where, params = _build_where(filter)
        query = f"SELECT COUNT(*) AS n FROM {self._table}{where}"
        rows = await self._connector.fetch(query, params)
        return rows[0]["n"] if rows else 0
