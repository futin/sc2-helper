from dataclasses import dataclass


@dataclass(frozen=True)
class HudElement:
    key: str
    label: str
    default_size: tuple[int, int]  # (width, height) for OCR capture region


HUD_ELEMENTS: list[HudElement] = [
    HudElement("minerals",     "Minerals",     (80, 30)),
    HudElement("gas",          "Gas",          (80, 30)),
    HudElement("supply",       "Supply",       (100, 30)),
    HudElement("idle_workers", "Idle Workers", (60, 25)),
]

HUD_ELEMENT_KEYS: list[str] = [e.key for e in HUD_ELEMENTS]
