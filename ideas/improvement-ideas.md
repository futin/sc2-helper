# SC2 Helper — Improvement Ideas

## 1. Banking Mode Toggle *(top priority — biggest pain point)*

Temporarily mutes mineral and gas warnings when consciously saving up (expansion, tech, etc.).

**Recommended approach: Timed silence + global hotkey**
- Global hotkey (e.g. `Cmd+B`) activates banking mode without alt-tabbing
- Silence duration is configurable (default 2 min)
- GUI runner screen shows "Banking mode — 1:34 remaining" indicator
- Auto-expires so player can't forget it's on

Alternative: persistent on/off toggle — simpler but risky to forget.

---

## 2. Smarter Contextual Detection

Context-aware suppression to reduce noise warnings:

- **Game-phase awareness** — Auto-suppress mineral/gas warnings below N supply (e.g. 40). Complements the manual banking toggle.
- **Post-fight cooldown** — Detect army loss (supply drop) and suppress idle-worker warnings for ~30s after. Avoids noise during rebuild phase.
- **Worker saturation reward** — If idle workers stay at 0 for 60+ consecutive seconds, lower idle-worker warning threshold to 1. Reward streaks of good macro.

---

## 3. Post-Game Coaching Summary

After each game ends, synthesize warning history into a short debrief spoken via TTS or shown in History tab:

> "Game over. You floated minerals 4 times, got supply-capped twice, and had zero gas issues. Focus: minerals."

No new OCR needed — pure aggregation of existing `game_stats` data. Fires automatically at game end.

---

## 4. Per-Race Coaching Tips

Race-specific warnings using the already-parsed `race` field from SC2 API:

- **Zerg** — Larva inject reminder (supply gap closes at hatchery)
- **Terran** — MULE calldown reminder (separate macro mechanic, not currently tracked)
- **Protoss** — Chrono boost reminder (proxy: minerals high + mid-game supply)

Requires separate message banks per race routed through existing `get_message()` system.

---

## 5. OCR Health Indicator

Expose OCR reliability in the GUI runner screen (currently all failures are silent in logs):

- Green badge: last 10 reads all parsed successfully
- Yellow badge: >20% parse failures in recent window
- Red badge: OCR appears broken (likely wrong coordinates)

No new detection logic — surfaces what `game_api.py` already tracks internally.

---

## 6. Replay-Linked History

Store path to the most recent `.SC2Replay` file alongside each `game_stats` row in SQLite. SC2 writes replays to a known default directory. Add one-click "Open Replay" button in Game History tab.

---

## 7. Warning Intensity Scaling

Scale warning urgency based on how bad the situation is, instead of binary warn/no-warn:

| Minerals | Message tone |
|----------|-------------|
| 600      | Mild nudge  |
| 1000     | Urgent      |
| 1500+    | Alarm       |

Extends the tiered threshold system already used for supply to minerals and gas.

---

## Implementation Order (suggested)

1. **Banking Mode Toggle** — isolated, no core loop changes, immediate payoff
2. **OCR Health Indicator** — low effort, high visibility
3. **Post-Game Summary** — no new data needed, good UX win
4. **Warning Intensity Scaling** — extends existing threshold system cleanly
5. **Smarter Contextual Detection** — more complex, requires game-state inference
6. **Per-Race Coaching Tips** — requires new message banks
7. **Replay-Linked History** — file system integration, lower priority
