"""Dev runner: watches src/ for .py changes and auto-restarts the app."""
import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

WATCH_DIR = Path(__file__).parent / "src"
APP_ENTRY = Path(__file__).parent / "src" / "frontend" / "sc2_ui.py"


class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.proc: subprocess.Popen | None = None
        self._last_restart = 0.0
        self.start()

    def start(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()
        print(">> Starting app...")
        self.proc = subprocess.Popen(
            [sys.executable, str(APP_ENTRY)],
            cwd=str(APP_ENTRY.parent),
        )

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            now = time.monotonic()
            if now - self._last_restart < 0.5:
                return
            self._last_restart = now
            print(f">> Changed: {event.src_path}")
            self.start()


if __name__ == "__main__":
    handler = RestartHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=True)
    observer.start()
    print(f">> Watching {WATCH_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.proc and handler.proc.poll() is None:
            handler.proc.terminate()
    observer.join()
