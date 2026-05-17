# DB Collection Layer

> 33 nodes · cohesion 0.09

## Key Concepts

- **Collection** (10 connections) — `src/backend/db/collection.py`
- **SQLiteConnector** (10 connections) — `src/backend/db/sqlite_connector.py`
- **connector.py** (10 connections) — `src/backend/db/connector.py`
- **_build_where()** (6 connections) — `src/backend/db/collection.py`
- **DBConnector** (5 connections) — `src/backend/db/connector.py`
- **collection.py** (5 connections) — `src/backend/db/collection.py`
- **.execute()** (4 connections) — `src/backend/db/sqlite_connector.py`
- **__init__.py** (4 connections) — `src/backend/db/__init__.py`
- **sqlite_connector.py** (4 connections) — `src/backend/db/sqlite_connector.py`
- **_build_set()** (3 connections) — `src/backend/db/collection.py`
- **.find()** (3 connections) — `src/backend/db/collection.py`
- **.update()** (3 connections) — `src/backend/db/collection.py`
- **.updateOne()** (3 connections) — `src/backend/db/collection.py`
- **.connect()** (3 connections) — `src/backend/db/sqlite_connector.py`
- **ABC** (2 connections)
- **.count()** (2 connections) — `src/backend/db/collection.py`
- **.delete()** (2 connections) — `src/backend/db/collection.py`
- **.findOne()** (2 connections) — `src/backend/db/collection.py`
- **ensure_tables()** (2 connections) — `src/backend/db/schema.py`
- **.execute_returning_rowid()** (2 connections) — `src/backend/db/sqlite_connector.py`
- **.fetch()** (2 connections) — `src/backend/db/sqlite_connector.py`
- **schema.py** (2 connections) — `src/backend/db/schema.py`
- **.create()** (1 connections) — `src/backend/db/collection.py`
- **.__init__()** (1 connections) — `src/backend/db/collection.py`
- **close()** (1 connections) — `src/backend/db/connector.py`
- *... and 8 more nodes in this community*

## Relationships

- [[Game History DB]] (2 shared connections)

## Source Files

- `src/backend/db/__init__.py`
- `src/backend/db/collection.py`
- `src/backend/db/connector.py`
- `src/backend/db/schema.py`
- `src/backend/db/sqlite_connector.py`

## Audit Trail

- EXTRACTED: 93 (93%)
- INFERRED: 7 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*