import random
from typing import List, Dict

# Style-specific move sets
STYLE_MOVES = {
    "powerhouse": [
        "Powerbomb", "Spear", "Chokeslam", "Military Press Slam", "Bearhug", 
        "Running Powerslam", "Spinebuster", "Clothesline from Hell", "Big Boot"
    ],
    "technician": [
        "German Suplex", "Northern Lights Suplex", "Armbar", "Kneebar", "Snap Suplex", 
        "Dragon Screw", "European Uppercut", "Wristlock", "Single Leg Crab"
    ],
    "high_flyer": [
        "Moonsault", "450 Splash", "Hurricanrana", "Springboard Dropkick", "Shooting Star Press", 
        "Suicide Dive", "Enzuigiri", "Tornado DDT", "Frankensteiner"
    ],
    "brawler": [
        "Stiff Right Hand", "Headbutt", "Lariat", "Running Knee", "Back Drop", 
        "Lou Thesz Press", "Eye Poke", "Low Blow", "DDT"
    ],
    "submission": [
        "Ankle Lock", "Crossface", "Guillotine Choke", "Sharpshooter", "Figure Four", 
        "Triangle Choke", "Fujiwara Armbar", "Sleeper Hold", "STF"
    ],
    "giant": [
        "Two-handed Chokeslam", "Big Splash", "Headbutt", "Bearhug", "Clubbing Blow", 
        "Gorilla Press", "Leg Drop", "Body Block"
    ],
    "hardcore": [
        "Kendo Stick Shot", "Chair Shot", "Garbage Can Lid Strike", "Piledriver", 
        "Powerbomb onto concrete", "Weapon Shot", "Biting"
    ],
    "striker": [
        "Roundhouse Kick", "Spinning Back Fist", "Knee Strike", "Elbow Smash", 
        "Palm Strike", "Leg Kick", "Superman Punch"
    ],
    "showman": [
        "Elbow Drop", "Neckbreaker", "Samoan Drop", "Bulldog", "Dropkick", 
        "Pump Handle Slam", "Russian Leg Sweep"
    ],
    "all_rounder": [
        "Suplex", "DDT", "Dropkick", "Clothesline", "Neckbreaker", 
        "Samoan Drop", "Backbreaker", "Scoop Slam"
    ]
}

# Generic fallbacks
GENERIC_MOVES = STYLE_MOVES["all_rounder"]

# Narrative templates for PWInsider Elite Recap
# {active} = wrestler doing move, {passive} = wrestler taking move
RECAP_TEMPLATES = {
    "opener": [
        "The match started with a feeling out process.",
        "{active} looked to gain an early advantage against {passive}.",
        "Both competitors circled each other, looking for an opening.",
        "The crowd was hot as the bell rang for {active} vs {passive}.",
    ],
    "momentum_shift": [
        "{active} turned the tide with a sudden {move}.",
        "{passive} fought back but was cut off by a {move} from {active}.",
        "Momentum shifted when {active} connected with a {move}.",
        "{active} began to take control, hitting a {move}.",
    ],
    "big_spot": [
        "HUGE {move} by {active} that nearly ended it!",
        "The crowd went wild as {active} hit a devastating {move}!",
        "{active} with a spectacular {move}!",
        "Incredible sequence ending with a {move} from {active}!",
    ],
    "near_fall": [
        "{passive} barely kicked out after a {move}!",
        "It looked like it was over after the {move}, but {passive} survived.",
        "So close! {active} can't believe {passive} kicked out of the {move}.",
        "The referee's hand came down for two... no! {passive} kicks out!",
    ],
    "finish": [
        "Finally, {active} hit the {move} for the 1-2-3.",
        "{active} secured the victory with a {move}.",
        "The end came when {active} connected with the {move} to win.",
        "{active} forced the tap out with a {move}.",
    ]
}

def get_move_for_style(style: str) -> str:
    """Get a random move appropriate for the fighting style."""
    style_key = style.lower().replace("fightingstyle.", "")
    moves = STYLE_MOVES.get(style_key, GENERIC_MOVES)
    return random.choice(moves)

def generate_commentary(
    wrestler_a_name: str, 
    wrestler_b_name: str, 
    match_rating: int, 
    wrestler_a_style: str = "all_rounder",
    wrestler_b_style: str = "all_rounder",
    num_spots: int = 5, 
    is_steel_cage: bool = False, 
    feud_intensity: str = "",
    winner_name: str = None,
    finisher_name: str = None
) -> List[str]:
    """
    Generates a "PWInsider Elite" style recap of the match.
    Uses wrestler styles to determine moves used in the narrative.
    """
    recap = []
    
    # 1. Intro
    intro_template = random.choice(RECAP_TEMPLATES["opener"])
    recap.append(intro_template.format(active=wrestler_a_name, passive=wrestler_b_name))

    # 2. Body of the match
    # Generate a sequence of exchanges
    current_attacker = wrestler_a_name
    current_victim = wrestler_b_name
    current_style = wrestler_a_style

    for i in range(num_spots):
        # Determine segment type based on match flow
        if i == num_spots - 1:
            # Setup for finish handled outside loop usually, but let's add a near fall here
            template = random.choice(RECAP_TEMPLATES["near_fall"])
        elif match_rating > 80 and random.random() > 0.6:
            template = random.choice(RECAP_TEMPLATES["big_spot"])
        else:
            template = random.choice(RECAP_TEMPLATES["momentum_shift"])

        # Select move based on attacker's style
        move = get_move_for_style(current_style)

        # Format line
        line = template.format(
            active=current_attacker, 
            passive=current_victim, 
            move=move
        )
        recap.append(line)

        # Switch momentum for next spot
        current_attacker, current_victim = current_victim, current_attacker
        current_style = wrestler_b_style if current_attacker == wrestler_b_name else wrestler_a_style

    # 3. Steel Cage specific line if applicable
    if is_steel_cage:
        recap.append(f"The steel cage came into play as {wrestler_a_name} threw {wrestler_b_name} into the mesh.")

    # 4. Feud line
    if feud_intensity:
        recap.append(f"The bad blood was evident throughout, this was a {feud_intensity} battle.")

    # 5. Finish
    if winner_name:
        finish_template = random.choice(RECAP_TEMPLATES["finish"])
        # Determine move: specific finisher or style-based fallback
        if finisher_name:
            winning_move = finisher_name
        else:
            # Fallback to style move of winner
            # Need to know winner's style. We have names/styles for A and B.
            if winner_name == wrestler_a_name:
                winning_move = get_move_for_style(wrestler_a_style)
            elif winner_name == wrestler_b_name:
                winning_move = get_move_for_style(wrestler_b_style)
            else:
                winning_move = "finishing maneuver" # Fallback for tag teams if name doesn't match single

        recap.append(finish_template.format(active=winner_name, move=winning_move))

    return recap


def generate_interference_commentary(stable_name: str, opponent_name: str, helped: bool) -> List[str]:
    """
    Generates recap lines for stable interference.
    """
    if helped:
        return [f"The finish was tainted when {stable_name} came down to distract {opponent_name}."]
    else:
        return [f"{stable_name} attempted to interfere but the referee caught them, causing a DQ!"]
