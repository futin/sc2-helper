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

    def remaining(self, key: str, seconds: float) -> float:
        """Return seconds left on cooldown, or 0 if ready."""
        if key not in self._last:
            return 0
        elapsed = time.monotonic() - self._last[key]
        return max(0.0, seconds - elapsed)
