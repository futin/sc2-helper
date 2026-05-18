import queue
import threading
from unittest.mock import MagicMock, patch

import pytest

from backend.classes.wake_word_detector import WakeWordDetector


def test_init_sets_attributes():
    called = []
    detector = WakeWordDetector(
        model_name="alexa",
        sensitivity=0.7,
        on_wake=lambda: called.append(1),
        chunk_ms=80,
    )
    assert detector._model_name == "alexa"
    assert detector._sensitivity == 0.7
    assert detector._chunk_ms == 80
    assert not detector._stop_event.is_set()


def test_stop_sets_event():
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: None)
    detector.stop()
    assert detector._stop_event.is_set()


def test_detect_loop_logs_error_on_missing_import():
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: None)
    with patch.dict("sys.modules", {"pyaudio": None, "openwakeword": None, "openwakeword.model": None}):
        # Should return without raising
        detector._detect_loop()


def test_detect_loop_calls_on_wake_when_threshold_met():
    called = []
    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=lambda: called.append(1))

    mock_model = MagicMock()
    mock_model.predict.return_value = {"alexa": 0.9}

    mock_stream = MagicMock()
    import numpy as np
    mock_stream.read.side_effect = [
        np.zeros(1280, dtype=np.int16).tobytes(),
        StopIteration,  # exit loop after one iteration
    ]

    mock_audio = MagicMock()
    mock_audio.open.return_value = mock_stream

    mock_pyaudio = MagicMock()
    mock_pyaudio.PyAudio.return_value = mock_audio
    mock_pyaudio.paInt16 = 8

    mock_oww_model = MagicMock()
    mock_oww_model.Model.return_value = mock_model

    detector._stop_event.set()  # stop after first chunk

    with patch.dict("sys.modules", {"pyaudio": mock_pyaudio, "openwakeword": MagicMock(), "openwakeword.model": mock_oww_model}):
        with patch("numpy.frombuffer", return_value=np.zeros(1280, dtype=np.int16)):
            detector._stop_event.clear()
            # Run one iteration by patching stop_event to stop after on_wake
            original_on_wake = detector._on_wake
            def stopping_on_wake():
                original_on_wake()
                detector._stop_event.set()
            detector._on_wake = stopping_on_wake
            detector._detect_loop()

    assert len(called) == 1
