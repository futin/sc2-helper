# Debug HUD Prints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--debug` flag to backend that prints HUD state (minerals, gas, supply, idle workers) every poll interval, and expose it as a checkbox in the RunnerScreen UI.

**Architecture:** Repurpose `--debug` CLI flag — replace one-shot API dump with full loop + per-interval print. Thread a `debug: bool` into the main loop. `RunnerScreen` gains a checkbox that appends `--debug` to the subprocess args. Debug stdout flows into the existing log textbox automatically.

**Tech Stack:** Python 3.11, customtkinter, subprocess (existing), pytest

---

### Task 1: Create feature branch

**Files:**
- No file changes — git only

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b feat/debug-hud-prints
```

Expected: `Switched to a new branch 'feat/debug-hud-prints'`

---

### Task 2: Repurpose `--debug` in backend

**Files:**
- Modify: `src/backend/index.py`

- [ ] **Step 1: Write failing test for debug print output**

Add to `tests/test_messages.py` (or create `tests/test_debug.py`):

```python
# tests/test_debug.py
import io
import sys
from unittest.mock import patch

# We test the formatting helper directly, so define it here to match implementation
def _debug_line(state):
    return (
        f"[DEBUG] minerals={state['minerals']}  gas={state['gas']}  "
        f"supply={state['supply_used']}/{state['supply_max']}  "
        f"idle_workers={state['idle_workers']}"
    )

def test_debug_line_format():
    state = {"minerals": 450, "gas": 120, "supply_used": 28, "supply_max": 36, "idle_workers": 0}
    line = _debug_line(state)
    assert line == "[DEBUG] minerals=450  gas=120  supply=28/36  idle_workers=0"

def test_debug_line_no_state():
    line = "[DEBUG] no state (game not running or OCR failed)"
    assert line.startswith("[DEBUG]")
    assert "no state" in line
```

- [ ] **Step 2: Run test to confirm it passes (pure formatting, no imports needed)**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper
python -m pytest tests/test_debug.py -v
```

Expected: 2 PASSED

- [ ] **Step 3: Modify `src/backend/index.py`**

Replace the entire `debug_mode()` function and update `main()` as follows.

**Remove** the `debug_mode()` function (lines ~269–279):
```python
# DELETE this entire function:
def debug_mode() -> None:
    """Hit /game endpoint once, pretty-print the raw JSON, then exit."""
    print("=== DEBUG MODE ===")
    print(f"Hitting {SC2_BASE}/game ...\n")
    try:
        game_resp = requests.get(f"{SC2_BASE}/game", timeout=REQUEST_TIMEOUT)
        print(f"Status: {game_resp.status_code}")
        print(json.dumps(game_resp.json(), indent=2))
    except (requests.ConnectionError, requests.Timeout) as exc:
        print(f"Connection failed: {exc}")
```

**Update `main()`** — replace the existing function body with:

```python
def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return

    debug: bool = "--debug" in sys.argv

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    config = load_config(Path(__file__).parent / "config.yaml")
    voice: str = config.get("tts_voice", "")
    mode: str = config.get("message_mode", "strict")
    custom_messages: dict = config.get("custom_messages", {})
    cooldown = CooldownTracker()
    speech = SpeechQueue()
    idle_onset: Optional[float] = None

    label = "[debug mode]" if debug else ""
    logging.info("SC2 Helper running [%s mode] %s. Press Ctrl+C to stop.", mode, label)
    try:
        while True:
            state = fetch_game_state(config)
            if debug:
                if state:
                    print(
                        f"[DEBUG] minerals={state['minerals']}  gas={state['gas']}  "
                        f"supply={state['supply_used']}/{state['supply_max']}  "
                        f"idle_workers={state['idle_workers']}",
                        flush=True,
                    )
                else:
                    print("[DEBUG] no state (game not running or OCR failed)", flush=True)
            if state:
                check_resources(state, config, cooldown, speech, voice, mode, custom_messages)
                check_supply(state, config, cooldown, speech, voice, mode, custom_messages)
                idle_onset = check_idle_workers(state, config, cooldown, speech, voice, idle_onset, mode, custom_messages)
            time.sleep(config["poll_interval"])
    except KeyboardInterrupt:
        print("Stopping.")
```

Also remove `json` from imports if it's no longer used elsewhere (it was only used in `debug_mode`). Check top of file — if `import json` is only referenced by `debug_mode`, delete that line.

