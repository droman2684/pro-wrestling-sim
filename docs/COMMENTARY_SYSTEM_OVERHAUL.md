# Commentary & Segment System Overhaul

## Overview

This document outlines the plan to overhaul the commentary system to provide more in-depth match reporting and add talking/promo segments to non-PPV shows. The goal is to create a more immersive wrestling show experience with dynamic storytelling.

---

## Current System (To Be Replaced)

### Current Commentary Generation

**Location:** `src/core/commentary.py`

**Current Features:**
- Basic, Mid-tier, and Dramatic moment templates
- Steel Cage specific moments
- Feud intensity moments (heated, intense, blood)
- Stable interference commentary
- Generic move list for substitution
- Single `generate_commentary()` function returns 7 random spots

**Current Problems:**
1. Commentary feels random and disconnected
2. No match structure (beginning, middle, end)
3. No momentum/flow tracking
4. No wrestler-specific moves or styles
5. No near-fall drama sequences
6. No finishing sequences
7. No talking segments on weekly shows
8. All matches feel the same regardless of style

---

## New Commentary System

### Match Phase System

Matches should now have distinct phases with appropriate commentary:

```python
class MatchPhase(Enum):
    OPENING = "opening"           # Feeling out process, tie-ups
    EARLY = "early"               # Building the match
    HEAT = "heat"                 # Heel/dominant wrestler in control
    HOPE_SPOT = "hope_spot"       # Underdog comeback teases
    COMEBACK = "comeback"         # Full comeback sequence
    FINISHING_STRETCH = "finish"  # Near falls, finisher attempts
    CONCLUSION = "conclusion"     # The actual finish
```

### New Commentary Structure

```python
class MatchCommentary:
    """Structured commentary for a complete match."""

    def __init__(self):
        self.introduction: str = ""           # Match announcement
        self.early_action: List[str] = []     # Opening phase
        self.mid_match: List[str] = []        # Heat/control segment
        self.hope_spots: List[str] = []       # Comeback teases
        self.near_falls: List[str] = []       # Dramatic kickouts
        self.finishing_sequence: List[str] = [] # Final stretch
        self.finish: str = ""                 # The ending
        self.post_match: List[str] = []       # After the bell

    def get_full_commentary(self) -> List[str]:
        """Returns all commentary in chronological order."""
        full = [self.introduction]
        full.extend(self.early_action)
        full.extend(self.mid_match)
        full.extend(self.hope_spots)
        full.extend(self.near_falls)
        full.extend(self.finishing_sequence)
        full.append(self.finish)
        full.extend(self.post_match)
        return [c for c in full if c]  # Filter empty strings
```

---

### Phase-Specific Commentary Templates

#### Opening Phase
```python
OPENING_TEMPLATES = [
    # Lock-up/Feeling Out
    "The bell rings and we're underway!",
    "{wrestler_a} and {wrestler_b} circle each other, sizing up their opponent.",
    "Collar-and-elbow tie-up to start things off.",
    "{wrestler_a} immediately goes for {wrestler_b}, no feeling out process here!",
    "The crowd is electric as these two finally meet in the ring!",
    "{wrestler_b} with a quick go-behind into a waistlock.",
    "Chain wrestling in the early going.",
    "{wrestler_a} backs {wrestler_b} into the corner - clean break... for now.",

    # Style-specific openers
    "{wrestler_a} shoots for a takedown early!", # Technical
    "{wrestler_b} starts with stiff strikes right away!", # Striker
    "High pace from the start as {wrestler_a} hits the ropes!", # High-flyer
    "{wrestler_a} uses their power advantage to shove {wrestler_b} down!", # Powerhouse
]
```

