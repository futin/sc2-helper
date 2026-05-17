# SC2 Helper

Real-time StarCraft II assistant. Monitors your HUD via screen OCR and fires spoken warnings when you're floating resources, getting supply-capped, or leaving workers idle.

---

## Disclaimer

SC2 Helper is a **learning tool** designed to help players build awareness of resource management, supply, and worker activity. It is **not** a substitute for developing the habit of manually checking your HUD during games — the goal is to train that awareness, not replace it.

This tool reads your screen using OCR (Optical Character Recognition) and does not interact with or inject into the game process in any way. As a result, it has a very low probability of being flagged by anti-cheat mechanisms. That said, use it at your own discretion and in accordance with any applicable game policies.

### Using statistics to improve your gameplay

The **Statistics** tab tracks per-game warning counts (minerals, gas, supply, idle workers) across your match history. Use this data to identify your weakest habits over time — for example, consistently high idle-worker warnings point to a macro routine problem, while frequent supply warnings suggest build order practice. Review your history after sessions to spot patterns, set a target warning count to beat each week, and watch that number fall as the habits become natural.

---

## Docs

- [Architecture & How it works](docs/architecture.md)
- [Running & Requirements](docs/running.md)
- [Configuration](docs/configuration.md)
- [Statistics](docs/statistics.md)
- [Message Modes](docs/messages.md)

---

## Quick start

```bash
pip install -r requirements.txt
python src/frontend/sc2_ui.py
```

Open **Settings**, configure screen capture regions via the **Coords Selection** tab, then click **▶ Run Script → ▶ Start**.
