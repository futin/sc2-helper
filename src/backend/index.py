"""
SC2 Helper — captures the StarCraft II HUD via screen OCR and speaks audio warnings.

Endpoints used:
  GET http://localhost:6119/game   → game/player status only (no resource data)

Resource values (minerals, gas, supply, idle workers) are read via screen capture
and OCR from the HUD.

Run normally:
  python3 -m backend.index

Debug mode (runs main loop and prints HUD state each interval):
  python3 -m backend.index --debug

Test OCR mode (saves crops and prints OCR results for each HUD region):
  python3 -m backend.index --test-ocr
"""

import sys

from backend.hud.debug import test_ocr_mode
from backend.logger import setup_logging
from backend.runner import GameRunner
from backend.service import get_config


def main() -> None:
    if "--test-ocr" in sys.argv:
        test_ocr_mode()
        return
    debug: bool = "--debug" in sys.argv
    setup_logging(debug)
    GameRunner(get_config(), debug).run()


if __name__ == "__main__":
    main()
