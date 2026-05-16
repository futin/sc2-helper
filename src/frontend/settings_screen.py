import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from config_manager import load_config

COORD_WIDTHS = {
    "minerals":     (80, 30),
    "gas":          (80, 30),
    "supply":       (100, 30),
    "idle_workers": (60, 25),
}

COORD_LABELS = {
    "minerals":     "Minerals",
    "gas":          "Gas",
    "supply":       "Supply",
    "idle_workers": "Idle Workers",
}

CATEGORIES = ["supply", "minerals", "gas", "idle_workers"]
CATEGORY_LABELS = {
    "supply":       "Supply",
    "minerals":     "Minerals",
    "gas":          "Gas",
    "idle_workers": "Idle Workers",
}


class SettingsScreen(ttk.Frame):
    def __init__(self, parent: tk.Widget, cfg: dict, on_save: Callable[[dict], None]):
        super().__init__(parent)
        self._cfg = cfg
        self._on_save = on_save
        self._build()

    def _build(self) -> None:
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._config_tab = _ConfigTab(self._notebook, self._cfg)
        self._messages_tab = _MessagesTab(self._notebook, self._cfg)
        self._coords_tab = _CoordsTab(self._notebook, self._cfg)

        self._notebook.add(self._config_tab, text="Configuration")
        self._notebook.add(self._messages_tab, text="Messages")
        self._notebook.add(self._coords_tab, text="Coords Selection")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(btn_frame, text="Save All", command=self._save).pack(side="right")

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


# ---------------------------------------------------------------------------
# Tab 1 — Configuration
# ---------------------------------------------------------------------------

