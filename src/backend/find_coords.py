"""
Move mouse over each SC2 HUD element. Press Enter in terminal to record position.
Run: python3 -m backend.find_coords
"""


def get_mouse_pos() -> tuple[int, int]:
    from Quartz import CGEventCreate, CGEventGetLocation
    event = CGEventCreate(None)
    pos = CGEventGetLocation(event)
    return int(pos.x), int(pos.y)


if __name__ == "__main__":
    from backend.hud_elements import HUD_ELEMENTS

    positions: list[tuple[int, int]] = []
    print("Move mouse to the TOP-LEFT of each HUD number, then press Enter.")
    print("Tip: aim for the leftmost pixel of the number text.\n")

    for e in HUD_ELEMENTS:
        input(f"  Hover over {e.label} (top-left corner), then press Enter...")
        x, y = get_mouse_pos()
        positions.append((x, y))
        print(f"    -> recorded: x={x}, y={y}\n")

    print("\nPaste these into config.yaml (adjust width/height as needed):")
    for e, (x, y) in zip(HUD_ELEMENTS, positions):
        w, h = e.default_size
        print(f"  {e.key}: [{x}, {y}, {w}, {h}]")
