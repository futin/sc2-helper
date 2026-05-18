# Message Banks & Tests

> 9 nodes · cohesion 0.50

## Key Concepts

- **get_message()** (9 connections) — `src/backend/messages.py`
- **test_messages.py** (6 connections) — `tests/test_messages.py`
- **test_strict_mode_returns_exact_string()** (2 connections) — `tests/test_messages.py`
- **test_funny_mode_returns_non_empty()** (2 connections) — `tests/test_messages.py`
- **test_custom_mode_uses_custom_messages()** (2 connections) — `tests/test_messages.py`
- **test_custom_mode_falls_back_to_strict_when_empty()** (2 connections) — `tests/test_messages.py`
- **test_custom_mode_falls_back_when_category_missing()** (2 connections) — `tests/test_messages.py`
- **Smoke tests for message selection logic.** (1 connections) — `tests/test_messages.py`
- **messages.py** (1 connections) — `src/backend/messages.py`

## Relationships

- [[Frontend Application]] (27 shared connections)

## Source Files

- `src/backend/messages.py`
- `tests/test_messages.py`

## Audit Trail

- EXTRACTED: 14 (52%)
- INFERRED: 13 (48%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*