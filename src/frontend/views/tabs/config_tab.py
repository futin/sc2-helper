import customtkinter as ctk


class ConfigTab(ctk.CTkScrollableFrame):
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
        row = self._build_voice_section(row)
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

    def _build_voice_section(self, row: int) -> int:
        row = self._section_header("Voice Control", row)
        vc = self._cfg.get("voice_control", {})

        self._lbl("Enable Voice Control", row, 0)
        self._voice_enabled_var = ctk.BooleanVar(value=vc.get("enabled", False))
        ctk.CTkCheckBox(self, text="", variable=self._voice_enabled_var).grid(
            row=row, column=1, sticky="w", padx=6, pady=3)
        row += 1

        self._lbl("Wake Word Model", row, 0)
        self._voice_wake_word_model = self._entry(row, 1)
        self._voice_wake_word_model.insert(0, vc.get("wake_word_model", "alexa"))
        row += 1

        self._lbl("Wake Sensitivity (0.0–1.0)", row, 0)
        self._voice_wake_sensitivity = self._entry(row, 1)
        self._voice_wake_sensitivity.insert(0, str(vc.get("wake_sensitivity", 0.6)))
        row += 1

        self._lbl("STT Backend", row, 0)
        self._voice_stt_backend = ctk.CTkOptionMenu(self, values=["google", "whisper"], width=120)
        self._voice_stt_backend.set(vc.get("stt_backend", "google"))
        self._voice_stt_backend.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        row += 1

        self._lbl("Silence Duration (s)", row, 0)
        self._voice_silence_duration = self._entry(row, 1)
        self._voice_silence_duration.insert(0, str(vc.get("silence_duration", 120)))
        row += 1

        self._lbl("Pause Threshold (s)", row, 0)
        self._voice_pause_threshold = self._entry(row, 1)
        self._voice_pause_threshold.insert(0, str(vc.get("pause_threshold", 1.2)))
        row += 1

        self._lbl("Phrase Time Limit (s)", row, 0)
        self._voice_phrase_time_limit = self._entry(row, 1)
        self._voice_phrase_time_limit.insert(0, str(vc.get("phrase_time_limit", 8)))
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
            silence_dur = int(self._voice_silence_duration.get())
            pause_thr = float(self._voice_pause_threshold.get())
            wake_sensitivity = float(self._voice_wake_sensitivity.get())
            phrase_limit = int(self._voice_phrase_time_limit.get())
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
            "voice_control": {
                "enabled": self._voice_enabled_var.get(),
                "wake_word_model": self._voice_wake_word_model.get().strip().lower(),
                "wake_sensitivity": wake_sensitivity,
                "stt_backend": self._voice_stt_backend.get(),
                "silence_duration": silence_dur,
                "pause_threshold": pause_thr,
                "phrase_time_limit": phrase_limit,
            },
        }
