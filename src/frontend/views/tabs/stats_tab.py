import customtkinter as ctk

from frontend.logic.stats_logic import StatsLoader


class StatsTab(ctk.CTkFrame):
    POLL_MS = 5000

    _RESULT_COLORS = {
        "Win":     ("#1a7a1a", "#4caf50"),
        "Loss":    ("#a01010", "#ef5350"),
        "Tie":     ("#7a6a00", "#ffc107"),
        "Unknown": ("#555555", "#aaaaaa"),
    }

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._loader = StatsLoader()
        self._records: list[dict] = []
        self._selected_idx: int | None = None
        self._live_data: dict | None = None
        self._build()
        self._refresh()

    def _build(self) -> None:
        self._banner_slot = ctk.CTkFrame(self, fg_color="transparent")
        self._banner_slot.pack(fill="x")

        self._live_outer = ctk.CTkFrame(self._banner_slot, fg_color=("#d0f0d0", "#1b4a1b"), corner_radius=6)
        self._live_title = ctk.CTkLabel(
            self._live_outer,
            text="Game in Progress",
            font=ctk.CTkFont(weight="bold"),
        )
        self._live_title.pack(anchor="w", padx=10, pady=(6, 0))
        self._live_counts_label = ctk.CTkLabel(self._live_outer, text="", justify="left")
        self._live_counts_label.pack(anchor="w", padx=10, pady=(0, 6))

        self._list_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._list_outer.pack(fill="both", expand=True, padx=8, pady=(4, 0))

        self._list_frame = ctk.CTkScrollableFrame(self._list_outer, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True)

        self._empty_label = ctk.CTkLabel(
            self._list_frame, text="No games recorded yet.", text_color="gray"
        )

        self._detail_outer = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=6)
        ctk.CTkLabel(
            self._detail_outer, text="Game Details", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))

        self._detail_labels: dict[str, ctk.CTkLabel] = {}
        fields = [
            ("Game ID",              "gameId"),
            ("Match Date",           "matchDate"),
            ("Duration",             "gameDuration"),
            ("Result",               "result"),
            ("Race",                 "race"),
            ("Mineral Warnings",     "mineralWarningsCount"),
            ("Gas Warnings",         "gasWarningsCount"),
            ("Supply Warnings",      "supplyWarningsCount"),
            ("Idle Worker Warnings", "idleWorkersWarningsCount"),
        ]
        for label_text, key in fields:
            row = ctk.CTkFrame(self._detail_outer, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=label_text, width=180, anchor="w").pack(side="left")
            val = ctk.CTkLabel(row, text="—", anchor="w")
            val.pack(side="left", fill="x", expand=True)
            self._detail_labels[key] = val

        ctk.CTkButton(
            self._detail_outer, text="Close", width=70, command=self._hide_detail
        ).pack(anchor="e", padx=10, pady=6)

    def _refresh(self) -> None:
        self._records = self._loader.load_history()
        self._live_data = self._loader.load_live()
        self._render_live_banner()
        self._render_list()
        if self._selected_idx is not None:
            if self._selected_idx < len(self._records):
                self._show_detail(self._selected_idx)
            else:
                self._hide_detail()
        self.after(self.POLL_MS, self._refresh)

    def _render_live_banner(self) -> None:
        if self._live_data:
            gs = self._live_data.get("gameStats", {})
            counts = (
                f"Minerals: {gs.get('mineralWarningsCount', 0)}  "
                f"Gas: {gs.get('gasWarningsCount', 0)}  "
                f"Supply: {gs.get('supplyWarningsCount', 0)}  "
                f"Idle Workers: {gs.get('idleWorkersWarningsCount', 0)}"
            )
            updated = self._live_data.get("lastUpdated", "")
            self._live_counts_label.configure(text=f"{counts}\nLast updated: {updated}")
            self._live_outer.pack(fill="x", padx=8, pady=(6, 2))
        else:
            self._live_outer.pack_forget()

    def _render_list(self) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        if not self._records:
            self._empty_label = ctk.CTkLabel(
                self._list_frame, text="No games recorded yet.", text_color="gray"
            )
            self._empty_label.pack(pady=20)
            return

        for i, rec in enumerate(reversed(self._records)):
            idx = len(self._records) - 1 - i
            result = rec.get("result", "Unknown")
            light_color, dark_color = self._RESULT_COLORS.get(result, self._RESULT_COLORS["Unknown"])

            row = ctk.CTkFrame(self._list_frame, fg_color=("gray88", "gray18"), corner_radius=4)
            row.pack(fill="x", padx=4, pady=2)

            ctk.CTkLabel(row, text=rec.get("gameId", "—"), anchor="w", width=180).pack(
                side="left", padx=(8, 4), pady=6
            )
            ctk.CTkLabel(
                row, text=result, anchor="w", width=60,
                text_color=(light_color, dark_color),
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="left", padx=4, pady=6)
            ctk.CTkLabel(row, text=rec.get("race", "—"), anchor="w", width=70).pack(
                side="left", padx=4, pady=6
            )
            ctk.CTkLabel(row, text=rec.get("gameDuration", "—"), anchor="w", width=60).pack(
                side="left", padx=4, pady=6
            )
            ctk.CTkLabel(row, text=rec.get("matchDate", "—"), anchor="w", width=160).pack(
                side="left", padx=4, pady=6
            )
            ctk.CTkButton(
                row, text="Details", width=70,
                command=lambda n=idx: self._show_detail(n),
            ).pack(side="right", padx=8, pady=4)

    def _show_detail(self, idx: int) -> None:
        self._selected_idx = idx
        rec = self._records[idx]
        gs = rec.get("gameStats", {})
        values = {
            "gameId":                   rec.get("gameId", "—"),
            "matchDate":                rec.get("matchDate", "—"),
            "gameDuration":             rec.get("gameDuration", "—"),
            "result":                   rec.get("result", "—"),
            "race":                     rec.get("race", "—"),
            "mineralWarningsCount":     str(gs.get("mineralWarningsCount", 0)),
            "gasWarningsCount":         str(gs.get("gasWarningsCount", 0)),
            "supplyWarningsCount":      str(gs.get("supplyWarningsCount", 0)),
            "idleWorkersWarningsCount": str(gs.get("idleWorkersWarningsCount", 0)),
        }
        for key, lbl in self._detail_labels.items():
            lbl.configure(text=values.get(key, "—"))
        self._detail_outer.pack(fill="x", padx=8, pady=(4, 8))

    def _hide_detail(self) -> None:
        self._selected_idx = None
        self._detail_outer.pack_forget()
