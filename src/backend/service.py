"""
Service layer — the only entry point for frontend to access config and stats.
Frontend must never import from backend.db directly.
"""

import asyncio
import json
from datetime import datetime

from backend.db import get_db
from backend.hud_elements import HUD_ELEMENTS

_DEFAULT_COORDS: dict[str, tuple[int, int]] = {
    "minerals":     (2026, 30),
    "gas":          (2193, 30),
    "supply":       (2358, 30),
    "idle_workers": (65, 999),
}

DEFAULT_CONFIG: dict = {
    "poll_interval": 2.5,
    "resources": {"mineral_threshold": 600, "gas_threshold": 600, "cooldown": 30},
    "supply": {
        "cooldown": 10,
        "tiers": [
            {"max_cap": 25, "gap": 3},
            {"max_cap": 50, "gap": 5},
            {"max_cap": 200, "gap": 10},
        ],
    },
    "workers": {"idle_seconds": 10, "cooldown": 30},
    "player_id": 1,
    "tts_voice": "Moira",
    "message_mode": "strict",
    "screen_capture": {
        **{
            e.key: [*_DEFAULT_COORDS[e.key], *e.default_size]
            for e in HUD_ELEMENTS
        },
        "ocr_threshold": 100,
    },
    "anomaly_filter": {
        "enabled": True,
        "max_delta": {"minerals": 1000, "gas": 500, "supply_used": 10, "supply_max": 16},
    },
    "custom_messages": {
        "minerals": [],
        "gas": [],
        "supply": [],
        "idle_workers": [],
    },
    "voice_control": {
        "enabled": False,
        "wake_word_model": "alexa",
        "wake_sensitivity": 0.5,
        "stt_backend": "google",
        "silence_duration": 120,
        "pause_threshold": 1.2,
        "phrase_time_limit": 8,
    },
}

_JSON_FIELDS = ("resources", "supply", "workers", "screen_capture", "anomaly_filter", "custom_messages", "voice_control")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _row_to_config(row: dict) -> dict:
    cfg = dict(row)
    cfg.pop("id", None)
    cfg.pop("updated_at", None)
    for field in _JSON_FIELDS:
        if field in cfg and isinstance(cfg[field], str):
            cfg[field] = json.loads(cfg[field])
    return cfg


def _config_to_row(cfg: dict) -> dict:
    row = {}
    row["poll_interval"] = cfg.get("poll_interval", DEFAULT_CONFIG["poll_interval"])
    row["player_id"] = cfg.get("player_id", DEFAULT_CONFIG["player_id"])
    row["tts_voice"] = cfg.get("tts_voice", DEFAULT_CONFIG["tts_voice"])
    row["message_mode"] = cfg.get("message_mode", DEFAULT_CONFIG["message_mode"])
    for field in _JSON_FIELDS:
        val = cfg.get(field, DEFAULT_CONFIG.get(field, {}))
        row[field] = json.dumps(val) if not isinstance(val, str) else val
    row["updated_at"] = datetime.now().isoformat(timespec="seconds")
    return row


def get_config() -> dict:
    async def _get():
        async with get_db() as db:
            col = db.collection("config")
            row = await col.findOne()
            if row is None:
                await col.create({"id": 1, **_config_to_row(DEFAULT_CONFIG)})
                return dict(DEFAULT_CONFIG)
            return _row_to_config(row)
    return asyncio.run(_get())


def save_config(cfg: dict) -> None:
    async def _save():
        async with get_db() as db:
            col = db.collection("config")
            await col.updateOne({"id": 1}, _config_to_row(cfg))
    asyncio.run(_save())


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def _row_to_record(row: dict) -> dict:
    return {
        "gameId": row["game_id"],
        "matchDate": row["match_date"],
        "gameDuration": row.get("game_duration") or "—",
        "result": row.get("result") or "—",
        "race": row.get("race") or "—",
        "gameStats": {
            "mineralWarningsCount": row["mineral_warnings"],
            "gasWarningsCount": row["gas_warnings"],
            "supplyWarningsCount": row["supply_warnings"],
            "idleWorkersWarningsCount": row["idle_worker_warnings"],
        },
    }


def _row_to_live(row: dict) -> dict:
    return {
        "gameId": row["game_id"],
        "matchDate": row["match_date"],
        "lastUpdated": row["last_updated"],
        "gameStats": {
            "mineralWarningsCount": row["mineral_warnings"],
            "gasWarningsCount": row["gas_warnings"],
            "supplyWarningsCount": row["supply_warnings"],
            "idleWorkersWarningsCount": row["idle_worker_warnings"],
        },
    }


def get_stats_history() -> list[dict]:
    async def _get():
        async with get_db() as db:
            col = db.collection("game_stats")
            rows = await col.find({"status": "complete"}, sort="match_date ASC")
            return [_row_to_record(r) for r in rows]
    try:
        return asyncio.run(_get())
    except Exception:
        return []


def get_live_stats() -> dict | None:
    async def _get():
        async with get_db() as db:
            col = db.collection("game_stats")
            row = await col.findOne({"status": "live"})
            return _row_to_live(row) if row else None
    try:
        return asyncio.run(_get())
    except Exception:
        return None