#### Heat/Control Phase
```python
HEAT_TEMPLATES = [
    # Wearing down opponent
    "{wrestler_a} is firmly in control now.",
    "{wrestler_b} is getting worn down by this relentless offense.",
    "A methodical attack here, working over the {body_part}.",
    "{wrestler_a} with a {rest_hold}, grinding down their opponent.",
    "The champion is picking their spots perfectly.",
    "{wrestler_b} reaching for the ropes... they're too far away!",
    "{wrestler_a} cutting off the ring, not letting {wrestler_b} escape.",
    "This has been one-sided for the past several minutes.",

    # Heel tactics
    "{wrestler_a} using the ropes for leverage! The ref didn't see it!",
    "A blatant choke by {wrestler_a}! Breaking at four!",
    "{wrestler_a} taking their time, taunting the crowd.",
    "The official is losing control here!",
    "{wrestler_a} goes to the eyes! Come on, ref!",
]
```

#### Hope Spot Phase
```python
HOPE_SPOT_TEMPLATES = [
    "{wrestler_b} fighting back! The crowd is coming alive!",
    "A flurry of offense from {wrestler_b}!",
    "{wrestler_b} ducks the {move} and connects with a {counter_move}!",
    "Is this the opening {wrestler_b} needed?",
    "The momentum may be shifting here!",
    "{wrestler_b} fires up! The crowd is behind them!",
    "Counter by {wrestler_b}! Both wrestlers are down!",
    "{wrestler_a} caught off guard! {wrestler_b} sees an opportunity!",
    "{wrestler_b} hulking up! They're feeding off the energy!",
    "Second wind for {wrestler_b}!",
]
```

#### Near Fall Sequences
```python
NEAR_FALL_TEMPLATES = [
    # Two counts
    "{wrestler_a} with the cover! ONE! TWO! NO! {wrestler_b} kicks out!",
    "Lateral press by {wrestler_a}! TWO COUNT ONLY!",
    "{wrestler_a} hooks the leg! ONE! TWO! Shoulder up!",
    "That was close! {wrestler_b} just got the shoulder up!",

    # Dramatic near falls (2.9 counts)
    "COVER! ONE! TWO! THR-NO! {wrestler_b} kicks out at the last second!",
    "{wrestler_a} can't believe it! How did {wrestler_b} survive that?!",
    "EVERYBODY THOUGHT THAT WAS IT! {wrestler_b} will not die!",
    "The referee's hand was coming down for three! {wrestler_b} just barely escaped!",
    "{wrestler_a} is in shock! That should have been the finish!",
    "The crowd thought we had a new champion!",
    "TWO AND NINE-TENTHS! {wrestler_b} stays alive!",

    # Finisher kickouts
    "{wrestler_b} kicked out of the {finisher}! UNBELIEVABLE!",
    "NO ONE kicks out of the {finisher}! Until now!",
    "How?! HOW did {wrestler_b} survive that?!",
]
```

#### Finishing Sequence
```python
FINISHING_SEQUENCE_TEMPLATES = [
    # Building to finish
    "{wrestler_a} is measuring {wrestler_b}...",
    "{wrestler_a} calling for the {finisher}!",
    "This could be it! {wrestler_a} setting up!",
    "The end is near! {wrestler_a} has that look in their eyes!",
    "{wrestler_b} struggles to their feet, right into position...",

    # Finisher reversal sequences
    "{wrestler_a} goes for the {finisher}! NO! {wrestler_b} escapes!",
    "Countered! {wrestler_b} saw it coming!",
    "{finisher} attempt! {wrestler_b} slips out the back door!",
    "{wrestler_a} can't connect! {wrestler_b} still has fight left!",

    # Final exchange
    "Both wrestlers throwing everything they have!",
    "Desperation from both competitors now!",
    "Who wants it more?!",
    "This is what championship matches are made of!",
]
```

