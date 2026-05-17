"""
One-time migration: seeds the SQLite DB from existing config.yaml and game_stats.json.

Run from the src/ directory:
    python -m backend.db.migrate

Safe to run multiple times — skips tables that already have data.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

import yaml

from backend.db import DB_PATH, get_db

_BACKEND_DIR = Path(__file__).parent.parent
_CONFIG_YAML = _BACKEND_DIR / "config.yaml"
_STATS_JSON = _BACKEND_DIR / "game_stats.json"
_LIVE_JSON = _BACKEND_DIR / "game_stats_live.json"

_JSON_FIELDS = ("resources", "supply", "workers", "screen_capture", "anomaly_filter", "custom_messages")


def _serialize_config(cfg: dict) -> dict:
    row = {}
    row["id"] = 1
    row["poll_interval"] = cfg.get("poll_interval", 2.5)
    row["player_id"] = cfg.get("player_id", 1)
    row["tts_voice"] = cfg.get("tts_voice", "Moira")
    row["message_mode"] = cfg.get("message_mode", "strict")
    row["resources"] = json.dumps(cfg.get("resources", {}))
    row["supply"] = json.dumps(cfg.get("supply", {}))
    row["workers"] = json.dumps(cfg.get("workers", {}))
    row["screen_capture"] = json.dumps(cfg.get("screen_capture", {}))
    row["anomaly_filter"] = json.dumps(cfg.get("anomaly_filter", {"enabled": False, "max_delta": {}}))
    row["custom_messages"] = json.dumps(cfg.get("custom_messages", {"minerals": [], "gas": [], "supply": [], "idle_workers": []}))
    row["updated_at"] = datetime.now().isoformat(timespec="seconds")
    return row


def _serialize_stats(record: dict) -> dict:
    gs = record.get("gameStats", {})
    return {
        "game_id": record["gameId"],
        "match_date": record["matchDate"],
        "game_duration": record.get("gameDuration"),
        "result": record.get("result"),
        "race": record.get("race"),
        "mineral_warnings": gs.get("mineralWarningsCount", 0),
        "gas_warnings": gs.get("gasWarningsCount", 0),
        "supply_warnings": gs.get("supplyWarningsCount", 0),
        "idle_worker_warnings": gs.get("idleWorkersWarningsCount", 0),
        "status": "complete",
        "last_updated": record.get("matchDate", datetime.now().isoformat(timespec="seconds")),
    }


def _serialize_live(record: dict) -> dict:
    gs = record.get("gameStats", {})
    return {
        "game_id": record["gameId"],
        "match_date": record["matchDate"],
        "game_duration": None,
        "result": None,
        "race": None,
        "mineral_warnings": gs.get("mineralWarningsCount", 0),
        "gas_warnings": gs.get("gasWarningsCount", 0),
        "supply_warnings": gs.get("supplyWarningsCount", 0),
        "idle_worker_warnings": gs.get("idleWorkersWarningsCount", 0),
        "status": "live",
        "last_updated": record.get("lastUpdated", datetime.now().isoformat(timespec="seconds")),
    }


async def migrate() -> None:
    async with get_db() as db:
        config_col = db.collection("config")
        stats_col = db.collection("game_stats")

        existing_config = await config_col.count()
        if existing_config == 0:
            if _CONFIG_YAML.exists():
                with open(_CONFIG_YAML) as f:
                    cfg = yaml.safe_load(f) or {}
                print(f"Migrating config from {_CONFIG_YAML}")
            else:
                cfg = {}
                print("No config.yaml found — inserting defaults")
            await config_col.create(_serialize_config(cfg))
            print("  config row created.")
        else:
            print("config table already has data, skipping.")

        existing_stats = await stats_col.count()
        if existing_stats == 0:
            migrated = 0
            if _STATS_JSON.exists():
                with open(_STATS_JSON) as f:
                    records = json.load(f)
                if isinstance(records, list):
                    for rec in records:
                        await stats_col.create(_serialize_stats(rec))
                        migrated += 1
                print(f"Migrated {migrated} completed games from {_STATS_JSON}")

            if _LIVE_JSON.exists():
                with open(_LIVE_JSON) as f:
                    live = json.load(f)
                await stats_col.create(_serialize_live(live))
                print(f"Migrated live game from {_LIVE_JSON}")
        else:
            print("game_stats table already has data, skipping.")

    print(f"Done. DB: {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(migrate())
