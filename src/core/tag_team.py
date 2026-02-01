import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.wrestler import Wrestler


@dataclass
class TagTeam:
    """Represents a tag team with two wrestlers and chemistry mechanics."""
    id: int
    name: str
    member_ids: List[int]
    chemistry: int = 50
    wins: int = 0
    losses: int = 0
    is_active: bool = True

    def get_team_rating(self, roster: List['Wrestler']) -> int:
        """
        Calculate team rating based on member overalls and chemistry.
        Formula: Average of member overalls × chemistry modifier (0.8 to 1.2)
        """
        members = self.get_members(roster)
        if len(members) != 2:
            return 0

        avg_overall = (members[0].get_overall_rating() + members[1].get_overall_rating()) / 2

        # Chemistry modifier: 0.8 at chemistry 0, 1.2 at chemistry 100
        chemistry_modifier = 0.8 + (self.chemistry / 100) * 0.4

        return int(avg_overall * chemistry_modifier)

    def get_members(self, roster: List['Wrestler']) -> List['Wrestler']:
        """Get the wrestler objects for this team's members."""
        members = []
        for wrestler in roster:
            if wrestler.id in self.member_ids:
                members.append(wrestler)
        return members

    def is_available(self, roster: List['Wrestler']) -> bool:
        """Check if team is available (both members healthy and not injured)."""
        if not self.is_active:
            return False

        members = self.get_members(roster)
        if len(members) != 2:
            return False

        return all(member.condition >= 20 and not member.is_injured for member in members)

    def update_after_match(self, is_winner: bool) -> None:
        """Update team chemistry and record after a match."""
        if is_winner:
            self.wins += 1
            # Chemistry grows 1-3 on wins
            import random
            chemistry_gain = random.randint(1, 3)
            self.chemistry = min(100, self.chemistry + chemistry_gain)
        else:
            self.losses += 1
            # Chemistry decreases 1 on losses
            self.chemistry = max(0, self.chemistry - 1)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "member_ids": self.member_ids,
            "chemistry": self.chemistry,
            "wins": self.wins,
            "losses": self.losses,
            "is_active": self.is_active
        }

    def __str__(self) -> str:
        return f"{self.name} (Chemistry: {self.chemistry})"


def load_tag_teams(filepath: str) -> List[TagTeam]:
    """Load tag teams from JSON file."""
    teams = []
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r') as f:
        data = json.load(f)
        for team_data in data:
            teams.append(TagTeam(
                id=team_data['id'],
                name=team_data['name'],
                member_ids=team_data['member_ids'],
                chemistry=team_data.get('chemistry', 50),
                wins=team_data.get('wins', 0),
                losses=team_data.get('losses', 0),
                is_active=team_data.get('is_active', True)
            ))

    return teams


def save_tag_teams(teams: List[TagTeam], filepath: str) -> None:
    """Save tag teams to JSON file."""
    data = [team.to_dict() for team in teams]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
