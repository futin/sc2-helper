_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS config (
    id              INTEGER PRIMARY KEY DEFAULT 1,
    poll_interval   REAL    NOT NULL,
    player_id       INTEGER NOT NULL,
    tts_voice       TEXT    NOT NULL,
    message_mode    TEXT    NOT NULL,
    resources       TEXT    NOT NULL,
    supply          TEXT    NOT NULL,
    workers         TEXT    NOT NULL,
    screen_capture  TEXT    NOT NULL,
    anomaly_filter  TEXT    NOT NULL,
    custom_messages TEXT    NOT NULL,
    voice_control   TEXT    NOT NULL DEFAULT '{}',
    updated_at      TEXT    NOT NULL
)
"""

_GAME_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS game_stats (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id              TEXT    NOT NULL UNIQUE,
    match_date           TEXT    NOT NULL,
    game_duration        TEXT,
    result               TEXT,
    race                 TEXT,
    mineral_warnings     INTEGER NOT NULL DEFAULT 0,
    gas_warnings         INTEGER NOT NULL DEFAULT 0,
    supply_warnings      INTEGER NOT NULL DEFAULT 0,
    idle_worker_warnings INTEGER NOT NULL DEFAULT 0,
    status               TEXT    NOT NULL DEFAULT 'live',
    last_updated         TEXT    NOT NULL
)
"""


async def ensure_tables(conn) -> None:
    await conn.execute(_CONFIG_TABLE)
    await conn.execute(_GAME_STATS_TABLE)
    try:
        await conn.execute("ALTER TABLE config ADD COLUMN voice_control TEXT NOT NULL DEFAULT '{}'")
    except Exception:
        pass
    await conn.commit()
