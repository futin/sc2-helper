from typing import Optional

from backend.classes import CooldownTracker, SpeechQueue
from backend.constants import PRIORITY_VOICE_RESPONSE


def handle_command(
    cmd,
    state: Optional[dict],
    speech: SpeechQueue,
    voice: str,
    config: dict,
    cooldown: CooldownTracker,
) -> None:
    if cmd.intent == "query_supply":
        if state:
            used = state.get("supply_used", "?")
            max_ = state.get("supply_max", "?")
            speech.speak(f"Supply is {used} of {max_}.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "query_resources":
        if state:
            minerals = state.get("minerals", "?")
            gas = state.get("gas", "?")
            speech.speak(f"You have {minerals} minerals and {gas} gas.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "query_workers":
        if state:
            idle_workers = state.get("idle_workers", "?")
            speech.speak(f"You have {idle_workers} idle workers.", voice, PRIORITY_VOICE_RESPONSE)
        else:
            speech.speak("No game active.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "silence":
        seconds = cmd.params["seconds"]
        mins = seconds // 60
        speech.speak(f"Going silent for {mins} minute{'s' if mins != 1 else ''}.", voice, PRIORITY_VOICE_RESPONSE)
    elif cmd.intent == "unmute":
        speech.speak("Sound enabled.", voice, PRIORITY_VOICE_RESPONSE)
