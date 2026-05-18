# Voice Command Parsing

> 4 nodes · cohesion 0.50

## Key Concepts

- **VoiceListener._listen_loop** (2 connections) — `src/backend/classes/voice_listener.py`
- **VoiceListener._parse_command** (2 connections) — `src/backend/classes/voice_listener.py`
- **VoiceCommand** (1 connections) — `src/backend/classes/voice_listener.py`
- **VoiceListener._transcribe** (1 connections) — `src/backend/classes/voice_listener.py`

## Relationships

- [[HUD Coordinate Config]] (6 shared connections)

## Source Files

- `src/backend/classes/voice_listener.py`

## Audit Trail

- EXTRACTED: 6 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*