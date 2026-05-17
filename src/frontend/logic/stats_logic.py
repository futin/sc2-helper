import json

from backend.stats import StatsManager


class StatsLoader:
    def load_history(self) -> list[dict]:
        try:
            text = StatsManager.STATS_PATH.read_text()
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_live(self) -> dict | None:
        try:
            text = StatsManager.LIVE_PATH.read_text()
            return json.loads(text)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
