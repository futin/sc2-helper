"""Smoke tests for config load/save round-trips."""
import tempfile
from pathlib import Path

import pytest
import yaml

from frontend.config_manager import load_config, save_config, _DEFAULT_CONFIG
from backend.hud_elements import HUD_ELEMENTS


def test_load_config_returns_defaults_on_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.yaml"
    cfg = load_config(missing)
    assert cfg["poll_interval"] == _DEFAULT_CONFIG["poll_interval"]
    assert "screen_capture" in cfg


def test_save_and_load_roundtrip(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    original = dict(_DEFAULT_CONFIG)
    original["poll_interval"] = 3.0
    save_config(original, cfg_path)

    loaded = load_config(cfg_path)
    assert loaded["poll_interval"] == 3.0


def test_default_screen_capture_has_all_hud_elements():
    cfg = dict(_DEFAULT_CONFIG)
    sc = cfg["screen_capture"]
    for e in HUD_ELEMENTS:
        assert e.key in sc, f"{e.key} missing from default screen_capture"
        region = sc[e.key]
        assert len(region) == 4, f"{e.key} region should be [x, y, w, h]"
        w, h = region[2], region[3]
        assert (w, h) == e.default_size, f"{e.key} size mismatch: got {(w, h)}, expected {e.default_size}"


def test_load_config_returns_default_on_empty_file(tmp_path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    cfg = load_config(empty)
    assert cfg["poll_interval"] == _DEFAULT_CONFIG["poll_interval"]
