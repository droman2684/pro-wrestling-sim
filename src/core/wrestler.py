import json
import os
import random
from enum import Enum
from typing import List, Optional, Dict, Any
from core.economy import Contract


class FightingStyle(Enum):
    """Fighting styles that affect how wrestlers perform in matches."""
    POWERHOUSE = "powerhouse"           # Strength/power moves focused
    TECHNICIAN = "technician"           # Technical wrestling, submissions
    HIGH_FLYER = "high_flyer"           # Aerial moves, speed
    BRAWLER = "brawler"                 # Striking, hardcore
    SHOWMAN = "showman"                 # Entertainment, crowd work
    SUBMISSION_SPECIALIST = "submission"  # Locks and holds
    ALL_ROUNDER = "all_rounder"         # Balanced across all areas
    GIANT = "giant"                     # Size-based offense, durability
    HARDCORE = "hardcore"               # Extreme/weapon specialist
    STRIKER = "striker"                 # MMA-style striking


class Wrestler:
    """
    Represents a single wrestler with WWE 2K-style attributes.

    Attributes are organized into 5 categories:
    - Physical (6): strength, speed, agility, durability, stamina, recovery
    - Offense (8): striking, grappling, submission, high_flying, hardcore, power_moves, technical, dirty_tactics
    - Defense (4): strike_defense, grapple_defense, aerial_defense, ring_awareness
    - Entertainment (5): mic_skills, charisma, look, star_power, entrance
    - Intangibles (4): psychology, consistency, big_match, clutch
    """

    def __init__(self, data: dict):
        # Identity
        self.id = data['id']
        self.name = data['name']
        self.nickname = data.get('nickname', None)  # Optional - can be None/empty
        self.billing_name = data.get('billing_name', None)  # Optional (e.g., "The Phenomenal AJ Styles")

        # Bio
        bio = data.get('bio', {})
        self.age = bio.get('age', 25)
        self.height = bio.get('height', 72)  # inches
        self.weight = bio.get('weight', 220)  # pounds
        self.region = bio.get('home_region', 'Unknown')
        self.years_active = bio.get('years_active', 1)

        # Check if using new format or legacy format
        if 'physical' in data:
            self._load_new_format(data)
        else:
            self._load_legacy_format(data)

        # Fighting Styles
        styles = data.get('styles', {})
        self.primary_style = styles.get('primary', 'all_rounder')
        self.secondary_style = styles.get('secondary', None)

        # Special Moves
        moves = data.get('moves', {})
        self.finishers = moves.get('finishers', [])
        self.signatures = moves.get('signatures', [])
        self.taunts = moves.get('taunts', [])

        # Dynamic Status
        status = data.get('status', {})
        self.morale = status.get('morale', 75)
        self.condition = status.get('condition', 100)
        self.alignment = status.get('alignment', 'Face')
        self.heat = status.get('heat', 50)
        self.wins = status.get('wins', 0)
        self.losses = status.get('losses', 0)
        self.has_mitb_briefcase = status.get('has_mitb_briefcase', False)
        self.is_injured = status.get('is_injured', False)
        self.injury_weeks_remaining = status.get('injury_weeks_remaining', 0)

        # Contract
        self.contract = Contract(**data.get('contract', {}))

    def _load_new_format(self, data: dict) -> None:
        """Load wrestler from new 27-attribute format."""
        # Physical Attributes (6)
        physical = data.get('physical', {})
        self.strength = physical.get('strength', 50)
        self.speed = physical.get('speed', 50)
        self.agility = physical.get('agility', 50)
        self.durability = physical.get('durability', 50)
        self.stamina = physical.get('stamina', 100)
        self.recovery = physical.get('recovery', 50)

        # Offensive Skills (8)
        offense = data.get('offense', {})
        self.striking = offense.get('striking', 50)
        self.grappling = offense.get('grappling', 50)
        self.submission = offense.get('submission', 50)
        self.high_flying = offense.get('high_flying', 50)
        self.hardcore = offense.get('hardcore', 50)
        self.power_moves = offense.get('power_moves', 50)
        self.technical = offense.get('technical', 50)
        self.dirty_tactics = offense.get('dirty_tactics', 50)

        # Defensive Skills (4)
        defense = data.get('defense', {})
        self.strike_defense = defense.get('strike_defense', 50)
        self.grapple_defense = defense.get('grapple_defense', 50)
        self.aerial_defense = defense.get('aerial_defense', 50)
        self.ring_awareness = defense.get('ring_awareness', 50)

        # Entertainment/Presence (5)
        entertainment = data.get('entertainment', {})
        self.mic_skills = entertainment.get('mic_skills', 50)
        self.charisma = entertainment.get('charisma', 50)
        self.look = entertainment.get('look', 50)
        self.star_power = entertainment.get('star_power', 50)
        self.entrance = entertainment.get('entrance', 50)

        # Intangibles (4)
        intangibles = data.get('intangibles', {})
        self.psychology = intangibles.get('psychology', 50)
        self.consistency = intangibles.get('consistency', 75)
        self.big_match = intangibles.get('big_match', 50)
        self.clutch = intangibles.get('clutch', 50)

    def _load_legacy_format(self, data: dict) -> None:
        """Load wrestler from legacy 9-attribute format and convert to new system."""
        # Handle old gimmick_name -> nickname conversion
        if 'gimmick_name' in data and not self.nickname:
            self.nickname = data.get('gimmick_name')

        # Get legacy stats
        old_ring = data.get('stats_ring', {})
        old_ent = data.get('stats_entertainment', {})

        # Legacy ring stats
        old_brawl = old_ring.get('brawl', 50)
        old_tech = old_ring.get('tech', 50)
        old_air = old_ring.get('air', 50)
        old_psych = old_ring.get('psychology', 50)
        old_stamina = old_ring.get('stamina', 100)

        # Legacy entertainment stats
        old_mic = old_ent.get('mic', 50)
        old_charisma = old_ent.get('charisma', 50)
        old_look = old_ent.get('look', 50)
        old_star = old_ent.get('star_quality', 50)

        # Map to new Physical stats
        self.strength = old_brawl
        self.speed = (old_air + old_tech) // 2
        self.agility = old_air
        self.durability = 75  # Default
        self.stamina = old_stamina
        self.recovery = 70  # Default

        # Map to new Offense stats
        self.striking = old_brawl
        self.grappling = (old_brawl + old_tech) // 2
        self.submission = old_tech
        self.high_flying = old_air
        self.hardcore = max(30, old_brawl - 10)
        self.power_moves = old_brawl
        self.technical = old_tech
        self.dirty_tactics = 50  # Default

        # Map to new Defense stats
        self.strike_defense = max(30, old_psych - 5)
        self.grapple_defense = max(30, old_tech - 5)
        self.aerial_defense = max(30, old_psych - 10)
        self.ring_awareness = old_psych

        # Map to new Entertainment stats
        self.mic_skills = old_mic
        self.charisma = old_charisma
        self.look = old_look
        self.star_power = old_star
        self.entrance = old_charisma  # Default to charisma

        # Map to new Intangibles
        self.psychology = old_psych
        self.consistency = 75  # Default
        self.big_match = max(50, old_star - 5)
        self.clutch = 70  # Default

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

    # Legacy property aliases for backward compatibility
    @property
    def gimmick(self) -> str:
        """Legacy alias for nickname (backward compatibility)."""
        return self.nickname or ""

    @property
    def brawl(self) -> int:
        """Legacy alias - maps to striking."""
        return self.striking

    @property
    def tech(self) -> int:
        """Legacy alias - maps to technical."""
        return self.technical

    @property
    def air(self) -> int:
        """Legacy alias - maps to high_flying."""
        return self.high_flying

    @property
    def psych(self) -> int:
        """Legacy alias - maps to psychology."""
        return self.psychology

    @property
    def mic(self) -> int:
        """Legacy alias - maps to mic_skills."""
        return self.mic_skills

    def get_overall_rating(self) -> int:
        """
        Calculates overall rating using weighted category averages.

        Weights:
        - Physical: 20%
        - Offense: 30%
        - Defense: 15%
        - Entertainment: 20%
        - Intangibles: 15%
        """
        # Physical (20% of overall)
        physical_avg = (
            self.strength + self.speed + self.agility +
            self.durability + self.stamina + self.recovery
        ) / 6

        # Offense (30% of overall) - excludes hardcore and dirty_tactics
        offense_avg = (
            self.striking + self.grappling + self.submission +
            self.high_flying + self.power_moves + self.technical
        ) / 6

        # Defense (15% of overall)
        defense_avg = (
            self.strike_defense + self.grapple_defense +
            self.aerial_defense + self.ring_awareness
        ) / 4

        # Entertainment (20% of overall) - excludes entrance
        entertainment_avg = (
            self.mic_skills + self.charisma + self.look + self.star_power
        ) / 4

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

    def get_workrate(self) -> int:
        """Calculate in-ring work rate for match quality."""
        return int((self.striking + self.technical + self.high_flying + self.grappling) / 4)

    def get_entertainment_value(self) -> int:
        """Calculate entertainment/promo value."""
        return int((self.mic_skills + self.charisma + self.star_power) / 3)

    def get_style_enum(self) -> Optional[FightingStyle]:
        """Get the primary fighting style as enum."""
        try:
            return FightingStyle(self.primary_style)
        except ValueError:
            return FightingStyle.ALL_ROUNDER

    def get_primary_finisher(self) -> Optional[Dict]:
        """Get the primary (first) finisher move."""
        if self.finishers:
            return self.finishers[0]
        return None

    def get_tier(self) -> str:
        """Get wrestler's tier based on overall rating."""
        rating = self.get_overall_rating()
        if rating >= 95:
            return "Legend"
        elif rating >= 90:
            return "Elite"
        elif rating >= 85:
            return "Main Eventer"
        elif rating >= 80:
            return "Upper Midcard"
        elif rating >= 75:
            return "Midcard"
        elif rating >= 70:
            return "Lower Midcard"
        elif rating >= 65:
            return "Jobber"
        elif rating >= 60:
            return "Rookie"
        else:
            return "Local Talent"

    def update_after_match(self, is_winner: bool, match_rating: int, duration_cost: int = 10) -> None:
        """Adjusts stats based on the match result and updates win/loss record."""
        # Update win/loss record
        if is_winner:
            self.wins += 1
        else:
            self.losses += 1

        # Stamina Drain
        self.stamina = max(0, self.stamina - duration_cost)

        # Condition Drain (long-term wear and tear)
        # High durability reduces condition loss, low durability increases it
        durability_modifier = 1.5 - (self.durability / 100)  # 1.5 at dur=0, 0.5 at dur=100
        condition_cost = int((duration_cost * 0.4) * durability_modifier)
        condition_cost = max(1, condition_cost)
        self.condition = max(0, self.condition - condition_cost)

        # Morale & Heat Changes
        if is_winner:
            self.morale = min(100, self.morale + 5)
            heat_gain = int(match_rating / 10)
            self.heat = min(100, self.heat + heat_gain)
        else:
            self.morale = max(0, self.morale - 3)
            if match_rating > 80:
                self.heat = min(100, self.heat + 2)
            else:
                self.heat = max(0, self.heat - 2)

        # Check for injury risk
        self.check_injury_risk()

    def recover_stamina(self, amount: int = 20) -> None:
        """Recover stamina between shows based on recovery stat."""
        recovery_bonus = self.recovery / 100  # 0.0 to 1.0
        actual_recovery = int(amount * (1 + recovery_bonus))
        self.stamina = min(100, self.stamina + actual_recovery)

    def check_injury_risk(self) -> bool:
        """
        Check if wrestler gets injured after a match.
        Only triggers when condition < 25. Returns True if injury occurred.
        """
        if self.condition >= 25 or self.is_injured:
            return False

        # Base injury chance: 2% at condition=24, up to 50% at condition=0
        base_chance = (25 - self.condition) * 2

        # Durability modifier: halves chance at 100, doubles at 0
        durability_factor = 2.0 - (self.durability / 50)
        durability_factor = max(0.25, durability_factor)

        injury_chance = base_chance * durability_factor

        if random.randint(1, 100) <= int(injury_chance):
            self.is_injured = True
            max_weeks = max(2, 8 - int(self.durability / 20))  # 8 at dur=0, 3 at dur=100
            self.injury_weeks_remaining = random.randint(2, max_weeks)
            return True
        return False

    def to_dict(self) -> dict:
        """Converts object back to new JSON format for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "billing_name": self.billing_name,

            "bio": {
                "age": self.age,
                "height": self.height,
                "weight": self.weight,
                "home_region": self.region,
                "years_active": self.years_active
            },

            "physical": {
                "strength": self.strength,
                "speed": self.speed,
                "agility": self.agility,
                "durability": self.durability,
                "stamina": self.stamina,
                "recovery": self.recovery
            },

            "offense": {
                "striking": self.striking,
                "grappling": self.grappling,
                "submission": self.submission,
                "high_flying": self.high_flying,
                "hardcore": self.hardcore,
                "power_moves": self.power_moves,
                "technical": self.technical,
                "dirty_tactics": self.dirty_tactics
            },

            "defense": {
                "strike_defense": self.strike_defense,
                "grapple_defense": self.grapple_defense,
                "aerial_defense": self.aerial_defense,
                "ring_awareness": self.ring_awareness
            },

            "entertainment": {
                "mic_skills": self.mic_skills,
                "charisma": self.charisma,
                "look": self.look,
                "star_power": self.star_power,
                "entrance": self.entrance
            },

            "intangibles": {
                "psychology": self.psychology,
                "consistency": self.consistency,
                "big_match": self.big_match,
                "clutch": self.clutch
            },

            "styles": {
                "primary": self.primary_style,
                "secondary": self.secondary_style
            },

            "moves": {
                "finishers": self.finishers,
                "signatures": self.signatures,
                "taunts": self.taunts
            },

            "status": {
                "morale": self.morale,
                "condition": self.condition,
                "alignment": self.alignment,
                "heat": self.heat,
                "wins": self.wins,
                "losses": self.losses,
                "has_mitb_briefcase": self.has_mitb_briefcase,
                "is_injured": self.is_injured,
                "injury_weeks_remaining": self.injury_weeks_remaining
            },

            "contract": self.contract.to_dict()
        }

    def __str__(self) -> str:
        return f"[{self.get_overall_rating()}] {self.display_name} W:{self.wins} L:{self.losses}"


def determine_style_from_stats(strength: int, technical: int, high_flying: int,
                                striking: int, submission: int) -> str:
    """Determine the best fighting style based on stats."""
    # Find highest stats to determine style
    stats = {
        'powerhouse': strength,
        'technician': technical,
        'high_flyer': high_flying,
        'brawler': striking,
        'submission': submission
    }

    max_stat = max(stats.values())

    # If stats are balanced (within 15 points of each other), go all-rounder
    if max_stat - min(stats.values()) <= 15:
        return 'all_rounder'

    # Return the style with highest stat
    for style, value in stats.items():
        if value == max_stat:
            return style

    return 'all_rounder'


def load_roster(filepath: str) -> List[Wrestler]:
    """Load roster from JSON file."""
    roster = []
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r') as f:
        data = json.load(f)
        for w_data in data:
            roster.append(Wrestler(w_data))

    return roster


def save_roster(roster_list: List[Wrestler], filepath: str) -> None:
    """Writes the current roster state back to the JSON file."""
    data = [w.to_dict() for w in roster_list]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def migrate_legacy_wrestler(old_data: dict) -> dict:
    """
    Convert old wrestler format to new format.
    Used for migrating existing save files.
    """
    old_ring = old_data.get('stats_ring', {})
    old_ent = old_data.get('stats_entertainment', {})
    old_status = old_data.get('status', {})
    old_bio = old_data.get('bio', {})

    # Legacy ring stats
    old_brawl = old_ring.get('brawl', 50)
    old_tech = old_ring.get('tech', 50)
    old_air = old_ring.get('air', 50)
    old_psych = old_ring.get('psychology', 50)
    old_stamina = old_ring.get('stamina', 100)

    # Legacy entertainment stats
    old_mic = old_ent.get('mic', 50)
    old_charisma = old_ent.get('charisma', 50)
    old_look = old_ent.get('look', 50)
    old_star = old_ent.get('star_quality', 50)

    # Determine fighting style from old stats
    primary_style = determine_style_from_stats(
        old_brawl, old_tech, old_air, old_brawl, old_tech
    )

    return {
        "id": old_data['id'],
        "name": old_data['name'],
        "nickname": old_data.get('gimmick_name', None),
        "billing_name": None,

        "bio": {
            "age": old_bio.get('age', 25),
            "height": 72,  # Default 6'0"
            "weight": 220,  # Default
            "home_region": old_bio.get('home_region', 'Unknown'),
            "years_active": 5  # Default
        },

        "physical": {
            "strength": old_brawl,
            "speed": (old_air + old_tech) // 2,
            "agility": old_air,
            "durability": 75,
            "stamina": old_stamina,
            "recovery": 70
        },

        "offense": {
            "striking": old_brawl,
            "grappling": (old_brawl + old_tech) // 2,
            "submission": old_tech,
            "high_flying": old_air,
            "hardcore": max(30, old_brawl - 10),
            "power_moves": old_brawl,
            "technical": old_tech,
            "dirty_tactics": 50
        },

        "defense": {
            "strike_defense": max(30, old_psych - 5),
            "grapple_defense": max(30, old_tech - 5),
            "aerial_defense": max(30, old_psych - 10),
            "ring_awareness": old_psych
        },

        "entertainment": {
            "mic_skills": old_mic,
            "charisma": old_charisma,
            "look": old_look,
            "star_power": old_star,
            "entrance": old_charisma
        },

        "intangibles": {
            "psychology": old_psych,
            "consistency": 75,
            "big_match": max(50, old_star - 5),
            "clutch": 70
        },

        "styles": {
            "primary": primary_style,
            "secondary": None
        },

        "moves": {
            "finishers": [],
            "signatures": []
        },

        "status": {
            "morale": old_status.get('morale', 75),
            "condition": old_status.get('condition', 100),
            "alignment": old_status.get('alignment', 'Face'),
            "heat": old_status.get('heat', 50),
            "wins": old_status.get('wins', 0),
            "losses": old_status.get('losses', 0),
            "has_mitb_briefcase": old_status.get('has_mitb_briefcase', False),
            "is_injured": False,
            "injury_weeks_remaining": 0
        },

        "contract": old_data.get('contract', {"per_appearance_fee": 1000})
    }
