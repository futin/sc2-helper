import random

SUPPLY_MESSAGES = [
    "Supply blocked incoming! Build something or cry later.",
    "You're capped. Your army is waiting. Are you waiting too?",
    "Supply is full. Your units are unionizing outside the barracks.",
    "No more room! Did you forget depots are a thing?",
    "Supply cap hit. Congratulations, you've built a very cozy base.",
    "Your production is on strike. Build more supply. Now.",
    "Almost capped. This is not a drill. Build. Depots. Now.",
    "Supply critical. Your opponent is laughing. Don't let them.",
    "Capped again? Incredible. Truly a signature move.",
    "Max supply approaching. Overlords don't build themselves. Actually they do. Use them.",
]

MINERAL_MESSAGES = [
    "Minerals piling up. Spend them. They're not a savings account.",
    "You have enough minerals to build a small moon. Please don't.",
    "Your bank account is full. Your army is not. Fix that.",
    "Stop hoarding. This isn't Minecraft.",
    "Minerals overflowing. Your economy weeps for efficiency.",
    "Rich and doing nothing. Very impressive. Very bad.",
    "That's a lot of blue crystals just sitting there judging you.",
    "Spend the minerals. Your workers mined them for a reason.",
    "Mineral surplus detected. Your macro just rolled its eyes.",
    "You're swimming in minerals. Build something before you drown.",
]

IDLE_WORKER_MESSAGES = [
    "Workers on vacation. Unpaid. Fix this immediately.",
    "Idle workers detected. They are deeply disappointed in you.",
    "Your workers are standing around like lost tourists. Send them somewhere.",
    "Those workers didn't sign up to watch the game. Put them to work.",
    "Idle workers! They have families to feed. Metaphorically.",
    "Workers sitting idle. This is the macro crime of the century.",
    "Your probes are having an existential crisis. Give them purpose.",
    "Lazy workers alert. They didn't choose this life. You did.",
    "Idle SCVs detected. They built this base and now you ignore them?",
    "Workers sleeping on the job. You're paying for this.",
]

GAS_MESSAGES = [
    "Gas overflowing. Build something gassy. Like a roach warren.",
    "Too much gas. Are you even teching? What is the plan here?",
    "Gas surplus. Your vespene geysers are personally offended.",
    "Drowning in gas. Either you're turtling or you forgot tech exists.",
    "Gas piling up. Your refineries are working harder than your brain.",
    "That's a lot of gas. Your units are still not upgraded. Interesting.",
    "Gas capped. Spend it or explain yourself to your future self.",
    "Vespene everywhere and nothing to show for it. Classic.",
    "Gas overload. The geysers are giving you everything. Give something back.",
    "Too much gas detected. Somewhere a Hydralisk is crying.",
]


def get_message(category: str, value: int = 0) -> str:
    messages = {
        "supply": SUPPLY_MESSAGES,
        "minerals": MINERAL_MESSAGES,
        "idle_workers": IDLE_WORKER_MESSAGES,
        "gas": GAS_MESSAGES,
    }
    return random.choice(messages[category])
