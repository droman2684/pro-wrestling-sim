from dataclasses import dataclass
from typing import Optional

@dataclass
class Title:
    """Represents a championship title."""
    id: int
    name: str
    prestige: int
    current_holder_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Converts object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "prestige": self.prestige,
            "current_holder_id": self.current_holder_id
        }

def load_titles(filepath: str) -> list['Title']:
    """Loads titles from a JSON file."""
    import json
    import os

    titles = []
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r') as f:
        data = json.load(f)
        for t_data in data:
            titles.append(Title(**t_data))
    
    return titles

def save_titles(titles: list['Title'], filepath: str) -> None:
    """Saves titles to a JSON file."""
    import json
    data = [t.to_dict() for t in titles]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
