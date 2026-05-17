SC2_BASE = "http://localhost:6119"
REQUEST_TIMEOUT = 1  # seconds

PRIORITY_SUPPLY = 0
PRIORITY_MINERALS = 1
PRIORITY_IDLE_WORKERS = 2
PRIORITY_GAS = 3

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
