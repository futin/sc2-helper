"""Entry point for the SC2 Helper UI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app import SC2HelperApp

if __name__ == "__main__":
    SC2HelperApp().mainloop()
