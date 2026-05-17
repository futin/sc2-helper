import customtkinter as ctk

from frontend.logic.stats_logic import StatsLoader


class StatsTab(ctk.CTkFrame):
    _RESULT_COLORS = {
        "Win":     ("#1a7a1a", "#4caf50"),
        "Loss":    ("#a01010", "#ef5350"),
        "Tie":     ("#7a6a00", "#ffc107"),
        "Unknown": ("#555555", "#aaaaaa"),
    }

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._loader = StatsLoader()
        self._selected_idx: int | None = None
        self._build()
        self._render_list()

    def _build(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._list_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._list_outer.grid(row=0, column=0, sticky="nsew", padx=8, pady=(4, 0))
        self._list_outer.grid_rowconfigure(0, weight=1)
        self._list_outer.grid_columnconfigure(0, weight=1)

        self._list_frame = ctk.CTkScrollableFrame(self._list_outer, fg_color="transparent")
        self._list_frame.grid(row=0, column=0, sticky="nsew")

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

    def _render_list(self) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        records = self._loader.load_history()

        if not records:
            ctk.CTkLabel(
                self._list_frame, text="No games recorded yet.", text_color="gray"
            ).pack(pady=20)
            return

        for i, rec in enumerate(reversed(records)):
            idx = len(records) - 1 - i
            result = rec.get("result") or "Unknown"
            light_color, dark_color = self._RESULT_COLORS.get(result, self._RESULT_COLORS["Unknown"])

            row = ctk.CTkFrame(self._list_frame, fg_color=("gray88", "gray18"), corner_radius=4)
            row.pack(fill="x", padx=4, pady=2)

            ctk.CTkLabel(row, text=rec.get("gameId") or "—", anchor="w", width=180).pack(
                side="left", padx=(8, 4), pady=6
            )
            ctk.CTkLabel(
                row, text=result, anchor="w", width=60,
                text_color=(light_color, dark_color),
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="left", padx=4, pady=6)
            ctk.CTkLabel(row, text=rec.get("race") or "—", anchor="w", width=70).pack(
                side="left", padx=4, pady=6
            )
            ctk.CTkLabel(row, text=rec.get("gameDuration") or "—", anchor="w", width=60).pack(
                side="left", padx=4, pady=6
            )
            ctk.CTkLabel(row, text=rec.get("matchDate") or "—", anchor="w", width=160).pack(
                side="left", padx=4, pady=6
            )

            for widget in (row, *row.winfo_children()):
                widget.bind("<Button-1>", lambda e, n=idx: self._show_detail(n))

        self._list_frame._parent_canvas.yview_moveto(0)

    def _show_detail(self, idx: int) -> None:
        records = self._loader.load_history()
        if idx >= len(records):
            return
        self._selected_idx = idx
        rec = records[idx]
        gs = rec.get("gameStats", {})
        values = {
            "gameId":                   rec.get("gameId") or "—",
            "matchDate":                rec.get("matchDate") or "—",
            "gameDuration":             rec.get("gameDuration") or "—",
            "result":                   rec.get("result") or "—",
            "race":                     rec.get("race") or "—",
            "mineralWarningsCount":     str(gs.get("mineralWarningsCount", 0)),
            "gasWarningsCount":         str(gs.get("gasWarningsCount", 0)),
            "supplyWarningsCount":      str(gs.get("supplyWarningsCount", 0)),
            "idleWorkersWarningsCount": str(gs.get("idleWorkersWarningsCount", 0)),
        }
        for key, lbl in self._detail_labels.items():
            lbl.configure(text=values.get(key, "—"))
        self._detail_outer.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))

    def _hide_detail(self) -> None:
        self._selected_idx = None
        self._detail_outer.grid_forget()

    def refresh(self) -> None:
        self._hide_detail()
        self._render_list()
