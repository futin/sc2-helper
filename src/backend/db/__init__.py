from contextlib import asynccontextmanager
from pathlib import Path

from .collection import Collection
from .connector import DBConnector
from .sqlite_connector import SQLiteConnector

DB_PATH = Path(__file__).parent / "sc2helper.db"


@asynccontextmanager
async def get_db():
    db = SQLiteConnector(DB_PATH)
    await db.connect()
    try:
        yield db
    finally:
        await db.close()


__all__ = ["get_db", "DBConnector", "Collection", "DB_PATH"]
