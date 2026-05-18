# Database Query Layer

> 33 nodes · cohesion 0.50

## Key Concepts

- **SQLiteConnector** (10 connections) — `src/backend/db/sqlite_connector.py`
- **connector.py** (10 connections) — `src/backend/db/connector.py`
- **Collection** (10 connections) — `src/backend/db/collection.py`
- **_build_where()** (6 connections) — `src/backend/db/collection.py`
- **DBConnector** (5 connections) — `src/backend/db/connector.py`
- **collection.py** (5 connections) — `src/backend/db/collection.py`
- **__init__.py** (4 connections) — `src/backend/db/__init__.py`
- **sqlite_connector.py** (4 connections) — `src/backend/db/sqlite_connector.py`
- **.execute()** (4 connections) — `src/backend/db/sqlite_connector.py`
- **.connect()** (3 connections) — `src/backend/db/sqlite_connector.py`
- **_build_set()** (3 connections) — `src/backend/db/collection.py`
- **.find()** (3 connections) — `src/backend/db/collection.py`
- **.update()** (3 connections) — `src/backend/db/collection.py`
- **.updateOne()** (3 connections) — `src/backend/db/collection.py`
- **.fetch()** (2 connections) — `src/backend/db/sqlite_connector.py`
- **.execute_returning_rowid()** (2 connections) — `src/backend/db/sqlite_connector.py`
- **ABC** (2 connections)
- **.findOne()** (2 connections) — `src/backend/db/collection.py`
- **.delete()** (2 connections) — `src/backend/db/collection.py`
- **.count()** (2 connections) — `src/backend/db/collection.py`
- **schema.py** (2 connections) — `src/backend/db/schema.py`
- **ensure_tables()** (2 connections) — `src/backend/db/schema.py`
- **DBConnector** (1 connections)
- **.__init__()** (1 connections) — `src/backend/db/sqlite_connector.py`
- **.close()** (1 connections) — `src/backend/db/sqlite_connector.py`
- *... and 8 more nodes in this community*

## Relationships

- [[History Dashboard]] (2 shared connections)

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