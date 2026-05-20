# SC2 Helper — Claude Context

## Knowledge Graph (prefer over grep)

A knowledge graph for this project lives at `.understand-anything/knowledge-graph.json`.

**Always query the knowledge graph first** when answering questions about code structure, file relationships, imports, layers, or architecture. Use grep/Read only for:
- Specific line-level details not in the graph (exact implementation, runtime values)
- Verifying a graph claim before acting on it

To query the graph conversationally, use skill `understand-anything:understand-chat` — **not** `understand-anything:understand-knowledge` (that is for Karpathy-pattern wikis, not codebases).

To explore the graph interactively, run `/understand-dashboard` to launch the Vite dashboard. The graph contains 101 nodes, 135 edges, 7 architectural layers, and a 15-step guided tour. See [docs/knowledge-graph.md](../docs/knowledge-graph.md) for full tool documentation.

To regenerate after code changes: `/understand`

---

## Project Docs

- [Architecture & How it works](../docs/architecture.md)
- [Running & Requirements](../docs/running.md)
- [Configuration](../docs/configuration.md)
- [Game History](../docs/game_history.md)
- [Message Modes](../docs/messages.md)

---

## Project Structure

### Backend (`src/backend/`)

| File | Responsibility |
|------|---------------|
| `index.py` | Entry point — parse args, call `GameRunner.run()` |
| `runner.py` | `GameRunner` class — owns all game loop state |
| `constants.py` | `SC2_BASE`, `REQUEST_TIMEOUT`, `PRIORITY_*`, `_RESULT_MAP`, `_RACE_MAP` |
| `utils.py` | `_extract_result`, `_extract_race`, `_format_debug_state` |
| `logger.py` | `setup_logging()` |
| `service.py` | Service layer — `get_config`, `save_config`, `get_stats_history`, `get_live_stats` |
| `game_history.py` | `GameHistoryManager` — per-game warning counts → SQLite |
| `sounds.py` | Audio cue helpers |
| `find_coords.py` | Standalone calibration script (macOS, `__main__` block) |
| `hud/elements.py` | `HudElement` dataclass + `HUD_ELEMENTS` list |
| `hud/ocr.py` | Screen capture (`mss`) + Tesseract OCR functions |
| `hud/api.py` | SC2 API polling, HUD capture, spike filter |
| `hud/debug.py` | `test_ocr_mode()` — OCR debug helper |
| `warnings/detectors.py` | `check_resources`, `check_supply`, `check_idle_workers` |
| `warnings/messages.py` | Warning message banks + `get_message()` |
| `voice/listener.py` | `VoiceListener` + `VoiceCommand` |
| `voice/wake_word.py` | `WakeWordDetector` |
| `voice/commands.py` | `handle_command()` — voice intent → TTS response |
| `classes/speech_queue.py` | `SpeechQueue` — priority TTS daemon thread |
| `classes/cooldown_tracker.py` | `CooldownTracker` |
| `db/__init__.py` | `get_db()` context manager, `DB_PATH` |
| `db/connector.py` | Database abstraction base |
| `db/sqlite_connector.py` | `aiosqlite` implementation |
| `db/collection.py` | Collection query API (`find`/`findOne`/`create`/`updateOne`) |
| `db/schema.py` | `CREATE TABLE` statements for `config` + `game_stats` |

### Frontend (`src/frontend/`)

**Views** (`views/`) — pure UI, no file I/O or subprocess logic:

| File | Responsibility |
|------|---------------|
| `views/runner_view.py` | `RunnerScreen` — Start/Stop UI, log display |
| `views/settings_view.py` | `SettingsScreen` — tab container + Save All |
| `views/tabs/config_tab.py` | Configuration tab (thresholds, tiers, OCR) |
| `views/tabs/messages_tab.py` | Message mode selector + custom message editor |
| `views/tabs/coords_tab.py` | HUD coordinate capture with countdown |
| `views/tabs/game_history_tab.py` | Game History dashboard |

**Logic** (`logic/`) — no UI code:

| File | Responsibility |
|------|---------------|
| `logic/runner_logic.py` | `RunnerController` — subprocess + thread management |
| `logic/game_history_logic.py` | `GameHistoryLoader` — reads history via `service.get_stats_history()` |

**Root:**

| File | Responsibility |
|------|---------------|
| `sc2_ui.py` | Entry point |
| `app.py` | `SC2HelperApp` root window |
| `config_manager.py` | Re-exports `get_config`, `save_config`, `DEFAULT_CONFIG` from `service` |

---

## Development Guidelines

### Think Before Coding

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity First

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### Surgical Changes

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting unless asked.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused. Don't remove pre-existing dead code unless asked.

### Goal-Driven Execution

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
