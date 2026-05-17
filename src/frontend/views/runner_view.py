import customtkinter as ctk

from frontend.logic.runner_logic import RunnerController

SCRIPT_DISPLAY_NAME = "sc2-helper"


class RunnerScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("SC2 Helper — Runner")
        self.geometry("720x480")
        self.minsize(500, 300)

        self._runner_ctrl = RunnerController(
            on_log=self._append_log,
            on_status=self._update_status,
            schedule=self.after,
        )

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
        self._append_log(f"--- Starting {SCRIPT_DISPLAY_NAME} ---\n")
        self._runner_ctrl.start(debug=self._debug_var.get())

    def _stop(self) -> None:
        self._runner_ctrl.stop()
        self._append_log("--- Process stopped ---\n")

    def _on_close(self) -> None:
        self._runner_ctrl.stop()
        self.destroy()

    def _update_status(self, state: str) -> None:
        if state == "running":
            self._btn_start.configure(state="disabled")
            self._btn_stop.configure(state="normal")
            self._debug_check.configure(state="disabled")
            self._status_lbl.configure(text="Running", text_color="green")
        elif state == "stopped":
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")
            self._debug_check.configure(state="normal")
            self._status_lbl.configure(text="Stopped", text_color="orange")
        elif state == "exited":
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")
            self._debug_check.configure(state="normal")
            self._status_lbl.configure(text="Exited", text_color="gray")
            self._append_log("--- Process exited ---\n")

    def _append_log(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.configure(state="disabled")
        self._log.see("end")

    def _clear_log(self) -> None:
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
