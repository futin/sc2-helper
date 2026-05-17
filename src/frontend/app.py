import customtkinter as ctk
from tkinter import messagebox

from frontend.config_manager import get_config, save_config
from frontend.views.runner_view import RunnerScreen
from frontend.views.settings_view import SettingsScreen

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class SC2HelperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SC2 Helper")
        self.geometry("660x700")
        self.minsize(500, 400)

        self._cfg = get_config()
        self._runner: RunnerScreen | None = None

        self._build()

    def _build(self) -> None:
        bar = ctk.CTkFrame(self, height=48, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="SC2 Helper", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=12)
        ctk.CTkButton(bar, text="▶  Run Script", command=self._open_runner, width=120).pack(side="right", padx=8, pady=6)

        self._settings = SettingsScreen(self, self._cfg, on_save=self._handle_save)
        self._settings.pack(fill="both", expand=True, padx=8, pady=8)

    def _handle_save(self, cfg: dict) -> None:
        self._cfg = cfg
        save_config(cfg)
        self._settings.refresh(cfg)
        messagebox.showinfo("Saved", "Configuration saved.")

    def _open_runner(self) -> None:
        if self._runner is not None and self._runner.winfo_exists():
            self._runner.lift()
            self._runner.focus_force()
            return
        self._runner = RunnerScreen(self)
