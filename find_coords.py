"""
Move mouse over each SC2 HUD element. Press Enter in terminal to record position.
Run: python3 find_coords.py
"""
import subprocess


def get_mouse_pos():
    from Quartz import CGEventCreate, CGEventGetLocation
    event = CGEventCreate(None)
    pos = CGEventGetLocation(event)
    return int(pos.x), int(pos.y)


labels = ["minerals (top-left corner)", "gas (top-left corner)", "supply (top-left corner)", "idle_workers (top-left corner)"]
positions = []

print("Move mouse to the TOP-LEFT of each HUD number, then press Enter.")
print("Tip: aim for the leftmost pixel of the number text.\n")

for label in labels:
    input(f"  Hover over {label}, then press Enter...")
    x, y = get_mouse_pos()
    positions.append((x, y))
    print(f"    -> recorded: x={x}, y={y}\n")

print("\nPaste these into config.yaml (adjust width/height as needed):")
print(f"  minerals:     [{positions[0][0]}, {positions[0][1]}, 80, 30]")
print(f"  gas:          [{positions[1][0]}, {positions[1][1]}, 80, 30]")
print(f"  supply:       [{positions[2][0]}, {positions[2][1]}, 100, 30]")
print(f"  idle_workers: [{positions[3][0]}, {positions[3][1]}, 60, 30]")
