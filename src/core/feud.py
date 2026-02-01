"""Feud system for managing wrestler rivalries and storylines."""
import json
import os
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.wrestler import Wrestler


# Intensity levels with their rating bonuses
INTENSITY_BONUSES = {
    "heated": 3,
    "intense": 6,
    "blood": 10
}


@dataclass
class Feud:
    """Represents a feud/rivalry between two wrestlers."""
    id: int
    wrestler_a_id: int
    wrestler_b_id: int
    intensity: str = "heated"  # heated (+3), intense (+6), blood (+10)
    matches_remaining: int = 3  # Auto-resolve countdown
    total_matches: int = 0
    wins_a: int = 0
    wins_b: int = 0
    is_active: bool = True
    blowoff_match_scheduled: bool = False

    def get_intensity_bonus(self) -> int:
        """Returns the match rating bonus based on feud intensity."""
        return INTENSITY_BONUSES.get(self.intensity, 3)

    def get_participants(self, roster: List['Wrestler']) -> tuple:
        """
        Get the wrestler objects for both participants.
        Returns (wrestler_a, wrestler_b) tuple.
        """
        wrestler_a = None
        wrestler_b = None
        for wrestler in roster:
            if wrestler.id == self.wrestler_a_id:
                wrestler_a = wrestler
            elif wrestler.id == self.wrestler_b_id:
                wrestler_b = wrestler
        return (wrestler_a, wrestler_b)

    def involves_wrestler(self, wrestler_id: int) -> bool:
        """Check if a wrestler is involved in this feud."""
        return wrestler_id in (self.wrestler_a_id, self.wrestler_b_id)

    def record_match(self, winner_id: int) -> bool:
        """
        Record a match result in this feud.
        Updates score, decrements remaining matches.
        Returns True if the feud has ended.
        """
        self.total_matches += 1

        if winner_id == self.wrestler_a_id:
            self.wins_a += 1
        elif winner_id == self.wrestler_b_id:
            self.wins_b += 1

        self.matches_remaining -= 1

        # Intensity escalation based on total matches
        if self.total_matches >= 4:
            self.intensity = "blood"
        elif self.total_matches >= 2:
            self.intensity = "intense"

        # Check if feud ends
        if self.blowoff_match_scheduled or self.matches_remaining <= 0:
            self.is_active = False
            return True

        return False

    def get_score_string(self) -> str:
        """Returns the current score as a formatted string."""
        return f"{self.wins_a}-{self.wins_b}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "wrestler_a_id": self.wrestler_a_id,
            "wrestler_b_id": self.wrestler_b_id,
            "intensity": self.intensity,
            "matches_remaining": self.matches_remaining,
            "total_matches": self.total_matches,
            "wins_a": self.wins_a,
            "wins_b": self.wins_b,
            "is_active": self.is_active,
            "blowoff_match_scheduled": self.blowoff_match_scheduled
        }

    def __str__(self) -> str:
        status = "ACTIVE" if self.is_active else "ENDED"
        return f"Feud ({self.intensity.upper()}) - Score: {self.get_score_string()} [{status}]"


def load_feuds(filepath: str) -> List[Feud]:
    """Load feuds from JSON file."""
    feuds = []
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r') as f:
        data = json.load(f)
        for feud_data in data:
            feuds.append(Feud(
                id=feud_data['id'],
                wrestler_a_id=feud_data['wrestler_a_id'],
                wrestler_b_id=feud_data['wrestler_b_id'],
                intensity=feud_data.get('intensity', 'heated'),
                matches_remaining=feud_data.get('matches_remaining', 3),
                total_matches=feud_data.get('total_matches', 0),
                wins_a=feud_data.get('wins_a', 0),
                wins_b=feud_data.get('wins_b', 0),
                is_active=feud_data.get('is_active', True),
                blowoff_match_scheduled=feud_data.get('blowoff_match_scheduled', False)
            ))

    return feuds


def save_feuds(feuds: List[Feud], filepath: str) -> None:
    """Save feuds to JSON file."""
    data = [feud.to_dict() for feud in feuds]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
