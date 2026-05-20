import customtkinter as ctk
from tkinter import messagebox

from backend.hud import HUD_ELEMENTS


class CoordsTab(ctk.CTkScrollableFrame):
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
        messagebox.showinfo("Saved", "Coordinates saved.")

    def refresh(self, cfg: dict) -> None:
        self._cfg = cfg
        sc = cfg.get("screen_capture", {})
        for e in HUD_ELEMENTS:
            existing = sc.get(e.key, [0, 0, 0, 0])
            x, y = existing[0], existing[1]
            self._recorded[e.key] = (x, y)
            self._coord_display[e.key].configure(text=f"x={x}, y={y}")
