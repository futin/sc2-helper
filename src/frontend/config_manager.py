from pathlib import Path
import yaml

from backend.hud_elements import HUD_ELEMENTS

CONFIG_PATH = Path(__file__).parent.parent / "backend" / "config.yaml"

# Default x,y positions — adjust via the Coords Selection tab in the GUI
_DEFAULT_COORDS: dict[str, tuple[int, int]] = {
    "minerals":     (2026, 30),
    "gas":          (2193, 30),
    "supply":       (2358, 30),
    "idle_workers": (65, 999),
}

_DEFAULT_CONFIG: dict = {
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
}


def load_config(path: Path = CONFIG_PATH) -> dict:
    try:
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        return cfg if cfg else dict(_DEFAULT_CONFIG)
    except FileNotFoundError:
        return dict(_DEFAULT_CONFIG)


def save_config(cfg: dict, path: Path = CONFIG_PATH) -> None:
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=None, sort_keys=False, allow_unicode=True)
