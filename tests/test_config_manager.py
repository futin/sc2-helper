"""Smoke tests for config get/save round-trips."""
import pytest

import backend.db as db_module
from frontend.config_manager import get_config, save_config, DEFAULT_CONFIG
from backend.hud.elements import HUD_ELEMENTS


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.db")


def test_get_config_returns_defaults_on_empty_db():
    cfg = get_config()
    assert cfg["poll_interval"] == DEFAULT_CONFIG["poll_interval"]
    assert "screen_capture" in cfg


def test_save_and_get_roundtrip():
    get_config()  # seed the row
    modified = dict(DEFAULT_CONFIG)
    modified["poll_interval"] = 3.0
    save_config(modified)

    loaded = get_config()
    assert loaded["poll_interval"] == 3.0


def test_default_screen_capture_has_all_hud_elements():
    cfg = dict(DEFAULT_CONFIG)
    sc = cfg["screen_capture"]
    for e in HUD_ELEMENTS:
        assert e.key in sc, f"{e.key} missing from default screen_capture"
        region = sc[e.key]
        assert len(region) == 4, f"{e.key} region should be [x, y, w, h]"
        w, h = region[2], region[3]
        assert (w, h) == e.default_size, f"{e.key} size mismatch: got {(w, h)}, expected {e.default_size}"


def test_get_config_returns_defaults_on_fresh_db():
    cfg = get_config()
    assert cfg["poll_interval"] == DEFAULT_CONFIG["poll_interval"]
