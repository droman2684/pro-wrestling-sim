# Wrestler Rating System Overhaul

## Overview

This document outlines the plan to overhaul the wrestler rating system from the current simplified model to a more comprehensive WWE 2K-style attribute system. The goal is to better differentiate wrestlers from each other and create more realistic match simulations.

---

## Current System (To Be Replaced)

### Current Attributes

**In-Ring Stats (4 attributes):**
- `brawl` - Striking/power moves
- `tech` - Technical wrestling ability
- `air` - High-flying moves
- `psychology` - Ring awareness and storytelling

**Entertainment Stats (4 attributes):**
- `mic` - Microphone skills
- `charisma` - Natural charisma
- `look` - Physical appearance
- `star_quality` - Overall star presence

**Overall Rating Calculation:**
```python
ring_avg = (brawl + tech + air + psych) / 4
ent_avg = (mic + charisma + look) / 3
overall = int((ring_avg * 0.6) + (ent_avg * 0.4))
```

### Problems with Current System
1. Too few attributes - wrestlers feel samey
2. No physical attributes (strength, speed, etc.)
3. No defensive capabilities tracked
4. No special moves or fighting style differentiation
5. Gimmick/nickname is required (should be optional)

---

## New WWE 2K-Style Rating System

### Identity Changes

```python
# OLD
self.name = data['name']
self.gimmick = data['gimmick_name']  # Required

# NEW
self.name = data['name']
self.nickname = data.get('nickname', None)  # Optional - can be None/empty
self.billing_name = data.get('billing_name', None)  # Optional (e.g., "The Phenomenal AJ Styles")
```

**Display Logic:**
- If `nickname` exists: Show as `"Nickname" Name` (e.g., "The Hitman" Bret Hart)
- If `nickname` is None/empty: Show just `Name` (e.g., Bret Hart)
- `billing_name` used for special announcements/entrances

---

### New Attribute Categories

#### 1. Physical Attributes (6 attributes)

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `strength` | Raw power for slams, power moves | Damage dealt with power moves, ability to lift heavier opponents |
| `speed` | Movement speed, attack quickness | Initiative in matches, counter opportunities |
| `agility` | Flexibility, acrobatic ability | High-flying move success, dodge chance |
| `durability` | Toughness, ability to absorb damage | Damage resistance, kickout ability |
| `stamina` | Cardio, endurance | How long before fatigue affects performance |
| `recovery` | How quickly they bounce back | Rest between matches, in-match recovery |

#### 2. Offensive Skills (8 attributes)

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `striking` | Punches, kicks, forearms, chops | Strike damage and accuracy |
| `grappling` | Suplexes, slams, throws | Grapple move success rate |
| `submission` | Holds, locks, stretches | Submission damage and escape difficulty |
| `high_flying` | Top rope moves, dives, springboards | High-risk move success rate |
| `hardcore` | Weapon usage, extreme moves | Weapon damage, hardcore match performance |
| `power_moves` | Big slams, powerbombs, press slams | Power move damage, lifting ability |
| `technical` | Chain wrestling, reversals, counters | Counter success rate, match flow |
| `dirty_tactics` | Eye rakes, low blows, cheating | Ref distraction success, illegal move effectiveness |

#### 3. Defensive Skills (4 attributes)

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `strike_defense` | Blocking/avoiding strikes | Damage reduction from strikes |
| `grapple_defense` | Escaping holds, blocking grapples | Escape rate from grapples |
| `aerial_defense` | Catching/countering high-flyers | Counter rate against aerial attacks |
| `ring_awareness` | Positioning, rope breaks, ring IQ | Avoiding dangerous situations |

#### 4. Entertainment/Presence (5 attributes)

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `mic_skills` | Promo ability, trash talk | Promo segment quality, feud heat generation |
| `charisma` | Natural magnetism, crowd connection | Crowd reaction, merchandise sales |
| `look` | Physical appearance, presentation | Visual appeal, marketability |
| `star_power` | Overall aura, main event presence | Match importance multiplier, drawing power |
| `entrance` | Entrance quality, theatrics | Show opening impact, crowd energy |

