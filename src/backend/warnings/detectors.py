# src/backend/warnings/detectors.py
import time
from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.constants import (
    PRIORITY_MINERALS, PRIORITY_GAS, PRIORITY_SUPPLY, PRIORITY_IDLE_WORKERS,
)
from backend.warnings.messages import get_message


def check_resources(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> None:
    minerals = state["minerals"]
    gas = state["gas"]
    res_cfg = config["resources"]

    if minerals is not None and minerals > res_cfg["mineral_threshold"] and cooldown.ready("minerals", res_cfg["cooldown"]):
        speech.speak(get_message("minerals", mode, custom_messages), voice, PRIORITY_MINERALS)
        if stats:
            stats.on_mineral_warning()
    if gas is not None and gas > res_cfg["gas_threshold"] and cooldown.ready("gas", res_cfg["cooldown"]):
        speech.speak(get_message("gas", mode, custom_messages), voice, PRIORITY_GAS)
        if stats:
            stats.on_gas_warning()


def check_supply(
    state: dict, config: dict, cooldown: CooldownTracker, speech: SpeechQueue,
    voice: str, mode: str, custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> None:
    supply_used = state["supply_used"]
    supply_max = state["supply_max"]

    if supply_used is None or supply_max is None or supply_max == 0:
        return

    supply_cfg = config["supply"]
    gap = supply_max - supply_used

    warn_gap = None
    for tier in supply_cfg["tiers"]:
        if supply_max <= tier["max_cap"]:
            warn_gap = tier["gap"]
            break

    if warn_gap is not None and gap <= warn_gap and cooldown.ready("supply", supply_cfg["cooldown"]):
        speech.speak(get_message("supply", mode, custom_messages), voice, PRIORITY_SUPPLY)
        if stats:
            stats.on_supply_warning()


def check_idle_workers(
    state: dict,
    config: dict,
    cooldown: CooldownTracker,
    speech: SpeechQueue,
    voice: str,
    idle_onset: Optional[float],
    mode: str = "strict",
    custom_messages: dict | None = None,
    stats: "GameHistoryManager | None" = None,
) -> Optional[float]:
    """Track idle workers. Returns updated idle_onset (or None if busy)."""
    idle_count = state["idle_workers"]
    workers_cfg = config["workers"]

    if idle_count is None or idle_count == 0:
        return None

    if idle_onset is None:
        idle_onset = time.monotonic()

    elapsed = time.monotonic() - idle_onset
    if elapsed >= workers_cfg["idle_seconds"] and cooldown.ready("workers", workers_cfg["cooldown"]):
        speech.speak(get_message("idle_workers", mode, custom_messages), voice, PRIORITY_IDLE_WORKERS)
        if stats:
            stats.on_idle_workers_warning()

    return idle_onset
