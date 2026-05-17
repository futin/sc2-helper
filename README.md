# SC2 Helper

Real-time StarCraft II assistant. Monitors your HUD via screen OCR and fires spoken warnings when you're floating resources, getting supply-capped, or leaving workers idle.

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