#### 5. Intangibles (4 attributes)

| Attribute | Description | Impact |
|-----------|-------------|--------|
| `psychology` | Storytelling, selling, drama | Match quality bonus, crowd investment |
| `consistency` | Reliability, steady performance | Variance in match ratings |
| `big_match` | Performance under pressure | Bonus in title matches, PPV main events |
| `clutch` | Ability to win close matches | Late-match performance boost |

---

### Fighting Style System

Each wrestler should have a primary and secondary fighting style that affects how their attributes are weighted in matches.

```python
class FightingStyle(Enum):
    POWERHOUSE = "powerhouse"      # Strength/power moves focused
    TECHNICIAN = "technician"      # Technical wrestling, submissions
    HIGH_FLYER = "high_flyer"      # Aerial moves, speed
    BRAWLER = "brawler"            # Striking, hardcore
    SHOWMAN = "showman"            # Entertainment, crowd work
    SUBMISSION_SPECIALIST = "submission_specialist"  # Locks and holds
    ALL_ROUNDER = "all_rounder"    # Balanced across all areas
    GIANT = "giant"                # Size-based offense, durability
    HARDCORE_SPECIALIST = "hardcore"  # Extreme/weapon specialist
    STRIKER = "striker"            # MMA-style striking
```

**Implementation:**
```python
self.primary_style = data.get('primary_style', 'all_rounder')
self.secondary_style = data.get('secondary_style', None)  # Optional
```

---

### Special Moves System

#### Finisher(s)
```python
self.finishers = [
    {
        "name": "Tombstone Piledriver",
        "type": "power",           # power, technical, aerial, submission, strike
        "damage": 95,              # Base damage (0-100)
        "setup_required": False,   # Needs specific setup?
        "can_be_reversed": True,
        "banned_in_pg": False      # For content ratings
    }
]
```

#### Signature Moves
```python
self.signatures = [
    {
        "name": "Old School",
        "type": "aerial",
        "damage": 70,
        "builds_momentum": True    # Helps set up finisher
    }
]
```

#### Taunts
```python
self.taunts = [
    {
        "name": "Throat Slash",
        "momentum_boost": 15,
        "crowd_reaction": "pop"    # pop, heat, mixed
    }
]
```

---

### Overall Rating Calculation

The new overall rating should be calculated with weighted categories based on the wrestler's role:

```python
def calculate_overall(self) -> int:
    # Physical (20% of overall)
    physical_avg = (
        self.strength + self.speed + self.agility +
        self.durability + self.stamina + self.recovery
    ) / 6

    # Offense (30% of overall)
    offense_avg = (
        self.striking + self.grappling + self.submission +
        self.high_flying + self.power_moves + self.technical
    ) / 6
    # Note: hardcore and dirty_tactics not included in base overall

    # Defense (15% of overall)
    defense_avg = (
        self.strike_defense + self.grapple_defense +
        self.aerial_defense + self.ring_awareness
    ) / 4

    # Entertainment (20% of overall)
    entertainment_avg = (
        self.mic_skills + self.charisma + self.look + self.star_power
    ) / 4
    # Note: entrance not included in overall

    # Intangibles (15% of overall)
    intangibles_avg = (
        self.psychology + self.consistency + self.big_match + self.clutch
    ) / 4

    overall = (
        (physical_avg * 0.20) +
        (offense_avg * 0.30) +
        (defense_avg * 0.15) +
        (entertainment_avg * 0.20) +
        (intangibles_avg * 0.15)
    )

    return int(overall)
```

---

### New Data Structure

