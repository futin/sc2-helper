import customtkinter as ctk
from tkinter import messagebox
from typing import Callable

from frontend.views.tabs import ConfigTab, MessagesTab, CoordsTab, StatsTab


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, cfg: dict, on_save: Callable[[dict], None]):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._cfg = cfg
        self._on_save = on_save
        self._build()

    def _build(self) -> None:
        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(fill="both", expand=True)

        self._tabview.add("Configuration")
        self._tabview.add("Messages")
        self._tabview.add("Coords Selection")
        self._tabview.add("Statistics")

        self._config_tab = ConfigTab(self._tabview.tab("Configuration"), self._cfg)
        self._config_tab.pack(fill="both", expand=True)

        self._messages_tab = MessagesTab(self._tabview.tab("Messages"), self._cfg)
        self._messages_tab.pack(fill="both", expand=True)

        self._coords_tab = CoordsTab(self._tabview.tab("Coords Selection"), self._cfg)
        self._coords_tab.pack(fill="both", expand=True)

        self._stats_tab = StatsTab(self._tabview.tab("Statistics"))
        self._stats_tab.pack(fill="both", expand=True)

        ctk.CTkButton(self, text="Save All", command=self._save, width=100).pack(anchor="e", pady=(0, 4))

    def _save(self) -> None:
        try:
            cfg = self._collect()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return
        self._on_save(cfg)

    def _collect(self) -> dict:
        cfg = dict(self._cfg)
        cfg.update(self._config_tab.collect())
        cfg.update(self._messages_tab.collect())
        return cfg

    def refresh(self, cfg: dict) -> None:
        self._cfg = cfg
        self._coords_tab.refresh(cfg)
