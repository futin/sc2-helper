from backend.constants import _RESULT_MAP, _RACE_MAP


def _extract_result(players: list, player_id: int) -> str:
    """Extract Win/Loss/Tie for player_id from an already-fetched players list."""
    idx = player_id - 1
    if 0 <= idx < len(players):
        result = _RESULT_MAP.get(players[idx].get("result", ""))
        if result:
            return result
    for p in players:
        result = _RESULT_MAP.get(p.get("result", ""))
        if result:
            return result
    return "Unknown"


def _extract_race(players: list, player_id: int) -> str:
    """Extract the player's race from the players list."""
    idx = player_id - 1
    if 0 <= idx < len(players):
        return _RACE_MAP.get(players[idx].get("race", ""), "Unknown")
    return "Unknown"


def _format_debug_state(state: dict) -> str:
    def _v(val) -> str:
        return '?' if val is None else str(val)

    return (
        f"[DEBUG] minerals={_v(state['minerals'])}  gas={_v(state['gas'])}  "
        f"supply={_v(state['supply_used'])}/{_v(state['supply_max'])}  "
        f"idle_workers={_v(state['idle_workers'])}"
    )