#### Finish Templates
```python
FINISH_TEMPLATES = {
    "clean_pinfall": [
        "{finisher} connects! Cover! ONE! TWO! THREE! It's over!",
        "{winner} hits the {finisher}! That's it! We have a winner!",
        "ONE! TWO! THREE! {winner} wins this one clean in the middle!",
        "{finisher}! INTO THE COVER! ONE! TWO! THREE! {winner} is victorious!",
    ],
    "submission": [
        "{winner} locks in the {finisher}! {loser} has nowhere to go!",
        "{loser} is fading... the referee checks the arm... IT'S OVER!",
        "TAP! TAP! TAP! {loser} couldn't escape the {finisher}!",
        "{winner} wrenches back on the {finisher}! {loser} has no choice but to submit!",
    ],
    "rollup": [
        "ROLLUP! ONE! TWO! THREE! {winner} steals one!",
        "Small package out of nowhere! {winner} gets the surprise victory!",
        "Inside cradle! The referee counts three! What an upset!",
    ],
    "dq": [
        "The referee has seen enough! Disqualification!",
        "That's a DQ! {winner} wins by disqualification!",
        "The official is calling for the bell! {loser} went too far!",
    ],
    "countout": [
        "NINE! TEN! It's a count out! {winner} wins!",
        "{loser} couldn't make it back to the ring in time!",
        "The referee reaches ten! Count out victory for {winner}!",
    ],
}
```

#### Post-Match Templates
```python
POST_MATCH_TEMPLATES = [
    # Winner celebration
    "{winner} celebrates in the ring!",
    "{winner} has their hand raised in victory!",
    "What a performance by {winner} tonight!",

    # Title match specific
    "{winner} retains the {title}!",
    "WE HAVE A NEW {title} CHAMPION! {winner}!",
    "{winner} is STILL your {title}!",

    # Feud specific
    "{winner} finally gets their revenge!",
    "This rivalry may finally be over!",
    "{winner} stands tall, but you have to think {loser} will want another shot!",

    # Post-match attack (random chance)
    "Wait! {attacker} is back! They're attacking {victim}!",
    "The match is over but the assault continues!",
    "{attacker} is sending a message!",
]
```

---

### Match-Type Specific Commentary

#### Singles Match Commentary Flow
```python
def generate_singles_commentary(
    wrestler_a: 'Wrestler',
    wrestler_b: 'Wrestler',
    winner: 'Wrestler',
    loser: 'Wrestler',
    rating: int,
    is_title_match: bool = False,
    feud: 'Feud' = None,
    finish_type: str = "clean_pinfall"
) -> MatchCommentary:
    """Generate full structured commentary for a singles match."""

    commentary = MatchCommentary()

    # Introduction based on match type
    if is_title_match:
        commentary.introduction = f"This is for the {title_name}! {wrestler_a.name} defends against {wrestler_b.name}!"
    elif feud:
        commentary.introduction = f"The rivalry continues! {wrestler_a.name} faces {wrestler_b.name}!"
    else:
        commentary.introduction = f"Singles competition! {wrestler_a.name} versus {wrestler_b.name}!"

    # Generate phases based on match rating
    num_spots = calculate_spots_by_rating(rating)

    # Early action (2-3 spots)
    commentary.early_action = generate_phase_spots(OPENING_TEMPLATES, ...)

    # Mid-match (3-5 spots based on rating)
    commentary.mid_match = generate_phase_spots(HEAT_TEMPLATES, ...)

    # Hope spots (1-3 spots)
    commentary.hope_spots = generate_phase_spots(HOPE_SPOT_TEMPLATES, ...)

    # Near falls (more for higher rated matches)
    num_near_falls = max(1, rating // 25)  # 1-4 near falls
    commentary.near_falls = generate_near_falls(num_near_falls, ...)

    # Finishing sequence (2-4 spots)
    commentary.finishing_sequence = generate_finishing_sequence(...)

    # The actual finish
    commentary.finish = generate_finish(finish_type, winner, loser, ...)

    # Post-match (1-2 spots)
    commentary.post_match = generate_post_match(winner, loser, ...)

    return commentary
```

