# Running

## Requirements

- Python 3.11+
- macOS (TTS uses the `say` command)
- Tesseract OCR installed: `brew install tesseract`
- StarCraft II running with the client API enabled (port 6119)
- `customtkinter` — installed via `pip install -r requirements.txt`

```bash
pip install -r requirements.txt
```

## GUI (recommended)

```bash
python src/frontend/sc2_ui.py
```

Opens the settings window. Click **▶ Run Script** to open the runner panel, then **▶ Start**.

## Backend only

```bash
python -m backend.index
```

## Debug mode — print HUD state each poll interval

```bash
python -m backend.index --debug
```

Prints live OCR values (`minerals`, `gas`, `supply`, `idle_workers`) to stdout every tick. Also available as a checkbox in the GUI runner toolbar.

## Test OCR mode — verify OCR is reading each region correctly

```bash
python -m backend.index --test-ocr
```

Saves raw and pre-processed crops to `src/backend/ocr_debug/` and prints OCR results. Useful for tuning `ocr_threshold`.

## Dev mode — hot-reload on file changes

```bash
python dev.py
```

Watches `src/` for `.py` changes and auto-restarts the UI. Requires `watchdog` (included in `requirements.txt`).
