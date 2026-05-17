import tkinter as tk
import customtkinter as ctk

from backend.hud_elements import HUD_ELEMENTS


class MessagesTab(ctk.CTkFrame):
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