#### Tag Team Match Specific
```python
TAG_TEAM_TEMPLATES = [
    # Tag sequences
    "{team_a_member1} makes the tag! Fresh man in!",
    "Hot tag to {team_a_member2}! They're cleaning house!",
    "{team_b} cutting the ring in half, isolating {isolated_wrestler}!",
    "Great teamwork by {team_a}! Double team {move}!",
    "{team_b_member1} reaches for the tag... {team_b_member2} isn't there!",
    "The legal men are {legal_a} and {legal_b}!",
    "Blind tag by {team_a}! The referee didn't see it!",
    "DOUBLE {move}! This is tag team wrestling at its finest!",
    "{team_a} with perfect chemistry! They've done this a thousand times!",
    "Miscommunication by {team_b}! They just took each other out!",
]
```

#### Multi-Man Match Specific
```python
MULTI_MAN_TEMPLATES = [
    # Chaos commentary
    "Bodies everywhere! This is controlled chaos!",
    "{wrestler_a} breaks up the pin! {wrestler_b} almost had it!",
    "Triple suplex! All three/four wrestlers down!",
    "Tower of doom in the corner! Everybody felt that!",
    "{wrestler_a} playing it smart, letting the others fight!",
    "Pinfall broken up again! No one can get a three count!",
    "{wrestler_a} threw {wrestler_b} into {wrestler_c}! Taking out two at once!",
    "The referee is struggling to maintain order!",
    "Everyone is getting their moments in this one!",
]
```

#### Ladder Match Specific
```python
LADDER_MATCH_TEMPLATES = [
    # Ladder spots
    "The ladder is set up in the center of the ring!",
    "{wrestler} is climbing! Can they reach the prize?!",
    "PUSHED OFF THE LADDER! {wrestler} crashes to the mat!",
    "Sunset flip powerbomb OFF THE LADDER!",
    "The ladder is bent in half from that impact!",
    "{wrestler} with a diving {move} off the top of the ladder!",
    "Both wrestlers reaching for the prize! Who will grab it first?!",
    "The ladder tips over! {wrestler} lands on the ropes!",
    "A second ladder has been brought into play!",
    "THEY'RE FIGHTING ON TOP OF TWO LADDERS!",
    "{wrestler} is inches away from victory!",
    "The fingertips are touching the {prize}!",
]
```

---

## Talking Segments System (Non-PPV Shows)

### Segment Types

Weekly TV shows should include 2-4 non-match segments to build storylines:

```python
class SegmentType(Enum):
    PROMO = "promo"                    # Single wrestler/stable promo
    INTERVIEW = "interview"            # Backstage interview
    CONFRONTATION = "confrontation"    # Two wrestlers face off
    CONTRACT_SIGNING = "contract"      # Contract signing (usually goes wrong)
    TALK_SHOW = "talk_show"           # In-ring talk show segment
    BACKSTAGE_BRAWL = "brawl"         # Backstage fight
    AUTHORITY_SEGMENT = "authority"    # GM/Owner announcement
    CELEBRATION = "celebration"        # Title celebration
    VIDEO_PACKAGE = "video"           # Recap/hype video
    DEBUT = "debut"                   # New wrestler debut
    RETURN = "return"                 # Returning wrestler
```

### Segment Data Structure

```python
@dataclass
class TalkingSegment:
    """A non-match segment on the show."""
    segment_type: SegmentType
    participants: List['Wrestler']
    rating: int                        # Segment quality rating
    heat_generated: int               # Heat change for participants
    transcript: List[str]             # The segment "script"
    outcome: str                      # What happened (optional)

    # Optional fields
    feud: Optional['Feud'] = None
    stable: Optional['Stable'] = None
    title: Optional['Title'] = None
    is_heel_turn: bool = False
    is_face_turn: bool = False
    attack_occurred: bool = False
    attacker: Optional['Wrestler'] = None
```

### Promo Segment Templates

