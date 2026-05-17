from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection


class DBConnector(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def fetch(self, query: str, params: tuple = ()) -> list[dict]: ...

    @abstractmethod
    async def execute(self, query: str, params: tuple = ()) -> int: ...

    @abstractmethod
    async def execute_returning_rowid(self, query: str, params: tuple = ()) -> int: ...

    def collection(self, name: str) -> Collection:
        from .collection import Collection
        return Collection(self, name)