#### JSON Format
```json
{
    "id": 1,
    "name": "Bret Hart",
    "nickname": "The Hitman",
    "billing_name": "The Best There Is, The Best There Was, The Best There Ever Will Be",

    "bio": {
        "age": 35,
        "height": 72,
        "weight": 234,
        "home_region": "Calgary, Alberta, Canada",
        "years_active": 15
    },

    "physical": {
        "strength": 72,
        "speed": 78,
        "agility": 75,
        "durability": 85,
        "stamina": 88,
        "recovery": 80
    },

    "offense": {
        "striking": 80,
        "grappling": 88,
        "submission": 95,
        "high_flying": 70,
        "hardcore": 55,
        "power_moves": 70,
        "technical": 98,
        "dirty_tactics": 45
    },

    "defense": {
        "strike_defense": 82,
        "grapple_defense": 90,
        "aerial_defense": 78,
        "ring_awareness": 95
    },

    "entertainment": {
        "mic_skills": 72,
        "charisma": 85,
        "look": 80,
        "star_power": 92,
        "entrance": 85
    },

    "intangibles": {
        "psychology": 98,
        "consistency": 95,
        "big_match": 95,
        "clutch": 88
    },

    "styles": {
        "primary": "technician",
        "secondary": "submission_specialist"
    },

    "moves": {
        "finishers": [
            {
                "name": "Sharpshooter",
                "type": "submission",
                "damage": 92
            }
        ],
        "signatures": [
            {
                "name": "Russian Leg Sweep",
                "type": "technical",
                "damage": 65
            },
            {
                "name": "Side Backbreaker",
                "type": "power",
                "damage": 60
            }
        ]
    },

    "status": {
        "morale": 100,
        "condition": 100,
        "alignment": "Face",
        "heat": 85,
        "wins": 0,
        "losses": 0,
        "has_mitb_briefcase": false,
        "is_injured": false,
        "injury_weeks_remaining": 0
    }
}
```

---

### Python Class Structure

```python
class Wrestler:
    def __init__(self, data: dict):
        # Identity
        self.id = data['id']
        self.name = data['name']
        self.nickname = data.get('nickname', None)  # OPTIONAL
        self.billing_name = data.get('billing_name', None)  # OPTIONAL

        # Bio
        self.age = data['bio']['age']
        self.height = data['bio'].get('height', 72)  # inches
        self.weight = data['bio'].get('weight', 220)  # pounds
        self.region = data['bio']['home_region']
        self.years_active = data['bio'].get('years_active', 1)

        # Physical Attributes
        self.strength = data['physical']['strength']
        self.speed = data['physical']['speed']
        self.agility = data['physical']['agility']
        self.durability = data['physical']['durability']
        self.stamina = data['physical']['stamina']
        self.recovery = data['physical']['recovery']

        # Offensive Skills
        self.striking = data['offense']['striking']
        self.grappling = data['offense']['grappling']
        self.submission = data['offense']['submission']
        self.high_flying = data['offense']['high_flying']
        self.hardcore = data['offense']['hardcore']
        self.power_moves = data['offense']['power_moves']
        self.technical = data['offense']['technical']
        self.dirty_tactics = data['offense']['dirty_tactics']

        # Defensive Skills
        self.strike_defense = data['defense']['strike_defense']
        self.grapple_defense = data['defense']['grapple_defense']
        self.aerial_defense = data['defense']['aerial_defense']
        self.ring_awareness = data['defense']['ring_awareness']

        # Entertainment
        self.mic_skills = data['entertainment']['mic_skills']
        self.charisma = data['entertainment']['charisma']
        self.look = data['entertainment']['look']
        self.star_power = data['entertainment']['star_power']
        self.entrance = data['entertainment']['entrance']

        # Intangibles
        self.psychology = data['intangibles']['psychology']
        self.consistency = data['intangibles']['consistency']
        self.big_match = data['intangibles']['big_match']
        self.clutch = data['intangibles']['clutch']

        # Fighting Styles
        self.primary_style = data['styles']['primary']
        self.secondary_style = data['styles'].get('secondary', None)

        # Special Moves
        self.finishers = data['moves'].get('finishers', [])
        self.signatures = data['moves'].get('signatures', [])

        # Dynamic Status (unchanged from original)
        self.morale = data['status']['morale']
        self.condition = data['status']['condition']
        self.alignment = data['status']['alignment']
        self.heat = data['status'].get('heat', 50)
        self.wins = data['status'].get('wins', 0)
        self.losses = data['status'].get('losses', 0)
        self.has_mitb_briefcase = data['status'].get('has_mitb_briefcase', False)
        self.is_injured = data['status'].get('is_injured', False)
        self.injury_weeks_remaining = data['status'].get('injury_weeks_remaining', 0)

    @property
    def display_name(self) -> str:
        """Returns the display name with optional nickname."""
        if self.nickname:
            return f'"{self.nickname}" {self.name}'
        return self.name

    @property
    def short_name(self) -> str:
        """Returns just the name without nickname."""
        return self.name
```

