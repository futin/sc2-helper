import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

SCRIPT_PATH = Path(__file__).parent.parent / "backend" / "sc2_helper.py"


class RunnerScreen(tk.Toplevel):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.title("SC2 Helper — Runner")
        self.geometry("720x480")
        self.minsize(500, 300)

        self._process: subprocess.Popen | None = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._polling: bool = False

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self) -> None:
        # ---- Control bar ----
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")

        self._btn_start = ttk.Button(bar, text="▶  Start", command=self._start, width=10)
        self._btn_start.pack(side="left", padx=(0, 6))

        self._btn_stop = ttk.Button(bar, text="■  Stop", command=self._stop, width=10, state="disabled")
        self._btn_stop.pack(side="left")

        self._status_lbl = ttk.Label(bar, text="Not running", foreground="#888")
        self._status_lbl.pack(side="left", padx=12)

        ttk.Button(bar, text="Clear Log", command=self._clear_log).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # ---- Log area ----
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._log = tk.Text(
            log_frame, state="disabled", wrap="word",
            font=("Menlo", 11), background="#1e1e1e", foreground="#d4d4d4",
            insertbackground="white", relief="flat",
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self._log.yview)
        self._log.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._log.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------------ #
    # Process management
    # ------------------------------------------------------------------ #

    def _start(self) -> None:
        if self._process is not None:
            return
        self._append_log(f"--- Starting {SCRIPT_PATH.name} ---\n")
        try:
            self._process = subprocess.Popen(
                [sys.executable, str(SCRIPT_PATH)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as e:
            self._append_log(f"ERROR: Could not start process: {e}\n")
            return

        self._polling = True
        threading.Thread(target=self._read_output, daemon=True).start()
        self._schedule_queue_check()

        self._btn_start.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._status_lbl.config(text="Running", foreground="#00aa00")

    def _stop(self) -> None:
        self._polling = False
        if self._process:
            self._process.terminate()
            self._process = None
        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled")
        self._status_lbl.config(text="Stopped", foreground="#aa4400")
        self._append_log("--- Process stopped ---\n")

    def _on_process_ended(self) -> None:
        self._polling = False
        self._process = None
        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled")
        self._status_lbl.config(text="Exited", foreground="#888")
        self._append_log("--- Process exited ---\n")

    def _on_close(self) -> None:
        self._stop()
        self.destroy()

    # ------------------------------------------------------------------ #
    # Threading: reader + queue drain
    # ------------------------------------------------------------------ #

    def _read_output(self) -> None:
        """Daemon thread — reads stdout lines into queue. Never touches tk."""
        for line in self._process.stdout:
            self._queue.put(line)
        self._queue.put(None)  # sentinel

    def _schedule_queue_check(self) -> None:
        self.after(100, self._check_queue)

    def _check_queue(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                if item is None:
                    self._on_process_ended()
                    return
                self._append_log(item)
        except queue.Empty:
            pass
        if self._polling:
            self.after(100, self._check_queue)

    # ------------------------------------------------------------------ #
    # Log helpers
    # ------------------------------------------------------------------ #

    def _append_log(self, text: str) -> None:
        self._log.config(state="normal")
        self._log.insert("end", text)
        self._log.config(state="disabled")
        self._log.see("end")

    def _clear_log(self) -> None:
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")
