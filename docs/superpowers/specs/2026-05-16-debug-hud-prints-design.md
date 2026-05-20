# Debug HUD Prints — Design

**Date:** 2026-05-16

## Context

OCR reads HUD regions (minerals, gas, supply, idle workers) each poll interval. No visibility into whether readings are correct. Need a way to verify OCR output without pausing the loop — both from CLI and from the UI runner.

## Goal

`--debug` flag runs the full main loop AND prints current game state to terminal every interval. Replace existing one-shot API dump. Also expose as a checkbox in `RunnerScreen` so dev mode works end-to-end.

## Changes

### `src/backend/index.py`

1. **Remove** `debug_mode()` — one-shot `/game` API dump no longer needed.
2. **`main()`** — detect `--debug` in `sys.argv`, pass `debug: bool` into loop body.
3. **Loop body** — after `fetch_game_state()`:
   - If state is not None: `print(f"[DEBUG] minerals={...}  gas={...}  supply={used}/{max}  idle_workers={...}")`
   - If state is None: `print("[DEBUG] no state (game not running or OCR failed)")`

### `src/frontend/runner_screen.py`

4. Add "Debug mode" `CTkCheckBox` to the toolbar (right of status label, left of Clear Log).
5. When starting subprocess, append `--debug` to args if checkbox is checked.
6. Debug prints flow into existing log textbox automatically (stdout is already piped).

## Output Format

```
[DEBUG] minerals=450  gas=120  supply=28/36  idle_workers=0
[DEBUG] no state (game not running or OCR failed)
```

## Branch

`feat/debug-hud-prints`

## Verification

**CLI:**
1. Run: `python3 -m backend.index --debug` with game running.
2. Confirm per-interval prints with correct HUD values.
3. Stop game — confirm "no state" prints.
4. Run without `--debug` — confirm no debug prints.

**UI (dev mode):**
1. Start `dev.py` or launch app normally.
2. Open Runner screen, check "Debug mode", click Start.
3. Confirm `[DEBUG]` lines appear in the log textbox each interval.
4. Uncheck "Debug mode", restart — confirm no debug lines.
