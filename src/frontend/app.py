import tkinter as tk
from tkinter import messagebox, ttk

from config_manager import CONFIG_PATH, load_config, save_config
from runner_screen import RunnerScreen
from settings_screen import SettingsScreen


class SC2HelperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SC2 Helper")
        self.geometry("660x700")
        self.minsize(500, 400)

        self._cfg = load_config()
        self._runner: RunnerScreen | None = None

        self._build()

    def _build(self) -> None:
        # ---- Top bar ----
        bar = ttk.Frame(self, padding=(10, 8))
        bar.pack(fill="x")

        ttk.Label(bar, text="SC2 Helper", font=("", 14, "bold")).pack(side="left")
        ttk.Button(bar, text="▶  Run Script", command=self._open_runner).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # ---- Settings ----
        self._settings = SettingsScreen(self, self._cfg, on_save=self._handle_save)
        self._settings.pack(fill="both", expand=True)

    def _handle_save(self, cfg: dict) -> None:
        self._cfg = cfg
        save_config(cfg)
        self._settings.refresh(cfg)
        messagebox.showinfo("Saved", "Configuration saved to config.yaml")

    def _open_runner(self) -> None:
        if self._runner is not None and self._runner.winfo_exists():
            self._runner.lift()
            self._runner.focus_force()
            return
        self._runner = RunnerScreen(self)