```python
PROMO_TEMPLATES = {
    "face_champion": [
        "{wrestler} comes to the ring with the {title} over their shoulder.",
        "\"Last week, {opponent} thought they could take what's mine. But I'm still standing here, YOUR {title}!\"",
        "The crowd chants \"{wrestler}! {wrestler}!\"",
        "\"I'll defend this title against anyone, anytime, anywhere! That's a promise!\"",
        "{wrestler} raises the title high as the crowd cheers.",
    ],
    "heel_champion": [
        "{wrestler} struts to the ring, {title} gleaming.",
        "\"You people don't deserve a champion like me. None of you could last five minutes in this ring with me!\"",
        "Heavy boos from the crowd.",
        "\"I've beaten everyone in this company. There's no one left who can challenge me!\"",
        "{wrestler} laughs as the crowd jeers.",
    ],
    "challenger_callout": [
        "{wrestler} wastes no time getting to the point.",
        "\"Hey {champion}! You've been ducking me for weeks! Get out here and face me like a man!\"",
        "The crowd pops huge, chanting for the confrontation.",
        "\"You can run, but you can't hide forever! I WILL be the next {title}!\"",
        "{wrestler} paces the ring, waiting...",
    ],
    "heel_beatdown_aftermath": [
        "{wrestler} limps to the ring, still feeling the effects of last week's attack.",
        "\"You think you hurt me? You think you broke me? {attacker}, you just made the biggest mistake of your life!\"",
        "The crowd rallies behind {wrestler}.",
        "\"At {ppv_name}, I'm going to make you pay for every second of pain you caused me!\"",
        "{wrestler} stares down the entrance ramp with fire in their eyes.",
    ],
}
```

### Interview Segment Templates

```python
INTERVIEW_TEMPLATES = {
    "pre_match": [
        "Backstage, {interviewer} is standing by with {wrestler}.",
        "\"{wrestler}, tonight you face {opponent} in a huge match. What's your strategy?\"",
        "{wrestler} looks focused and determined.",
        "\"Tonight, I prove to the world why I belong at the top. {opponent} is standing in my way, and I'm going to run right through them.\"",
        "{wrestler} walks off toward the gorilla position.",
    ],
    "post_match_winner": [
        "{interviewer} catches up with {wrestler} backstage.",
        "\"What a victory tonight! How are you feeling?\"",
        "{wrestler} is still catching their breath, sweat dripping down their face.",
        "\"That was the toughest match of my career. But I dug deep and found a way. This is just the beginning!\"",
        "{wrestler} walks off with their arm raised.",
    ],
    "post_match_loser": [
        "{interviewer} approaches {wrestler} as they walk backstage, clearly frustrated.",
        "\"A tough loss tonight. What went wrong out there?\"",
        "{wrestler} stops, jaw clenched.",
        "\"What went wrong? I made one mistake, and {opponent} capitalized. But this isn't over. Not by a long shot.\"",
        "{wrestler} storms off, pushing past the camera.",
    ],
    "interrupted": [
        "{interviewer} begins the interview with {wrestler}.",
        "\"Tonight you-\" ",
        "Suddenly, {attacker} appears and blindsides {wrestler}!",
        "The interview area descends into chaos as {attacker} lays waste to {wrestler}!",
        "{attacker} stands over the fallen {wrestler}. \"See you Sunday.\"",
        "Officials rush in to separate them as we go to commercial!",
    ],
}
```

### Confrontation Segment Templates

