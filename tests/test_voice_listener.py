import queue
from unittest.mock import MagicMock, patch

import pytest

from backend.classes.voice_listener import VoiceCommand, VoiceListener


def _make_listener(q=None):
    return VoiceListener(
        stt_backend="google",
        command_queue=q or queue.Queue(),
        pause_threshold=1.2,
        phrase_time_limit=8,
    )


# --- _parse_command ---

def test_parse_supply():
    listener = _make_listener()
    cmd = listener._parse_command("alexa supply status")
    assert cmd is not None
    assert cmd.intent == "query_supply"


def test_parse_resources():
    listener = _make_listener()
    cmd = listener._parse_command("alexa how many minerals")
    assert cmd is not None
    assert cmd.intent == "query_resources"


def test_parse_silence_minutes():
    listener = _make_listener()
    cmd = listener._parse_command("alexa silent for 3 minutes")
    assert cmd is not None
    assert cmd.intent == "silence"
    assert cmd.params["seconds"] == 180


def test_parse_silence_seconds():
    listener = _make_listener()
    cmd = listener._parse_command("alexa silence for 30 seconds")
    assert cmd is not None
    assert cmd.intent == "silence"
    assert cmd.params["seconds"] == 30


def test_parse_unknown_returns_none():
    listener = _make_listener()
    cmd = listener._parse_command("alexa what is the weather")
    assert cmd is None


# --- handle_wake ---

def test_handle_wake_enqueues_command():
    q = queue.Queue()
    listener = _make_listener(q)

    mock_sr = MagicMock()
    mock_recognizer = MagicMock()
    mock_recognizer.recognize_google.return_value = "supply status"
    mock_sr.Recognizer.return_value = mock_recognizer
    mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=False)
    mock_sr.WaitTimeoutError = TimeoutError

    with patch.dict("sys.modules", {"speech_recognition": mock_sr}):
        listener.handle_wake()

    assert not q.empty()
    cmd = q.get_nowait()
    assert cmd.intent == "query_supply"


def test_handle_wake_timeout_does_not_enqueue():
    q = queue.Queue()
    listener = _make_listener(q)

    mock_sr = MagicMock()
    mock_recognizer = MagicMock()
    mock_sr.WaitTimeoutError = TimeoutError
    mock_recognizer.listen.side_effect = TimeoutError
    mock_sr.Recognizer.return_value = mock_recognizer
    mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("sys.modules", {"speech_recognition": mock_sr}):
        listener.handle_wake()

    assert q.empty()


def test_handle_wake_missing_import_does_not_raise():
    listener = _make_listener()
    with patch.dict("sys.modules", {"speech_recognition": None}):
        listener.handle_wake()  # should return cleanly
