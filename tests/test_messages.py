"""Smoke tests for message selection logic."""
import pytest

from backend.messages import get_message, STRICT_MESSAGES


def test_strict_mode_returns_exact_string():
    for category in STRICT_MESSAGES:
        result = get_message(category, mode="strict")
        assert result == STRICT_MESSAGES[category]


def test_funny_mode_returns_non_empty():
    for category in ("supply", "minerals", "gas", "idle_workers"):
        result = get_message(category, mode="funny")
        assert isinstance(result, str) and result


def test_custom_mode_uses_custom_messages():
    custom = {"supply": ["custom supply warning"]}
    result = get_message("supply", mode="custom", custom_messages=custom)
    assert result == "custom supply warning"


def test_custom_mode_falls_back_to_strict_when_empty():
    result = get_message("supply", mode="custom", custom_messages={})
    assert result == STRICT_MESSAGES["supply"]


def test_custom_mode_falls_back_when_category_missing():
    result = get_message("minerals", mode="custom", custom_messages={"supply": ["x"]})
    assert result == STRICT_MESSAGES["minerals"]
