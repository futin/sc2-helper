SC2_BASE = "http://localhost:6119"
REQUEST_TIMEOUT = 1  # seconds

PRIORITY_VOICE_RESPONSE = 0
PRIORITY_SUPPLY = 1
PRIORITY_MINERALS = 2
PRIORITY_IDLE_WORKERS = 3
PRIORITY_GAS = 4

_RESULT_MAP = {
    "Win": "Win", "Victory": "Win",
    "Loss": "Loss", "Defeat": "Loss",
    "Tie": "Tie",
}

_RACE_MAP = {
    "Prot": "Protoss", "Protoss": "Protoss",
    "Terr": "Terran",  "Terran": "Terran",
    "Zerg": "Zerg",
    "random": "Random", "Random": "Random",
}
