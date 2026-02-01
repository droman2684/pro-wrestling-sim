"""
Weekly Show System
Handles recurring television shows.
"""
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.calendar import DayOfWeek, ShowTier


@dataclass
class WeeklyShow:
    """A recurring weekly television show."""
    id: int
    name: str                           # "Monday Night Raw"
    short_name: str                     # "Raw"
    day_of_week: 'DayOfWeek'            # When it airs
    tier: 'ShowTier'                    # MAJOR or MINOR
    brand_id: Optional[int]             # Associated brand (for brand split)
    arena: str                          # Default arena name
    is_active: bool = True

    # Show configuration
    match_slots: int = 5                # Number of matches per show
    segment_slots: int = 3              # Number of talking segments
    runtime_minutes: int = 120          # 2 hours default

    # Stats tracking
    total_episodes: int = 0
    average_rating: float = 0.0

    def update_stats(self, new_rating: float) -> None:
        """Update show statistics after an episode."""
        self.total_episodes += 1
        # Running average
        if self.total_episodes == 1:
            self.average_rating = new_rating
        else:
            self.average_rating = (
                (self.average_rating * (self.total_episodes - 1) + new_rating)
                / self.total_episodes
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'day_of_week': self.day_of_week.value,
            'tier': self.tier.value,
            'brand_id': self.brand_id,
            'arena': self.arena,
            'is_active': self.is_active,
            'match_slots': self.match_slots,
            'segment_slots': self.segment_slots,
            'runtime_minutes': self.runtime_minutes,
            'total_episodes': self.total_episodes,
            'average_rating': self.average_rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeeklyShow':
        """Create from dictionary."""
        from core.calendar import DayOfWeek, ShowTier

        return cls(
            id=data['id'],
            name=data['name'],
            short_name=data['short_name'],
            day_of_week=DayOfWeek(data['day_of_week']),
            tier=ShowTier(data['tier']),
            brand_id=data.get('brand_id'),
            arena=data.get('arena', 'Various Arenas'),
            is_active=data.get('is_active', True),
            match_slots=data.get('match_slots', 5),
            segment_slots=data.get('segment_slots', 3),
            runtime_minutes=data.get('runtime_minutes', 120),
            total_episodes=data.get('total_episodes', 0),
            average_rating=data.get('average_rating', 0.0),
        )


def load_weekly_shows(filepath: str) -> List[WeeklyShow]:
    """Load weekly shows from a JSON file."""
    import json
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return [WeeklyShow.from_dict(s) for s in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_weekly_shows(shows: List[WeeklyShow], filepath: str) -> None:
    """Save weekly shows to a JSON file."""
    import json
    with open(filepath, 'w') as f:
        json.dump([s.to_dict() for s in shows], f, indent=4)