---

### Rating Tiers

| Rating Range | Tier | Description |
|--------------|------|-------------|
| 95-100 | Legend | All-time greats, once in a generation |
| 90-94 | Elite | Top tier main eventers |
| 85-89 | Main Eventer | Championship caliber |
| 80-84 | Upper Midcard | Title contenders |
| 75-79 | Midcard | Solid reliable performers |
| 70-74 | Lower Midcard | Enhancement talent with potential |
| 65-69 | Jobber | Used to put others over |
| 60-64 | Rookie | Green, still developing |
| Below 60 | Local Talent | Barely trained |

---

### Migration Strategy

#### Phase 1: Update Core Classes
1. Update `Wrestler` class with new attributes
2. Add backward compatibility for old data format
3. Create migration script to convert old wrestler data

#### Phase 2: Update Match Simulation
1. Modify match engine to use new attributes
2. Implement fighting style bonuses
3. Add finisher/signature move system

#### Phase 3: Update UI
1. Update wrestler profile page to show new stats
2. Update create wrestler form with all new fields
3. Add stat bars for each category
4. Make nickname field optional with "(Optional)" label

#### Phase 4: Data Migration
1. Create script to migrate existing wrestlers.json
2. Intelligently map old stats to new system
3. Assign default values for new fields

---

### Old to New Stat Mapping

When migrating existing data:

```python
def migrate_wrestler(old_data: dict) -> dict:
    """Convert old wrestler format to new format."""

    old_ring = old_data['stats_ring']
    old_ent = old_data['stats_entertainment']

    return {
        "id": old_data['id'],
        "name": old_data['name'],
        "nickname": old_data.get('gimmick_name', None),  # Old gimmick becomes nickname
        "billing_name": None,

        "bio": {
            "age": old_data['bio']['age'],
            "height": 72,  # Default
            "weight": 220,  # Default
            "home_region": old_data['bio']['home_region'],
            "years_active": 5  # Default
        },

        "physical": {
            "strength": old_ring['brawl'],  # Map brawl to strength
            "speed": (old_ring['air'] + old_ring['tech']) // 2,
            "agility": old_ring['air'],
            "durability": 75,  # Default
            "stamina": old_ring['stamina'],
            "recovery": 70  # Default
        },

        "offense": {
            "striking": old_ring['brawl'],
            "grappling": (old_ring['brawl'] + old_ring['tech']) // 2,
            "submission": old_ring['tech'],
            "high_flying": old_ring['air'],
            "hardcore": old_ring['brawl'] - 10,
            "power_moves": old_ring['brawl'],
            "technical": old_ring['tech'],
            "dirty_tactics": 50  # Default
        },

        "defense": {
            "strike_defense": old_ring['psych'] - 5,
            "grapple_defense": old_ring['tech'] - 5,
            "aerial_defense": old_ring['psych'] - 10,
            "ring_awareness": old_ring['psych']
        },

        "entertainment": {
            "mic_skills": old_ent['mic'],
            "charisma": old_ent['charisma'],
            "look": old_ent['look'],
            "star_power": old_ent['star_quality'],
            "entrance": old_ent['charisma']  # Default to charisma
        },

        "intangibles": {
            "psychology": old_ring['psych'],
            "consistency": 75,  # Default
            "big_match": old_ent['star_quality'] - 5,
            "clutch": 70  # Default
        },

        "styles": {
            "primary": determine_style(old_ring),  # Function to guess style
            "secondary": None
        },

        "moves": {
            "finishers": [],
            "signatures": []
        },

        "status": old_data['status']
    }
```

