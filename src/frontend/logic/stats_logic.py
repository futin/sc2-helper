from backend.service import get_live_stats, get_stats_history


class StatsLoader:
    def load_history(self) -> list[dict]:
        return get_stats_history()


    def load_live(self) -> dict | None:
        return get_live_stats()
