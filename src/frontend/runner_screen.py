import queue
import subprocess
import sys
import threading
import customtkinter as ctk
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent
BACKEND_MODULE = "backend.index"
SCRIPT_DISPLAY_NAME = "sc2-helper"


class RunnerScreen(ctk.CTkToplevel):
    def __init__(self, parent):
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
        bar = ctk.CTkFrame(self, height=44, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self._btn_start = ctk.CTkButton(bar, text="▶  Start", command=self._start, width=90)
        self._btn_start.pack(side="left", padx=(8, 4), pady=6)

        self._btn_stop = ctk.CTkButton(bar, text="■  Stop", command=self._stop, width=90, state="disabled")
        self._btn_stop.pack(side="left", padx=4, pady=6)

        self._status_lbl = ctk.CTkLabel(bar, text="Not running", text_color="gray")
        self._status_lbl.pack(side="left", padx=12)

        self._debug_var = ctk.BooleanVar(value=False)
        self._debug_check = ctk.CTkCheckBox(
            bar, text="Debug mode", variable=self._debug_var, width=110
        )
        self._debug_check.pack(side="left", padx=12)

        ctk.CTkButton(bar, text="Clear Log", command=self._clear_log, width=80).pack(side="right", padx=8, pady=6)

        self._log = ctk.CTkTextbox(
            self, wrap="word",
            font=ctk.CTkFont(family="Menlo", size=11),
            state="disabled",
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)

    def _start(self) -> None:
        if self._process is not None:
            return
        self._append_log(f"--- Starting {SCRIPT_DISPLAY_NAME} ---\n")
        try:
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
        except Exception as e:
            self._append_log(f"ERROR: Could not start process: {e}\n")
            return

        self._polling = True
        threading.Thread(target=self._read_output, daemon=True).start()
        self._schedule_queue_check()

        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._debug_check.configure(state="disabled")
        self._status_lbl.configure(text="Running", text_color="green")

    def _stop(self) -> None:
        self._polling = False
        if self._process:
            self._process.terminate()
            self._process = None
        self._btn_start.configure(state="normal")
        self._debug_check.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        self._status_lbl.configure(text="Stopped", text_color="orange")
        self._append_log("--- Process stopped ---\n")

    def _on_process_ended(self) -> None:
        self._polling = False
        self._process = None
        self._btn_start.configure(state="normal")
        self._debug_check.configure(state="normal")
        self._btn_stop.configure(state="disabled")
        self._status_lbl.configure(text="Exited", text_color="gray")
        self._append_log("--- Process exited ---\n")

    def _on_close(self) -> None:
        self._stop()
        self.destroy()

    def _read_output(self) -> None:
        for line in self._process.stdout:
            self._queue.put(line)
        self._queue.put(None)

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

    def _append_log(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.configure(state="disabled")
        self._log.see("end")

    def _clear_log(self) -> None:
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
