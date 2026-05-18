# TTS Speech Queue

> 11 nodes · cohesion 0.50

## Key Concepts

- **SpeechQueue** (9 connections) — `src/backend/classes/speech_queue.py`
- **test_speech_queue.py** (4 connections) — `tests/test_speech_queue.py`
- **test_priority_ordering()** (3 connections) — `tests/test_speech_queue.py`
- **test_speak_enqueues_without_error()** (2 connections) — `tests/test_speech_queue.py`
- **test_counter_increments()** (2 connections) — `tests/test_speech_queue.py`
- **Smoke tests for SpeechQueue — no actual TTS subprocess spawned.** (1 connections) — `tests/test_speech_queue.py`
- **Lower priority number = higher urgency = dequeued first.** (1 connections) — `tests/test_speech_queue.py`
- **speech_queue.py** (1 connections) — `src/backend/classes/speech_queue.py`
- **.__init__()** (1 connections) — `src/backend/classes/speech_queue.py`
- **._worker()** (1 connections) — `src/backend/classes/speech_queue.py`
- **.speak()** (1 connections) — `src/backend/classes/speech_queue.py`

## Relationships

- [[Voice Listener]] (24 shared connections)
- [[Frontend Application]] (1 shared connections)
- [[Game State Detectors]] (1 shared connections)

## Source Files

- `src/backend/classes/speech_queue.py`
- `tests/test_speech_queue.py`

## Audit Trail

- EXTRACTED: 18 (69%)
- INFERRED: 8 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*