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
            on_state=self._update_tracking,
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

        self._build_tracking()

        self._log = ctk.CTkTextbox(
            self, wrap="word",
            font=ctk.CTkFont(family="Menlo", size=11),
            state="disabled",
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_tracking(self) -> None:
        frame = ctk.CTkFrame(self, height=68, corner_radius=6)
        frame.pack(fill="x", padx=8, pady=(4, 0))
        frame.pack_propagate(False)

        status_cell = ctk.CTkFrame(frame, fg_color="transparent", width=90)
        status_cell.pack(side="left", padx=(12, 4), pady=8)
        status_cell.pack_propagate(False)
        ctk.CTkLabel(status_cell, text="LIVE", font=ctk.CTkFont(size=9), text_color="gray50").pack(anchor="w")
        self._track_status = ctk.CTkLabel(status_cell, text="Not running", text_color="gray", font=ctk.CTkFont(size=11))
        self._track_status.pack(anchor="w")

        ctk.CTkFrame(frame, width=1, height=44, fg_color="gray40").pack(side="left", padx=8, pady=12)

        self._track_labels: dict[str, ctk.CTkLabel] = {}
        warn_keys = {"minerals": "mw", "gas": "gw", "supply": "sw", "idle": "iw"}
        for key, title in [("minerals", "Minerals"), ("gas", "Gas"), ("supply", "Supply"), ("idle", "Idle")]:
            cell = ctk.CTkFrame(frame, fg_color="transparent")
            cell.pack(side="left", padx=16, pady=4)
            ctk.CTkLabel(cell, text=title, font=ctk.CTkFont(size=9), text_color="gray50").pack()
            row = ctk.CTkFrame(cell, fg_color="transparent")
            row.pack()
            val_lbl = ctk.CTkLabel(row, text="—", font=ctk.CTkFont(size=13, weight="bold"))
            val_lbl.pack(side="left")
            warn_lbl = ctk.CTkLabel(row, text="", font=ctk.CTkFont(size=10), text_color="gray50")
            warn_lbl.pack(side="left", padx=(4, 0))
            self._track_labels[key] = val_lbl
            self._track_labels[warn_keys[key]] = warn_lbl

    _WARN_LABEL_KEYS = {"mw", "gw", "sw", "iw"}

    def _update_tracking(self, state_str: str) -> None:
        if state_str == "game=idle":
            self._track_status.configure(text="No game", text_color="gray")
            for key, lbl in self._track_labels.items():
                lbl.configure(text="—" if key not in self._WARN_LABEL_KEYS else "")
            return
        parts: dict[str, str] = {}
        for part in state_str.split():
            k, _, v = part.partition("=")
            parts[k] = v
        self._track_status.configure(text="In game", text_color="green")
        self._track_labels["minerals"].configure(text=parts.get("minerals", "?"))
        self._track_labels["gas"].configure(text=parts.get("gas", "?"))
        self._track_labels["supply"].configure(text=parts.get("supply", "?"))
        self._track_labels["idle"].configure(text=parts.get("idle", "?"))
        for wk in ("mw", "gw", "sw", "iw"):
            n = parts.get(wk, "0")
            self._track_labels[wk].configure(text=f"⚠ {n}" if n != "0" else "")

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
            self._reset_tracking()
        elif state == "exited":
            self._btn_start.configure(state="normal")
            self._btn_stop.configure(state="disabled")
            self._debug_check.configure(state="normal")
            self._status_lbl.configure(text="Exited", text_color="gray")
            self._append_log("--- Process exited ---\n")
            self._reset_tracking()

    def _reset_tracking(self) -> None:
        self._track_status.configure(text="Not running", text_color="gray")
        for key, lbl in self._track_labels.items():
            lbl.configure(text="—" if key not in self._WARN_LABEL_KEYS else "")

    def _append_log(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text)
        self._log.configure(state="disabled")
        self._log.see("end")

    def _clear_log(self) -> None:
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