```python
CONFRONTATION_TEMPLATES = {
    "face_vs_heel": [
        "{face} is in the ring when {heel}'s music hits!",
        "{heel} walks down slowly, microphone in hand, smirking.",
        "\"You think you're so special, don't you {face}? The fans love you. But love doesn't win championships.\"",
        "{face} responds: \"The difference between us is that I earn my opportunities. You just steal them.\"",
        "The tension is palpable as they stand nose-to-nose!",
        "{heel} shoves {face}! {face} fires back with a right hand!",
        "They're brawling! Security floods the ring to separate them!",
        "This rivalry just reached a boiling point!",
    ],
    "staredown": [
        "{wrestler_a} and {wrestler_b} meet in the center of the ring.",
        "Neither man is backing down.",
        "The crowd is on their feet, sensing what's about to happen.",
        "Nose to nose... forehead to forehead...",
        "{wrestler_a} says something we can't hear... {wrestler_b}'s expression changes...",
        "They're fighting! {wrestler_a} and {wrestler_b} are throwing hands!",
        "Officials rush out to separate them before their match at {ppv_name}!",
    ],
    "alliance_formed": [
        "{wrestler_a} is in the ring, calling out {enemy}.",
        "But before {enemy} can respond, {wrestler_b}'s music hits!",
        "{wrestler_a} looks confused as {wrestler_b} enters the ring.",
        "{wrestler_b}: \"I know we've had our differences. But {enemy} is a bigger problem for both of us.\"",
        "{wrestler_a} considers for a moment... then extends their hand!",
        "They shake! An unlikely alliance has been formed!",
        "The enemy of my enemy is my friend!",
    ],
}
```

### Contract Signing Templates

```python
CONTRACT_SIGNING_TEMPLATES = [
    # Setup
    "The ring is set with a table, two chairs, and the contract.",
    "{authority_figure} stands in the ring to officiate the signing.",
    "First, {wrestler_a} makes their way to the ring.",
    "{wrestler_b} follows, and the tension is immediate.",
    "\"Gentlemen, at {ppv_name}, you will face each other for the {title}. Please, sign the contract.\"",

    # The signing (various outcomes)
    # Peaceful (rare)
    "{wrestler_a} signs without incident. {wrestler_b} does the same.",
    "\"It's official! The match is signed!\"",
    "Both competitors stand and shake hands... for now.",

    # Standard chaos
    "{wrestler_a} signs and slides it to {wrestler_b}.",
    "{wrestler_b} picks up the pen... then throws it at {wrestler_a}!",
    "The table goes flying! They're brawling in the ring!",
    "The contract signing has descended into chaos!",
    "Security tries to restore order as we go off the air!",

    # Table spot
    "{wrestler_a} puts {wrestler_b} through the table! Contract papers flying everywhere!",
    "{wrestler_a} signs the contract while {wrestler_b} lies in the wreckage!",
    "\"I'll see you at {ppv_name}!\"",
]
```

### Talk Show Segment Templates

```python
TALK_SHOW_TEMPLATES = {
    "highlight_reel": {
        "name": "The Highlight Reel",
        "host": "Chris Jericho-type",
        "setup": [
            "\"Welcome to the most must-see talk show in wrestling history... THE HIGHLIGHT REEL!\"",
            "The host poses as the crowd reacts.",
            "\"Tonight, my guest is someone who thinks they're better than me. {guest}, get out here!\"",
        ],
    },
    "kings_court": {
        "name": "King's Court",
        "host": "Jerry Lawler-type",
        "setup": [
            "\"All rise for the King's Court!\"",
            "The host sits on their throne, crown on head.",
            "\"Tonight, I have an audience with {guest}. Bring them out!\"",
        ],
    },
    "vip_lounge": {
        "name": "VIP Lounge",
        "host": "MVP-type",
        "setup": [
            "The ring is set up like a VIP section - couches, velvet ropes.",
            "\"Welcome to the VIP Lounge! I'm your host, and tonight, I have a VERY important person...\"",
            "\"Please welcome... {guest}!\"",
        ],
    },
    "generic": {
        "name": "{host}'s Talk Show",
        "setup": [
            "{host} welcomes the audience to their show.",
            "\"My guest tonight has been making waves. Please welcome {guest}!\"",
        ],
    },
}

# Talk show outcomes
TALK_SHOW_OUTCOMES = [
    "The segment ends peacefully with a handshake.",
    "{guest} attacks {host}! The talk show has gone off the rails!",
    "A third party interrupts! {intruder} is here!",
    "{host} reveals a bombshell that shocks everyone!",
    "The segment ends with {guest} issuing an open challenge!",
    "{host} and {guest} form an unlikely alliance!",
]
```

