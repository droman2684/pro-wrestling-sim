"""
Brand System
Handles roster splits and brand-exclusive content.
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.wrestler import Wrestler
    from core.title import Title


@dataclass
class Brand:
    """A brand/roster split (like Raw vs SmackDown)."""
    id: int
    name: str                           # "Monday Night Raw", "Thursday Nitro"
    short_name: str                     # "Raw", "Nitro"
    color: str                          # Hex color for UI (#FF0000)
    assigned_titles: List[int] = field(default_factory=list)    # Title IDs exclusive to this brand
    assigned_wrestlers: List[int] = field(default_factory=list) # Wrestler IDs on this brand
    is_active: bool = True

    def get_roster(self, all_wrestlers: List['Wrestler']) -> List['Wrestler']:
        """Get wrestlers assigned to this brand."""
        return [w for w in all_wrestlers if w.id in self.assigned_wrestlers]

    def get_titles(self, all_titles: List['Title']) -> List['Title']:
        """Get titles assigned to this brand."""
        return [t for t in all_titles if t.id in self.assigned_titles]

    def get_roster_count(self) -> int:
        """Get number of wrestlers assigned."""
        return len(self.assigned_wrestlers)

    def get_title_count(self) -> int:
        """Get number of titles assigned."""
        return len(self.assigned_titles)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'color': self.color,
            'assigned_titles': list(self.assigned_titles),
            'assigned_wrestlers': list(self.assigned_wrestlers),
            'is_active': self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Brand':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            short_name=data['short_name'],
            color=data['color'],
            assigned_titles=data.get('assigned_titles', []),
            assigned_wrestlers=data.get('assigned_wrestlers', []),
            is_active=data.get('is_active', True),
        )


@dataclass
class TitleAssignment:
    """Links a title to a brand."""
    title_id: int
    brand_id: int
    assigned_date: dict                 # {year, month, week}
    is_exclusive: bool = True           # Can only be defended on this brand's shows

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'title_id': self.title_id,
            'brand_id': self.brand_id,
            'assigned_date': self.assigned_date,
            'is_exclusive': self.is_exclusive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TitleAssignment':
        """Create from dictionary."""
        return cls(
            title_id=data['title_id'],
            brand_id=data['brand_id'],
            assigned_date=data.get('assigned_date', {}),
            is_exclusive=data.get('is_exclusive', True),
        )


@dataclass
class WrestlerAssignment:
    """Links a wrestler to a brand."""
    wrestler_id: int
    brand_id: int
    assigned_date: dict                 # {year, month, week}
    is_free_agent: bool = False         # Can appear on any show

    # Draft/Trade history
    previous_brands: List[dict] = field(default_factory=list)
    # [{brand_id, start_date, end_date}, ...]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'wrestler_id': self.wrestler_id,
            'brand_id': self.brand_id,
            'assigned_date': self.assigned_date,
            'is_free_agent': self.is_free_agent,
            'previous_brands': self.previous_brands,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WrestlerAssignment':
        """Create from dictionary."""
        return cls(
            wrestler_id=data['wrestler_id'],
            brand_id=data['brand_id'],
            assigned_date=data.get('assigned_date', {}),
            is_free_agent=data.get('is_free_agent', False),
            previous_brands=data.get('previous_brands', []),
        )


def load_brands(filepath: str) -> List[Brand]:
    """Load brands from a JSON file."""
    import json
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return [Brand.from_dict(b) for b in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_brands(brands: List[Brand], filepath: str) -> None:
    """Save brands to a JSON file."""
    import json
    with open(filepath, 'w') as f:
        json.dump([b.to_dict() for b in brands], f, indent=4)
