# Voice Listener

> 10 nodes · cohesion 0.50

## Key Concepts

- **VoiceListener** (10 connections) — `src/backend/classes/voice_listener.py`
- **._parse_command()** (4 connections) — `src/backend/classes/voice_listener.py`
- **voice_listener.py** (3 connections) — `src/backend/classes/voice_listener.py`
- **._listen_loop()** (3 connections) — `src/backend/classes/voice_listener.py`
- **._transcribe()** (3 connections) — `src/backend/classes/voice_listener.py`
- **VoiceCommand** (2 connections) — `src/backend/classes/voice_listener.py`
- **.__init__()** (1 connections) — `src/backend/classes/voice_listener.py`
- **.start()** (1 connections) — `src/backend/classes/voice_listener.py`
- **.stop()** (1 connections) — `src/backend/classes/voice_listener.py`
- **Voice listener — background thread that listens for a wake word then transcribes** (1 connections) — `src/backend/classes/voice_listener.py`

## Relationships

- [[Project Architecture Docs]] (28 shared connections)
- [[Database Query Layer]] (1 shared connections)

## Source Files

- `src/backend/classes/voice_listener.py`

## Audit Trail

- EXTRACTED: 27 (93%)
- INFERRED: 2 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*