"""Smoke tests for SpeechQueue — no actual TTS subprocess spawned."""
import queue
import time
from unittest.mock import patch

import pytest

from backend.sc2_helper import SpeechQueue, PRIORITY_SUPPLY, PRIORITY_MINERALS


def test_speak_enqueues_without_error():
    with patch("subprocess.run"):
        sq = SpeechQueue()
        sq.speak("test message", priority=5)


def test_priority_ordering():
    """Lower priority number = higher urgency = dequeued first."""
    results: list[int] = []

    def fake_run(cmd, **_):
        pass

    with patch("subprocess.run", side_effect=fake_run):
        sq = SpeechQueue()
        # Pause worker so we can inspect queue order
        sq._queue.put((PRIORITY_SUPPLY, 1, "supply msg", ""))
        sq._queue.put((PRIORITY_MINERALS, 2, "mineral msg", ""))

        first = sq._queue.get()
        assert first[0] == PRIORITY_SUPPLY, "Supply (lower priority number) should come first"
        sq._queue.task_done()

        second = sq._queue.get()
        assert second[0] == PRIORITY_MINERALS
        sq._queue.task_done()


def test_counter_increments():
    with patch("subprocess.run"):
        sq = SpeechQueue()
        assert sq._counter == 0
        sq.speak("a", priority=1)
        sq.speak("b", priority=1)
        # Counter may have incremented in worker thread — check ≥ 2
        time.sleep(0.05)
        assert sq._counter >= 2