---

### Segment Rating Calculation

```python
def calculate_segment_rating(
    segment_type: SegmentType,
    participants: List['Wrestler'],
    feud: Optional['Feud'] = None,
    is_title_related: bool = False
) -> int:
    """Calculate quality rating for a talking segment."""

    # Base: average mic skills of participants
    avg_mic = sum(w.mic_skills for w in participants) / len(participants)

    # Charisma bonus
    avg_charisma = sum(w.charisma for w in participants) / len(participants)
    charisma_bonus = avg_charisma / 20  # 0-5 points

    # Segment type modifier
    type_modifiers = {
        SegmentType.PROMO: 0,
        SegmentType.INTERVIEW: -5,
        SegmentType.CONFRONTATION: +10,
        SegmentType.CONTRACT_SIGNING: +15,
        SegmentType.TALK_SHOW: +5,
        SegmentType.BACKSTAGE_BRAWL: +5,
        SegmentType.AUTHORITY_SEGMENT: 0,
        SegmentType.CELEBRATION: +5,
        SegmentType.DEBUT: +20,
        SegmentType.RETURN: +15,
    }
    type_bonus = type_modifiers.get(segment_type, 0)

    # Feud bonus
    feud_bonus = 0
    if feud:
        feud_bonus = feud.get_intensity_bonus()

    # Title bonus
    title_bonus = 5 if is_title_related else 0

    # Random variance
    variance = random.randint(-5, 5)

    rating = avg_mic + charisma_bonus + type_bonus + feud_bonus + title_bonus + variance

    return min(100, max(0, int(rating)))
```

---

### Heat/Momentum Effects

Segments should affect wrestler heat and storyline momentum:

```python
def apply_segment_effects(
    segment: TalkingSegment,
    game_state: 'GameState'
) -> None:
    """Apply heat and momentum changes from a segment."""

    base_heat_change = segment.rating // 20  # 0-5 base

    for participant in segment.participants:
        # Good segments increase heat
        heat_gain = base_heat_change

        # Alignment bonus (heels get heat from bad actions, faces from good)
        if participant.alignment == "Heel" and segment.attack_occurred:
            heat_gain += 3
        elif participant.alignment == "Face" and not segment.attack_occurred:
            heat_gain += 2

        # Turn effects
        if segment.is_heel_turn and participant == segment.attacker:
            heat_gain += 10
            participant.alignment = "Heel"
        elif segment.is_face_turn:
            heat_gain += 8
            participant.alignment = "Face"

        participant.heat = min(100, participant.heat + heat_gain)

    # Update feud heat if applicable
    if segment.feud:
        segment.feud.heat = min(100, segment.feud.heat + segment.rating // 10)
```

---

### Show Structure with Segments

#### Non-PPV (Weekly TV) Show Format

```python
class WeeklyShow(Show):
    """Extended show class with segment support."""

    def __init__(self, name: str):
        super().__init__(name, is_ppv=False)
        self.segments: List[TalkingSegment] = []
        self.segment_slots = 3  # Default: 3 talking segments per show

    def add_segment(self, segment: TalkingSegment) -> None:
        """Add a talking segment to the show."""
        self.segments.append(segment)

    def auto_generate_segments(self, game_state: 'GameState') -> None:
        """Automatically generate segments based on current storylines."""
        # Segment 1: Opening promo (champion or top babyface)
        # Segment 2: Feud confrontation or interview
        # Segment 3: Contract signing or talk show (if PPV upcoming)
        pass
```

