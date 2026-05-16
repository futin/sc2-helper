import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.index import _format_debug_state

_NO_STATE_LINE = "[DEBUG] no state (game not running or OCR failed)"


def test_debug_line_format():
    state = {"minerals": 450, "gas": 120, "supply_used": 28, "supply_max": 36, "idle_workers": 0}
    assert _format_debug_state(state) == "[DEBUG] minerals=450  gas=120  supply=28/36  idle_workers=0"


def test_debug_no_state_line_format():
    assert _NO_STATE_LINE.startswith("[DEBUG]")
    assert "no state" in _NO_STATE_LINE
