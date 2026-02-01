"""
Stable module for managing wrestling factions/stables.

A stable is a group of 3+ wrestlers with a designated leader.
Stables provide shared heat effects and match interference mechanics.
"""
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.wrestler import Wrestler


@dataclass
class Stable:
    """
    Represents a wrestling stable/faction.

    Stables are groups of 3+ wrestlers with a designated leader.
    Members share heat gains/losses and can interfere in matches.
    """
    id: int
    name: str
    leader_id: int
    member_ids: List[int]  # Includes leader
    is_active: bool = True

    def get_members(self, roster: List['Wrestler']) -> List['Wrestler']:
        """Get the wrestler objects for all stable members."""
        members = []
        for wrestler in roster:
            if wrestler.id in self.member_ids:
                members.append(wrestler)
        return members

    def get_leader(self, roster: List['Wrestler']) -> Optional['Wrestler']:
        """Get the leader wrestler object."""
        for wrestler in roster:
            if wrestler.id == self.leader_id:
                return wrestler
        return None

    def get_power_rating(self, roster: List['Wrestler']) -> int:
        """
        Calculate stable power rating.
        Power rating is the average overall rating of all members.
        """
        members = self.get_members(roster)
        if not members:
            return 0

        total = sum(member.get_overall_rating() for member in members)
        return int(total / len(members))

    def get_non_participant_members(self, participant_id: int, roster: List['Wrestler']) -> List['Wrestler']:
        """Get stable members who are NOT the participant (for interference)."""
        members = []
        for wrestler in roster:
            if wrestler.id in self.member_ids and wrestler.id != participant_id:
                members.append(wrestler)
        return members

    def add_member(self, wrestler_id: int) -> bool:
        """
        Add a wrestler to the stable.
        Returns True if successful, False if already a member.
        """
        if wrestler_id in self.member_ids:
            return False
        self.member_ids.append(wrestler_id)
        return True

    def remove_member(self, wrestler_id: int) -> bool:
        """
        Remove a wrestler from the stable.
        Returns True if successful, False if not a member or would leave < 3 members.
        """
        if wrestler_id not in self.member_ids:
            return False
        if len(self.member_ids) <= 3:
            return False  # Must maintain minimum of 3 members

        self.member_ids.remove(wrestler_id)

        # If leader was removed, assign new leader
        if wrestler_id == self.leader_id and self.member_ids:
            self.leader_id = self.member_ids[0]

        return True

    def set_leader(self, wrestler_id: int) -> bool:
        """
        Set a new leader for the stable.
        Returns True if successful, False if wrestler not a member.
        """
        if wrestler_id not in self.member_ids:
            return False
        self.leader_id = wrestler_id
        return True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "is_active": self.is_active
        }

    def __str__(self) -> str:
        return f"{self.name} ({len(self.member_ids)} members)"


def load_stables(filepath: str) -> List[Stable]:
    """Load stables from JSON file."""
    stables = []
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r') as f:
        data = json.load(f)
        for stable_data in data:
            stables.append(Stable(
                id=stable_data['id'],
                name=stable_data['name'],
                leader_id=stable_data['leader_id'],
                member_ids=stable_data['member_ids'],
                is_active=stable_data.get('is_active', True)
            ))

    return stables


def save_stables(stables: List[Stable], filepath: str) -> None:
    """Save stables to JSON file."""
    data = [stable.to_dict() for stable in stables]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
