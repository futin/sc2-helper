from backend.service import get_stats_history


class StatsLoader:
    def load_history(self) -> list[dict]:
        return get_stats_history()
