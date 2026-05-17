import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Callable

SRC_DIR = Path(__file__).parent.parent.parent
BACKEND_MODULE = "backend.index"


class RunnerController:
    def __init__(
        self,
        on_log: Callable[[str], None],
        on_status: Callable[[str], None],
        schedule: Callable[[int, Callable], None],
    ) -> None:
        self._on_log = on_log
        self._on_status = on_status
        self._schedule = schedule
        self._process: subprocess.Popen | None = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._polling: bool = False

    def start(self, debug: bool = False) -> bool:
        """Start the backend process. Returns False if already running."""
        if self._process is not None:
            return False
        cmd = [sys.executable, "-m", BACKEND_MODULE]
        if debug:
            cmd.append("--debug")
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(SRC_DIR),
            )
        except Exception as e:
            self._on_log(f"ERROR: Could not start process: {e}\n")
            return False

        self._polling = True
        threading.Thread(target=self._read_output, daemon=True).start()
        self._schedule(100, self._check_queue)
        self._on_status("running")
        return True

    def stop(self) -> None:
        self._polling = False
        if self._process:
            self._process.terminate()
            self._process = None
        self._on_status("stopped")

    def _read_output(self) -> None:
        for line in self._process.stdout:
            self._queue.put(line)
        self._queue.put(None)

    def _check_queue(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                if item is None:
                    self._polling = False
                    self._process = None
                    self._on_status("exited")
                    return
                self._on_log(item)
        except queue.Empty:
            pass
        if self._polling:
            self._schedule(100, self._check_queue)
