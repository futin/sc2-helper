# Message Modes

| Mode | Behaviour |
|------|-----------|
| `strict` | Short, direct: "Check supply." |
| `funny` | Random snarky message from a built-in bank |
| `custom` | Your own messages from `config.yaml → custom_messages`, falls back to strict |

Custom messages are configured per category (`supply`, `minerals`, `gas`, `idle_workers`) as a list of strings. The GUI **Messages** tab exposes this when `custom` mode is selected.