class _ConfigTab(ttk.Frame):
    def __init__(self, parent: tk.Widget, cfg: dict):
        super().__init__(parent)
        self._cfg = cfg
        self._tier_rows: list[dict] = []
        self._build()

    def _build(self) -> None:
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._inner = ttk.Frame(canvas)

        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        f = self._inner
        row = 0

        def lbl(text, r, c, **kw):
            ttk.Label(f, text=text).grid(row=r, column=c, sticky="w", padx=6, pady=3, **kw)

        def spinbox(r, c, **kw):
            sb = ttk.Spinbox(f, width=10, **kw)
            sb.grid(row=r, column=c, sticky="w", padx=6, pady=3)
            return sb

        # ---- General ----
        ttk.Label(f, text="General", font=("", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(10, 2))
        row += 1

        lbl("Poll Interval (s)", row, 0)
        self._poll_interval = spinbox(row, 1, from_=0.5, to=10.0, increment=0.5)
        self._poll_interval.set(cfg.get("poll_interval", 2.5))
        row += 1

        lbl("Player ID", row, 0)
        self._player_id = spinbox(row, 1, from_=1, to=8, increment=1)
        self._player_id.set(cfg.get("player_id", 1))
        row += 1

        lbl("TTS Voice", row, 0)
        self._tts_voice = ttk.Entry(f, width=14)
        self._tts_voice.insert(0, cfg.get("tts_voice", "Moira"))
        self._tts_voice.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        row += 1

        lbl("Message Mode", row, 0)
        self._message_mode = ttk.Combobox(f, values=["strict", "funny", "custom"], width=11, state="readonly")
        self._message_mode.set(cfg.get("message_mode", "strict"))
        self._message_mode.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        row += 1

        ttk.Separator(f, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        row += 1

        # ---- Resources ----
        ttk.Label(f, text="Resources", font=("", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))
        row += 1

        res = cfg.get("resources", {})
        lbl("Mineral Threshold", row, 0)
        self._mineral_threshold = spinbox(row, 1, from_=0, to=5000, increment=50)
        self._mineral_threshold.set(res.get("mineral_threshold", 600))
        row += 1

        lbl("Gas Threshold", row, 0)
        self._gas_threshold = spinbox(row, 1, from_=0, to=5000, increment=50)
        self._gas_threshold.set(res.get("gas_threshold", 600))
        row += 1

        lbl("Resources Cooldown (s)", row, 0)
        self._res_cooldown = spinbox(row, 1, from_=5, to=120, increment=5)
        self._res_cooldown.set(res.get("cooldown", 30))
        row += 1

        ttk.Separator(f, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        row += 1

        # ---- Supply ----
        ttk.Label(f, text="Supply", font=("", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))
        row += 1

        sup = cfg.get("supply", {})
        lbl("Supply Cooldown (s)", row, 0)
        self._supply_cooldown = spinbox(row, 1, from_=5, to=120, increment=5)
        self._supply_cooldown.set(sup.get("cooldown", 10))
        row += 1

        lbl("Supply Tiers", row, 0)
        row += 1

        self._tiers_frame = ttk.Frame(f)
        self._tiers_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=6)
        row += 1

        header = ttk.Frame(self._tiers_frame)
        header.pack(fill="x")
        ttk.Label(header, text="Max Cap", width=10).pack(side="left", padx=4)
        ttk.Label(header, text="Gap", width=8).pack(side="left", padx=4)

        self._tier_list_frame = ttk.Frame(self._tiers_frame)
        self._tier_list_frame.pack(fill="x")

        for tier in sup.get("tiers", []):
            self._add_tier_row(tier.get("max_cap", 200), tier.get("gap", 10))

        ttk.Button(self._tiers_frame, text="+ Add Tier", command=self._add_tier_row).pack(
            anchor="w", pady=4)

        ttk.Separator(f, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        row += 1

        # ---- Workers ----
        ttk.Label(f, text="Workers", font=("", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))
        row += 1

        wrk = cfg.get("workers", {})
        lbl("Idle Seconds", row, 0)
        self._idle_seconds = spinbox(row, 1, from_=1, to=60, increment=1)
        self._idle_seconds.set(wrk.get("idle_seconds", 10))
        row += 1

        lbl("Workers Cooldown (s)", row, 0)
        self._workers_cooldown = spinbox(row, 1, from_=5, to=120, increment=5)
        self._workers_cooldown.set(wrk.get("cooldown", 30))
        row += 1

        ttk.Separator(f, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        row += 1

        # ---- Screen Capture ----
        ttk.Label(f, text="Screen Capture", font=("", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))
        row += 1

        sc = cfg.get("screen_capture", {})
        lbl("OCR Threshold", row, 0)
        self._ocr_threshold = spinbox(row, 1, from_=0, to=255, increment=5)
        self._ocr_threshold.set(sc.get("ocr_threshold", 100))
        row += 1

    def _add_tier_row(self, max_cap: int = 200, gap: int = 10) -> None:
        row_frame = ttk.Frame(self._tier_list_frame)
        row_frame.pack(fill="x", pady=2)

        mc = ttk.Spinbox(row_frame, from_=1, to=200, increment=1, width=9)
        mc.set(max_cap)
        mc.pack(side="left", padx=4)

        g = ttk.Spinbox(row_frame, from_=1, to=50, increment=1, width=7)
        g.set(gap)
        g.pack(side="left", padx=4)

        row_data = {"frame": row_frame, "max_cap": mc, "gap": g}
        self._tier_rows.append(row_data)

        ttk.Button(
            row_frame, text="Remove",
            command=lambda rd=row_data: self._remove_tier_row(rd),
        ).pack(side="left", padx=4)

    def _remove_tier_row(self, row_data: dict) -> None:
        row_data["frame"].destroy()
        self._tier_rows = [r for r in self._tier_rows if r is not row_data]

    def collect(self) -> dict:
        try:
            poll = float(self._poll_interval.get())
            player = int(self._player_id.get())
            m_thresh = int(self._mineral_threshold.get())
            g_thresh = int(self._gas_threshold.get())
            r_cool = int(self._res_cooldown.get())
            s_cool = int(self._supply_cooldown.get())
            idle_s = int(self._idle_seconds.get())
            w_cool = int(self._workers_cooldown.get())
            ocr_t = int(self._ocr_threshold.get())
        except ValueError as e:
            raise ValueError(f"Invalid number: {e}") from e

        tiers = []
        for r in self._tier_rows:
            try:
                tiers.append({
                    "max_cap": int(r["max_cap"].get()),
                    "gap": int(r["gap"].get()),
                })
            except ValueError as e:
                raise ValueError(f"Invalid tier value: {e}") from e
        tiers.sort(key=lambda t: t["max_cap"])

        sc = dict(self._cfg.get("screen_capture", {}))
        sc["ocr_threshold"] = ocr_t

        return {
            "poll_interval": poll,
            "player_id": player,
            "tts_voice": self._tts_voice.get().strip(),
            "message_mode": self._message_mode.get(),
            "resources": {
                "mineral_threshold": m_thresh,
                "gas_threshold": g_thresh,
                "cooldown": r_cool,
            },
            "supply": {"cooldown": s_cool, "tiers": tiers},
            "workers": {"idle_seconds": idle_s, "cooldown": w_cool},
            "screen_capture": sc,
        }


# ---------------------------------------------------------------------------
# Tab 2 — Messages
# ---------------------------------------------------------------------------

class _MessagesTab(ttk.Frame):
    def __init__(self, parent: tk.Widget, cfg: dict):
        super().__init__(parent)
        self._cfg = cfg
        self._build()

    def _build(self) -> None:
        mode_frame = ttk.LabelFrame(self, text="Message Mode")
        mode_frame.pack(fill="x", padx=12, pady=12)

        self._mode_var = tk.StringVar(value=self._cfg.get("message_mode", "strict"))
        self._mode_var.trace_add("write", self._on_mode_change)

        for mode in ("strict", "funny", "custom"):
            ttk.Radiobutton(
                mode_frame, text=mode.capitalize(),
                variable=self._mode_var, value=mode,
            ).pack(side="left", padx=12, pady=8)

        self._custom_frame = ttk.LabelFrame(self, text="Custom Messages (one per line)")
        self._text_widgets: dict[str, tk.Text] = {}

        custom = self._cfg.get("custom_messages", {})
        for cat in CATEGORIES:
            row = ttk.Frame(self._custom_frame)
            row.pack(fill="x", padx=8, pady=4)
            ttk.Label(row, text=CATEGORY_LABELS[cat], width=14, anchor="w").pack(side="left")
            txt = tk.Text(row, height=3, width=50, wrap="word")
            txt.pack(side="left", fill="x", expand=True)
            msgs = custom.get(cat, [])
            if msgs:
                txt.insert("1.0", "\n".join(msgs))
            self._text_widgets[cat] = txt
            sb = ttk.Scrollbar(row, command=txt.yview)
            sb.pack(side="left", fill="y")
            txt.configure(yscrollcommand=sb.set)

        self._on_mode_change()

    def _on_mode_change(self, *_) -> None:
        if self._mode_var.get() == "custom":
            self._custom_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        else:
            self._custom_frame.pack_forget()

    def collect(self) -> dict:
        mode = self._mode_var.get()
        custom: dict[str, list[str]] = {}
        for cat, txt in self._text_widgets.items():
            raw = txt.get("1.0", "end-1c")
            custom[cat] = [line for line in raw.splitlines() if line.strip()]
        return {"message_mode": mode, "custom_messages": custom}


# ---------------------------------------------------------------------------
# Tab 3 — Coords Selection
# ---------------------------------------------------------------------------

class _CoordsTab(ttk.Frame):
    def __init__(self, parent: tk.Widget, cfg: dict):
        super().__init__(parent)
        self._cfg = cfg
        self._recorded: dict[str, tuple[int, int]] = {}
        self._coord_display: dict[str, ttk.Label] = {}
        self._build()

    def _build(self) -> None:
        ttk.Label(
            self,
            text="Move your mouse to the top-left corner of each HUD element, then click Capture.",
            wraplength=480,
        ).pack(padx=12, pady=(12, 6), anchor="w")

        sc = self._cfg.get("screen_capture", {})

        for name in COORD_LABELS:
            existing = sc.get(name, [0, 0, 0, 0])
            x, y = existing[0], existing[1]
            self._recorded[name] = (x, y)

            frame = ttk.LabelFrame(self, text=COORD_LABELS[name])
            frame.pack(fill="x", padx=12, pady=4)

            ttk.Button(
                frame,
                text=f"Capture {COORD_LABELS[name]}",
                command=lambda n=name: self._capture(n),
            ).pack(side="left", padx=8, pady=6)

            lbl = ttk.Label(frame, text=f"x={x}, y={y}", foreground="#555")
            lbl.pack(side="left", padx=8)
            self._coord_display[name] = lbl

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=12, pady=8)

        ttk.Button(self, text="Save Coords to Config", command=self._save_coords).pack(
            anchor="e", padx=12, pady=(0, 12))

    def _capture(self, name: str) -> None:
        try:
            from find_coords import get_mouse_pos
            x, y = get_mouse_pos()
        except Exception as e:
            messagebox.showerror("Capture Error", f"Could not read mouse position:\n{e}")
            return
        self._recorded[name] = (x, y)
        self._coord_display[name].config(text=f"x={x}, y={y}", foreground="#007700")

    def _save_coords(self) -> None:
        sc = dict(self._cfg.get("screen_capture", {}))
        for name, (x, y) in self._recorded.items():
            w, h = COORD_WIDTHS[name]
            sc[name] = [x, y, w, h]
        cfg = dict(self._cfg)
        cfg["screen_capture"] = sc

        from config_manager import save_config
        save_config(cfg)
        self._cfg = cfg
        messagebox.showinfo("Saved", "Coordinates saved to config.yaml")

    def refresh(self, cfg: dict) -> None:
        self._cfg = cfg
        sc = cfg.get("screen_capture", {})
        for name in COORD_LABELS:
            existing = sc.get(name, [0, 0, 0, 0])
            x, y = existing[0], existing[1]
            self._recorded[name] = (x, y)
            self._coord_display[name].config(text=f"x={x}, y={y}", foreground="#555")
