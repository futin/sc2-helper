import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable

from backend.hud_elements import HUD_ELEMENTS


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

        self._config_tab = _ConfigTab(self._tabview.tab("Configuration"), self._cfg)
        self._config_tab.pack(fill="both", expand=True)

        self._messages_tab = _MessagesTab(self._tabview.tab("Messages"), self._cfg)
        self._messages_tab.pack(fill="both", expand=True)

        self._coords_tab = _CoordsTab(self._tabview.tab("Coords Selection"), self._cfg)
        self._coords_tab.pack(fill="both", expand=True)

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


# ---------------------------------------------------------------------------
# Tab 1 — Configuration
# ---------------------------------------------------------------------------

class _ConfigTab(ctk.CTkScrollableFrame):
    def __init__(self, parent, cfg: dict):
        super().__init__(parent)
        self._cfg = cfg
        self._tier_rows: list[dict] = []
        self._build()

    def _lbl(self, text: str, row: int, col: int, **kw) -> None:
        ctk.CTkLabel(self, text=text).grid(row=row, column=col, sticky="w", padx=6, pady=3, **kw)

    def _entry(self, row: int, col: int, width: int = 120) -> ctk.CTkEntry:
        e = ctk.CTkEntry(self, width=width)
        e.grid(row=row, column=col, sticky="w", padx=6, pady=3)
        return e

    def _section_header(self, text: str, row: int) -> int:
        ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=(10, 2))
        return row + 1

    def _spacer(self, row: int) -> int:
        ctk.CTkLabel(self, text="").grid(row=row, column=0)
        return row + 1

    def _build(self) -> None:
        row = 0
        row = self._build_general_section(row)
        row = self._build_resources_section(row)
        row = self._build_supply_section(row)
        row = self._build_workers_section(row)
        self._build_screen_capture_section(row)

    def _build_general_section(self, row: int) -> int:
        row = self._section_header("General", row)

        self._lbl("Poll Interval (s)", row, 0)
        self._poll_interval = self._entry(row, 1)
        self._poll_interval.insert(0, str(self._cfg.get("poll_interval", 2.5)))
        row += 1

        self._lbl("TTS Voice", row, 0)
        self._tts_voice = self._entry(row, 1)
        self._tts_voice.insert(0, self._cfg.get("tts_voice", "Moira"))
        row += 1

        return self._spacer(row)

    def _build_resources_section(self, row: int) -> int:
        row = self._section_header("Resources", row)
        res = self._cfg.get("resources", {})

        self._lbl("Mineral Threshold", row, 0)
        self._mineral_threshold = self._entry(row, 1)
        self._mineral_threshold.insert(0, str(res.get("mineral_threshold", 600)))
        row += 1

        self._lbl("Gas Threshold", row, 0)
        self._gas_threshold = self._entry(row, 1)
        self._gas_threshold.insert(0, str(res.get("gas_threshold", 600)))
        row += 1

        self._lbl("Resources Cooldown (s)", row, 0)
        self._res_cooldown = self._entry(row, 1)
        self._res_cooldown.insert(0, str(res.get("cooldown", 30)))
        row += 1

        return self._spacer(row)

    def _build_supply_section(self, row: int) -> int:
        row = self._section_header("Supply", row)
        sup = self._cfg.get("supply", {})

        self._lbl("Supply Cooldown (s)", row, 0)
        self._supply_cooldown = self._entry(row, 1)
        self._supply_cooldown.insert(0, str(sup.get("cooldown", 10)))
        row += 1

        self._lbl("Supply Tiers", row, 0)
        row += 1

        self._tiers_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._tiers_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=6)
        row += 1

        header = ctk.CTkFrame(self._tiers_frame, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Max Cap", width=80).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="Gap", width=60).pack(side="left", padx=4)

        self._tier_list_frame = ctk.CTkFrame(self._tiers_frame, fg_color="transparent")
        self._tier_list_frame.pack(fill="x")

        for tier in sup.get("tiers", []):
            self._add_tier_row(tier.get("max_cap", 200), tier.get("gap", 10))

        ctk.CTkButton(self._tiers_frame, text="+ Add Tier", command=self._add_tier_row, width=100).pack(
            anchor="w", pady=4)

        return self._spacer(row)

    def _build_workers_section(self, row: int) -> int:
        row = self._section_header("Workers", row)
        wrk = self._cfg.get("workers", {})

        self._lbl("Idle Seconds", row, 0)
        self._idle_seconds = self._entry(row, 1)
        self._idle_seconds.insert(0, str(wrk.get("idle_seconds", 10)))
        row += 1

        self._lbl("Workers Cooldown (s)", row, 0)
        self._workers_cooldown = self._entry(row, 1)
        self._workers_cooldown.insert(0, str(wrk.get("cooldown", 30)))
        row += 1

        return self._spacer(row)

    def _build_screen_capture_section(self, row: int) -> int:
        row = self._section_header("Screen Capture", row)
        sc = self._cfg.get("screen_capture", {})

        self._lbl("OCR Threshold", row, 0)
        self._ocr_threshold = self._entry(row, 1)
        self._ocr_threshold.insert(0, str(sc.get("ocr_threshold", 100)))
        row += 1

        return row

    def _add_tier_row(self, max_cap: int = 200, gap: int = 10) -> None:
        row_frame = ctk.CTkFrame(self._tier_list_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        mc = ctk.CTkEntry(row_frame, width=80)
        mc.insert(0, str(max_cap))
        mc.pack(side="left", padx=4)

        g = ctk.CTkEntry(row_frame, width=60)
        g.insert(0, str(gap))
        g.pack(side="left", padx=4)

        row_data = {"frame": row_frame, "max_cap": mc, "gap": g}
        self._tier_rows.append(row_data)

        ctk.CTkButton(
            row_frame, text="Remove", width=70,
            command=lambda rd=row_data: self._remove_tier_row(rd),
        ).pack(side="left", padx=4)

    def _remove_tier_row(self, row_data: dict) -> None:
        row_data["frame"].destroy()
        self._tier_rows = [r for r in self._tier_rows if r is not row_data]

    def collect(self) -> dict:
        try:
            poll = float(self._poll_interval.get())
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
            "tts_voice": self._tts_voice.get().strip(),
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

class _MessagesTab(ctk.CTkFrame):
    def __init__(self, parent, cfg: dict):
        super().__init__(parent, fg_color="transparent")
        self._cfg = cfg
        self._build()

    def _build(self) -> None:
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(mode_frame, text="Message Mode", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=8, pady=(6, 2))

        self._mode_var = tk.StringVar(value=self._cfg.get("message_mode", "strict"))
        self._mode_var.trace_add("write", self._on_mode_change)

        btn_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(0, 6))
        for mode in ("strict", "funny", "custom"):
            ctk.CTkRadioButton(
                btn_row, text=mode.capitalize(),
                variable=self._mode_var, value=mode,
            ).pack(side="left", padx=12)

        self._custom_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self._custom_frame, text="Custom Messages (one per line)", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=8, pady=(6, 2))

        self._text_widgets: dict[str, ctk.CTkTextbox] = {}
        custom = self._cfg.get("custom_messages", {})
        for e in HUD_ELEMENTS:
            row = ctk.CTkFrame(self._custom_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(row, text=e.label, width=100, anchor="w").pack(side="left")
            txt = ctk.CTkTextbox(row, height=60, wrap="word")
            txt.pack(side="left", fill="x", expand=True)
            msgs = custom.get(e.key, [])
            if msgs:
                txt.insert("1.0", "\n".join(msgs))
            self._text_widgets[e.key] = txt

        self._on_mode_change()

    def _on_mode_change(self, *_) -> None:
        if self._mode_var.get() == "custom":
            self._custom_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        else:
            self._custom_frame.pack_forget()

    def collect(self) -> dict:
        mode = self._mode_var.get()
        custom: dict[str, list[str]] = {}
        for key, txt in self._text_widgets.items():
            raw = txt.get("1.0", "end-1c")
            custom[key] = [line for line in raw.splitlines() if line.strip()]
        return {"message_mode": mode, "custom_messages": custom}


# ---------------------------------------------------------------------------
# Tab 3 — Coords Selection
# ---------------------------------------------------------------------------

class _CoordsTab(ctk.CTkScrollableFrame):
    def __init__(self, parent, cfg: dict):
        super().__init__(parent)
        self._cfg = cfg
        self._recorded: dict[str, tuple[int, int]] = {}
        self._coord_display: dict[str, ctk.CTkLabel] = {}
        self._capture_btns: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Click Capture, then move your mouse to the HUD element within 3 seconds.",
            wraplength=480,
        ).pack(padx=12, pady=(12, 6), anchor="w")

        sc = self._cfg.get("screen_capture", {})
        for e in HUD_ELEMENTS:
            existing = sc.get(e.key, [0, 0, 0, 0])
            x, y = existing[0], existing[1]
            self._recorded[e.key] = (x, y)

            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", padx=12, pady=4)

            ctk.CTkLabel(frame, text=e.label, font=ctk.CTkFont(weight="bold"), width=100).pack(side="left", padx=8, pady=6)

            btn = ctk.CTkButton(
                frame,
                text="Capture",
                width=80,
                command=lambda n=e.key: self._capture(n),
            )
            btn.pack(side="left", padx=4, pady=6)
            self._capture_btns[e.key] = btn

            lbl = ctk.CTkLabel(frame, text=f"x={x}, y={y}")
            lbl.pack(side="left", padx=8)
            self._coord_display[e.key] = lbl

        ctk.CTkButton(self, text="Save Coords to Config", command=self._save_coords).pack(
            anchor="e", padx=12, pady=(8, 12))

    def _capture(self, name: str) -> None:
        btn = self._capture_btns[name]
        self._countdown(name, btn, 3)

    def _countdown(self, name: str, btn: ctk.CTkButton, remaining: int) -> None:
        if remaining > 0:
            btn.configure(text=f"{remaining}…", state="disabled")
            self.after(1000, lambda: self._countdown(name, btn, remaining - 1))
        else:
            btn.configure(text="Capture", state="normal")
            try:
                from backend.find_coords import get_mouse_pos
                x, y = get_mouse_pos()
            except Exception as e:
                messagebox.showerror("Capture Error", f"Could not read mouse position:\n{e}")
                return
            self._recorded[name] = (x, y)
            self._coord_display[name].configure(text=f"x={x}, y={y}")

    def _save_coords(self) -> None:
        sc = dict(self._cfg.get("screen_capture", {}))
        for e in HUD_ELEMENTS:
            x, y = self._recorded[e.key]
            sc[e.key] = [x, y, *e.default_size]
        cfg = dict(self._cfg)
        cfg["screen_capture"] = sc

        from frontend.config_manager import save_config
        save_config(cfg)
        self._cfg = cfg
        messagebox.showinfo("Saved", "Coordinates saved to config.yaml")

    def refresh(self, cfg: dict) -> None:
        self._cfg = cfg
        sc = cfg.get("screen_capture", {})
        for e in HUD_ELEMENTS:
            existing = sc.get(e.key, [0, 0, 0, 0])
            x, y = existing[0], existing[1]
            self._recorded[e.key] = (x, y)
            self._coord_display[e.key].configure(text=f"x={x}, y={y}")