---

### UI Changes Required

#### 1. Wrestler Profile Page (`wrestler.html`)
- Display stats in categorized sections (Physical, Offense, Defense, etc.)
- Show fighting style badges
- Display finisher and signature moves
- Handle optional nickname display

#### 2. Create Wrestler Form (`create_wrestler.html`)
- Add all new attribute sliders organized by category
- Add fighting style dropdowns
- Add finisher/signature move inputs
- Mark nickname as "(Optional)"
- Add height/weight inputs

#### 3. Roster View (`roster.html`)
- Show primary fighting style badge
- Display condensed stat overview
- Handle wrestlers without nicknames

#### 4. Booking Page (`booking.html`)
- Show style matchup indicators (e.g., "Technical vs High Flyer")
- Display key stats relevant to match type

---

### Files to Modify

1. `src/core/wrestler.py` - Complete rewrite of Wrestler class
2. `src/core/match.py` - Update match simulation logic
3. `src/services/game_service.py` - Update wrestler creation
4. `src/ui/web/templates/wrestler.html` - New stat display
5. `src/ui/web/templates/create_wrestler.html` - New form fields
6. `src/ui/web/templates/roster.html` - Updated cards
7. `src/ui/web/templates/booking.html` - Style indicators
8. `data/databases/default/wrestlers.json` - Migrate data
9. `src/ui/web/static/css/style.css` - New stat bar styles

---

### Example Wrestler Comparisons

After migration, wrestlers should be clearly differentiated:

**Technical Wrestler (Bret Hart):**
- High: Technical (98), Submission (95), Psychology (98), Consistency (95)
- Medium: Striking (80), Grappling (88), Durability (85)
- Low: High Flying (70), Dirty Tactics (45), Hardcore (55)

**High Flyer (Shawn Michaels):**
- High: High Flying (95), Agility (92), Speed (90), Charisma (98)
- Medium: Technical (85), Striking (78), Star Power (98)
- Low: Strength (65), Power Moves (60), Submission (70)

**Powerhouse (Diesel):**
- High: Strength (92), Power Moves (90), Durability (88), Look (92)
- Medium: Striking (78), Grappling (75), Intimidation (85)
- Low: Speed (55), Agility (45), High Flying (20), Technical (55)

**Brawler (Big Boss Man):**
- High: Striking (85), Brawling (88), Durability (82), Hardcore (75)
- Medium: Strength (80), Stamina (80), Grappling (70)
- Low: Technical (55), High Flying (30), Submission (45)

---

### Summary of Changes

| Area | Current | New |
|------|---------|-----|
| Total Attributes | 9 | 27 |
| Attribute Categories | 2 | 5 |
| Nickname | Required | Optional |
| Fighting Styles | None | 10 options |
| Special Moves | None | Finishers + Signatures |
| Physical Stats | 1 (stamina) | 6 |
| Offensive Stats | 4 | 8 |
| Defensive Stats | 0 | 4 |
| Entertainment Stats | 4 | 5 |
| Intangibles | 0 | 4 |

This overhaul will make each wrestler feel unique and create more strategic depth in match booking and simulation.