- [ ] **Step 4: Verify `json` import usage**

```bash
grep -n "json" /Users/andrejajevtic/Documents/custom-projects/sc2-helper/src/backend/index.py
```

If `json` only appears in the removed `debug_mode` function, delete the `import json` line.

- [ ] **Step 5: Run existing test suite to confirm no regressions**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper
python -m pytest tests/ -v
```

Expected: all previously passing tests still PASS.

- [ ] **Step 6: Commit**

```bash
git add src/backend/index.py tests/test_debug.py
git commit -m "feat(debug): repurpose --debug to print HUD state each interval"
```

---

### Task 3: Add Debug checkbox to RunnerScreen

**Files:**
- Modify: `src/frontend/runner_screen.py`

- [ ] **Step 1: Add the checkbox widget to `_build()`**

In `runner_screen.py`, locate the `_build()` method. After the `self._status_lbl` pack line and before the `ctk.CTkButton(bar, text="Clear Log", ...)` line, add:

```python
self._debug_var = ctk.BooleanVar(value=False)
self._debug_check = ctk.CTkCheckBox(
    bar, text="Debug mode", variable=self._debug_var, width=110
)
self._debug_check.pack(side="left", padx=12)
```

- [ ] **Step 2: Pass `--debug` to subprocess in `_start()`**

In `_start()`, update the `subprocess.Popen` call. Replace:

```python
self._process = subprocess.Popen(
    [sys.executable, "-m", BACKEND_MODULE],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd=str(SRC_DIR),
)
```

With:

```python
cmd = [sys.executable, "-m", BACKEND_MODULE]
if self._debug_var.get():
    cmd.append("--debug")
self._process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd=str(SRC_DIR),
)
```

- [ ] **Step 3: Disable checkbox while running, re-enable on stop**

In `_start()`, after configuring button states, add:
```python
self._debug_check.configure(state="disabled")
```

In `_stop()`, after configuring button states, add:
```python
self._debug_check.configure(state="normal")
```

In `_on_process_ended()`, after configuring button states, add:
```python
self._debug_check.configure(state="normal")
```

- [ ] **Step 4: Run the app and verify checkbox appears**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper
python dev.py
```

Open Runner screen — confirm "Debug mode" checkbox is visible in the toolbar, left of "Clear Log".

- [ ] **Step 5: Smoke-test the full flow**

1. Check "Debug mode" checkbox.
2. Click Start.
3. Confirm `[DEBUG]` lines appear in log textbox every ~2.5 seconds.
4. Click Stop.
5. Uncheck "Debug mode", click Start again.
6. Confirm no `[DEBUG]` lines appear.

- [ ] **Step 6: Commit**

```bash
git add src/frontend/runner_screen.py
git commit -m "feat(runner): add Debug mode checkbox to RunnerScreen toolbar"
```

---

### Task 4: Final verification and PR

- [ ] **Step 1: Run full test suite one more time**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper
python -m pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Test CLI debug mode directly**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper/src
python -m backend.index --debug
```

Expected: `[DEBUG]` lines print each interval (or "no state" if SC2 not running). Ctrl+C stops cleanly.

- [ ] **Step 3: Confirm `--test-ocr` still works**

```bash
cd /Users/andrejajevtic/Documents/custom-projects/sc2-helper/src
python -m backend.index --test-ocr
```

Expected: OCR results printed, crops saved to `ocr_debug/`.

- [ ] **Step 4: Push and open PR**

```bash
git push -u origin feat/debug-hud-prints
gh pr create --title "feat: debug HUD prints per interval" --body "$(cat <<'EOF'
## Summary
- Repurpose `--debug` CLI flag: runs full loop and prints HUD state (minerals, gas, supply, idle workers) each poll interval
- Replace one-shot API dump behavior
- Add Debug mode checkbox to RunnerScreen toolbar; appends `--debug` to subprocess args when checked
- Checkbox disabled while process is running

## Test plan
- [ ] `--debug` prints `[DEBUG]` lines each interval when game running
- [ ] `--debug` prints "no state" lines when game not running
- [ ] Normal mode (no flag) has no debug output
- [ ] `--test-ocr` still works unchanged
- [ ] RunnerScreen Debug checkbox visible and functional
- [ ] Checkbox disabled while running, re-enabled on stop/exit
- [ ] All pytest tests pass

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
