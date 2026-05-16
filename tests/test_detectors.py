"""Smoke tests for detector logic — no TTS subprocess spawned."""
from unittest.mock import MagicMock, patch

import pytest

from backend.sc2_helper import (
    CooldownTracker,
    SpeechQueue,
    check_resources,
    check_supply,
    check_idle_workers,
    PRIORITY_SUPPLY,
    PRIORITY_MINERALS,
    PRIORITY_GAS,
    PRIORITY_IDLE_WORKERS,
)

BASE_CONFIG = {
    "resources": {"mineral_threshold": 600, "gas_threshold": 600, "cooldown": 30},
    "supply": {
        "cooldown": 10,
        "tiers": [
            {"max_cap": 25, "gap": 3},
            {"max_cap": 50, "gap": 5},
            {"max_cap": 200, "gap": 10},
        ],
    },
    "workers": {"idle_seconds": 0, "cooldown": 30},
}

BELOW_THRESHOLD_STATE = {
    "minerals": 300, "gas": 300,
    "supply_used": 15, "supply_max": 25,
    "idle_workers": 0,
}

ABOVE_THRESHOLD_STATE = {
    "minerals": 800, "gas": 800,
    "supply_used": 24, "supply_max": 25,
    "idle_workers": 3,
}


def _make_speech() -> SpeechQueue:
    with patch("subprocess.run"):
        sq = SpeechQueue()
    sq.speak = MagicMock()
    return sq


def test_check_resources_no_speak_below_threshold():
    speech = _make_speech()
    cooldown = CooldownTracker()
    check_resources(BELOW_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    speech.speak.assert_not_called()


def test_check_resources_speaks_when_over_threshold():
    speech = _make_speech()
    cooldown = CooldownTracker()
    check_resources(ABOVE_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    assert speech.speak.call_count >= 1


def test_check_resources_cooldown_prevents_repeat():
    speech = _make_speech()
    cooldown = CooldownTracker()
    check_resources(ABOVE_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    first_count = speech.speak.call_count
    check_resources(ABOVE_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    assert speech.speak.call_count == first_count, "Cooldown should block second call"


def test_check_supply_speaks_when_capped():
    speech = _make_speech()
    cooldown = CooldownTracker()
    check_supply(ABOVE_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    speech.speak.assert_called_once()
    _, _, priority = speech.speak.call_args[0]
    assert priority == PRIORITY_SUPPLY


def test_check_supply_silent_when_ok():
    speech = _make_speech()
    cooldown = CooldownTracker()
    check_supply(BELOW_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", "strict")
    speech.speak.assert_not_called()


def test_check_idle_workers_speaks_when_idle():
    speech = _make_speech()
    cooldown = CooldownTracker()
    result = check_idle_workers(ABOVE_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", None, "strict")
    assert result is not None, "idle_onset should be set"
    speech.speak.assert_called_once()


def test_check_idle_workers_resets_on_zero():
    speech = _make_speech()
    cooldown = CooldownTracker()
    result = check_idle_workers(BELOW_THRESHOLD_STATE, BASE_CONFIG, cooldown, speech, "", 999.0, "strict")
    assert result is None, "idle_onset should reset to None when workers = 0"
