import threading
from unittest.mock import MagicMock, patch

import numpy as np

from backend.voice.wake_word import WakeWordDetector


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
    assert detector._refractory_s == 2.0
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


def _make_detector_mocks(model_name="alexa", sensitivity=0.5, on_wake=None, score=0.9):
    """Return (detector, mock_pyaudio, mock_oww_model) configured for a single-pass loop."""
    if on_wake is None:
        on_wake = lambda: None
    detector = WakeWordDetector(model_name=model_name, sensitivity=sensitivity, on_wake=on_wake)

    mock_model = MagicMock()
    mock_model.predict.return_value = {model_name: score}

    mock_stream = MagicMock()
    mock_stream.read.return_value = np.zeros(1280, dtype=np.int16).tobytes()
    mock_stream.get_read_available.return_value = 0

    mock_audio = MagicMock()
    mock_audio.open.return_value = mock_stream

    mock_pyaudio = MagicMock()
    mock_pyaudio.PyAudio.return_value = mock_audio
    mock_pyaudio.paInt16 = 8

    mock_oww_model = MagicMock()
    mock_oww_model.Model.return_value = mock_model

    return detector, mock_pyaudio, mock_oww_model


def test_detect_loop_calls_on_wake_when_threshold_met():
    called = []

    def stopping_on_wake():
        called.append(1)
        detector._stop_event.set()

    detector, mock_pyaudio, mock_oww_model = _make_detector_mocks(on_wake=stopping_on_wake)

    with patch.dict("sys.modules", {"pyaudio": mock_pyaudio, "openwakeword": MagicMock(), "openwakeword.model": mock_oww_model}):
        with patch("numpy.frombuffer", return_value=np.zeros(1280, dtype=np.int16)):
            detector._detect_loop()

    assert len(called) == 1


def test_detect_loop_refractory_suppresses_second_wake():
    """Second above-threshold chunk within refractory_s must not trigger on_wake again."""
    called = []

    # Use a very long refractory period so the second call is definitely suppressed.
    detector = WakeWordDetector(
        model_name="alexa",
        sensitivity=0.5,
        on_wake=lambda: called.append(1),
        refractory_s=60.0,
    )

    mock_model = MagicMock()
    mock_model.predict.return_value = {"alexa": 0.9}

    chunk = np.zeros(1280, dtype=np.int16).tobytes()

    iteration = [0]

    def read_side_effect(*args, **kwargs):
        iteration[0] += 1
        if iteration[0] >= 3:
            detector._stop_event.set()
        return chunk

    mock_stream = MagicMock()
    mock_stream.read.side_effect = read_side_effect
    mock_stream.get_read_available.return_value = 0

    mock_audio = MagicMock()
    mock_audio.open.return_value = mock_stream

    mock_pyaudio = MagicMock()
    mock_pyaudio.PyAudio.return_value = mock_audio
    mock_pyaudio.paInt16 = 8

    mock_oww_model = MagicMock()
    mock_oww_model.Model.return_value = mock_model

    with patch.dict("sys.modules", {"pyaudio": mock_pyaudio, "openwakeword": MagicMock(), "openwakeword.model": mock_oww_model}):
        with patch("numpy.frombuffer", return_value=np.zeros(1280, dtype=np.int16)):
            detector._detect_loop()

    # Despite multiple high-score chunks, on_wake should only fire once.
    assert len(called) == 1


def test_detect_loop_recovers_from_audio_read_error():
    """Loop must not crash on stream.read raising an exception."""
    called = []

    iteration = [0]

    def read_side_effect(*args, **kwargs):
        iteration[0] += 1
        if iteration[0] == 1:
            raise OSError("buffer underrun")
        detector._stop_event.set()
        return np.zeros(1280, dtype=np.int16).tobytes()

    def stopping_on_wake():
        called.append(1)

    detector = WakeWordDetector(model_name="alexa", sensitivity=0.5, on_wake=stopping_on_wake)

    mock_model = MagicMock()
    mock_model.predict.return_value = {"alexa": 0.9}

    mock_stream = MagicMock()
    mock_stream.read.side_effect = read_side_effect
    mock_stream.get_read_available.return_value = 0

    mock_audio = MagicMock()
    mock_audio.open.return_value = mock_stream

    mock_pyaudio = MagicMock()
    mock_pyaudio.PyAudio.return_value = mock_audio
    mock_pyaudio.paInt16 = 8

    mock_oww_model = MagicMock()
    mock_oww_model.Model.return_value = mock_model

    with patch.dict("sys.modules", {"pyaudio": mock_pyaudio, "openwakeword": MagicMock(), "openwakeword.model": mock_oww_model}):
        with patch("numpy.frombuffer", return_value=np.zeros(1280, dtype=np.int16)):
            detector._detect_loop()  # must not raise

    # Loop recovered: second chunk (after error) was processed and on_wake fired.
    assert len(called) == 1
