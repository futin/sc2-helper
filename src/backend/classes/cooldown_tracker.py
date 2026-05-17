import time


class CooldownTracker:
    def __init__(self):
        self._last: dict = {}

    def ready(self, key: str, seconds: float) -> bool:
        """Return True (and record the time) if the cooldown has elapsed."""
        now = time.monotonic()
        if key not in self._last or now - self._last[key] >= seconds:
            self._last[key] = now
            return True
        return False