#### Suggested Show Flow

```
WEEKLY TV SHOW STRUCTURE:
==========================
1. Opening Promo Segment (5-10 min)
   - Champion, top face, or authority figure
   - Sets up the night's main storylines

2. Match 1: Opening Match
   - Usually midcard, good workers
   - Gets the crowd warmed up

3. Backstage Interview Segment
   - Pre-match hype for later match
   - Or post-attack reaction

4. Match 2: Secondary Match
   - Could be tag team or women's match
   - Continues ongoing storylines

5. In-Ring Confrontation/Contract Signing
   - Main feud face-to-face
   - Usually ends in chaos

6. Match 3: Featured Match
   - Upper midcard or #1 contender
   - Higher stakes

7. Backstage Segment
   - Authority makes announcement
   - Or backstage attack/brawl

8. Match 4: Main Event
   - Top stars or title match
   - Show-closing angle possible

POST-SHOW:
- Dark match for live crowd
```

---

### Segment Result Data Structure

```python
@dataclass
class SegmentResult:
    """Result of a talking segment for show results."""
    segment_type: str
    participants: List[str]
    rating: int
    transcript: List[str]
    outcome: str
    heat_changes: Dict[str, int]  # wrestler_name: heat_change
    turn_occurred: bool = False
    turn_type: str = ""  # "heel" or "face"
    turn_wrestler: str = ""
    attack_occurred: bool = False
    attacker_name: str = ""
    victim_name: str = ""
```

---

### UI Changes Required

#### 1. Show Results Page (`results.html`)
- Add segment results between matches
- Display segment ratings and transcripts
- Show heat changes from segments
- Highlight turns and attacks

#### 2. Booking Page (`booking.html`)
- Add "Add Segment" button for weekly shows
- Segment type dropdown
- Participant selection
- Auto-generate segments option

#### 3. New Segment Booking Modal
```html
<!-- Segment Booking Modal -->
<div class="modal" id="addSegmentModal">
    <div class="modal-content">
        <h5>Add Talking Segment</h5>
        <form action="{{ url_for('add_segment') }}" method="post">
            <select name="segment_type">
                <option value="promo">Promo</option>
                <option value="interview">Interview</option>
                <option value="confrontation">Confrontation</option>
                <option value="contract">Contract Signing</option>
                <option value="talk_show">Talk Show</option>
            </select>

            <select name="participants" multiple>
                {% for w in wrestlers %}
                <option value="{{ w.id }}">{{ w.name }}</option>
                {% endfor %}
            </select>

            <button type="submit">Add Segment</button>
        </form>
    </div>
</div>
```

---

### Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| `src/core/commentary.py` | Rewrite | Complete overhaul with phased commentary |
| `src/core/segment.py` | Create | New file for talking segment classes |
| `src/core/show.py` | Modify | Add segment support to Show class |
| `src/core/game_state.py` | Modify | Add segment result data classes |
| `src/services/game_service.py` | Modify | Add segment management methods |
| `src/ui/web/app.py` | Modify | Add segment booking routes |
| `src/ui/web/templates/booking.html` | Modify | Add segment booking UI |
| `src/ui/web/templates/results.html` | Modify | Display segment results |

---

### Summary of Changes

| Feature | Current | New |
|---------|---------|-----|
| Commentary Phases | None | 7 distinct phases |
| Match Introduction | None | Context-aware intro |
| Near Fall Drama | Basic | Dramatic 2.9 counts |
| Finishing Sequence | Random | Structured buildup |
| Post-Match | None | Winner/loser reactions |
| Talking Segments | None | 10 segment types |
| Segment Rating | N/A | Mic skill + charisma based |
| Heat System | Basic | Segment-influenced |
| Show Structure | Matches only | Matches + Segments |
| Commentary Templates | ~50 | 200+ |

This overhaul will create a more immersive, TV-like experience with proper match storytelling and non-match content that builds storylines.
