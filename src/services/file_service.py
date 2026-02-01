import os
import shutil
import json # Import json
from pathlib import Path
from typing import List, Tuple, Dict, Any


def get_project_root() -> Path:
    """Get the project root directory (parent of src/)."""
    return Path(__file__).parent.parent.parent


def get_databases_path() -> Path:
    """Get the path to the databases directory."""
    return get_project_root() / "data" / "databases"


def get_saves_path() -> Path:
    """Get the path to the saves directory."""
    return get_project_root() / "saves"


def list_databases() -> List[str]:
    """
    Scans the data/databases folder for available mods.
    Returns a list of database folder names.
    """
    path = get_databases_path()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return []
    return [d.name for d in path.iterdir() if d.is_dir()]


def list_saves() -> List[str]:
    """
    Scans the saves folder for existing game sessions.
    Returns a list of save folder names.
    """
    path = get_saves_path()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return []
    return [d.name for d in path.iterdir() if d.is_dir()]


def create_new_save(db_name: str, save_name: str) -> Tuple[bool, str]:
    """
    Creates a new save by copying a database template.
    Returns (success, message).
    """
    src = get_databases_path() / db_name
    dst = get_saves_path() / save_name

    if not src.exists():
        return False, f"Database '{db_name}' not found."

    if dst.exists():
        return False, f"Save name '{save_name}' already exists."

    try:
        shutil.copytree(src, dst)
        # Initialize an empty game_state.json
        save_game_state_data(save_name, {'year': 1, 'month': 1, 'week': 1})
        # Initialize an empty company.json
        save_company_data(save_name, {'bank_account': 500000, 'prestige': 50, 'viewers': 1000000})
        return True, f"Created universe '{save_name}' from '{db_name}'."
    except Exception as e:
        return False, str(e)


def get_save_path(save_name: str) -> Path:
    """Get the full path for a save folder."""
    return get_saves_path() / save_name


def get_roster_path(save_name: str) -> Path:
    """Get the path to the wrestlers.json file for a save."""
    return get_save_path(save_name) / "wrestlers.json"


def get_tag_teams_path(save_name: str) -> Path:
    """Get the path to the tag_teams.json file for a save."""
    return get_save_path(save_name) / "tag_teams.json"

def get_titles_path(save_name: str) -> Path:
    """Get the path to the titles.json file for a save."""
    return get_save_path(save_name) / "titles.json"


def get_feuds_path(save_name: str) -> Path:
    """Get the path to the feuds.json file for a save."""
    return get_save_path(save_name) / "feuds.json"


def get_stables_path(save_name: str) -> Path:
    """Get the path to the stables.json file for a save."""
    return get_save_path(save_name) / "stables.json"


def get_game_state_path(save_name: str) -> Path:
    """Get the path to the game_state.json file for a save."""
    return get_save_path(save_name) / "game_state.json"

def get_company_path(save_name: str) -> Path:
    """Get the path to the company.json file for a save."""
    return get_save_path(save_name) / "company.json"


def get_records_path(save_name: str) -> Path:
    """Get the path to the records.json file for a save."""
    return get_save_path(save_name) / "records.json"


def get_calendar_path(save_name: str) -> Path:
    """Get the path to the calendar.json file for a save."""
    return get_save_path(save_name) / "calendar.json"


def get_brands_path(save_name: str) -> Path:
    """Get the path to the brands.json file for a save."""
    return get_save_path(save_name) / "brands.json"


def get_weekly_shows_path(save_name: str) -> Path:
    """Get the path to the weekly_shows.json file for a save."""
    return get_save_path(save_name) / "weekly_shows.json"


def get_news_path(save_name: str) -> Path:
    """Get the path to the news.json file for a save."""
    return get_save_path(save_name) / "news.json"


def save_exists(save_name: str) -> bool:
    """Check if a save folder exists."""
    return get_save_path(save_name).exists()


def database_exists(db_name: str) -> bool:
    """Check if a database folder exists."""
    return (get_databases_path() / db_name).exists()


def load_game_state_data(save_name: str) -> Dict[str, Any]:
    """Loads game state data from game_state.json."""
    path = get_game_state_path(save_name)
    if not path.exists():
        return {'year': 1, 'month': 1, 'week': 1} # Default state
    
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {'year': 1, 'month': 1, 'week': 1} # Default on corrupt file


def save_game_state_data(save_name: str, data: Dict[str, Any]) -> None:
    """Saves game state data to game_state.json."""
    path = get_game_state_path(save_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_company_data(save_name: str) -> Dict[str, Any]:
    """Loads company data from company.json."""
    path = get_company_path(save_name)
    if not path.exists():
        return {'bank_account': 500000, 'prestige': 50, 'viewers': 1000000} # Default state
    
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {'bank_account': 500000, 'prestige': 50, 'viewers': 1000000} # Default on corrupt file

def save_company_data(save_name: str, data: Dict[str, Any]) -> None:
    """Saves company data to company.json."""
    path = get_company_path(save_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def load_records_data(save_name: str) -> Dict[str, Any]:
    """Loads records data from records.json."""
    path = get_records_path(save_name)
    if not path.exists():
        # Return empty structure for new saves
        return {
            "match_history": [],
            "wrestler_records": {},
            "title_reigns": [],
            "_next_match_id": 1,
            "_next_reign_id": 1,
        }

    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Return empty structure on corrupt file
            return {
                "match_history": [],
                "wrestler_records": {},
                "title_reigns": [],
                "_next_match_id": 1,
                "_next_reign_id": 1,
            }


def save_records_data(save_name: str, data: Dict[str, Any]) -> None:
    """Saves records data to records.json."""
    path = get_records_path(save_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def load_calendar_data(save_name: str) -> Dict[str, Any]:
    """Loads calendar data from calendar.json."""
    path = get_calendar_path(save_name)
    if not path.exists():
        # Return empty structure for new saves
        return {
            'brands': [],
            'weekly_shows': [],
            'scheduled_shows': [],
            'ppv_calendar': [],
            '_next_show_id': 1,
        }

    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {
                'brands': [],
                'weekly_shows': [],
                'scheduled_shows': [],
                'ppv_calendar': [],
                '_next_show_id': 1,
            }


def save_calendar_data(save_name: str, data: Dict[str, Any]) -> None:
    """Saves calendar data to calendar.json."""
    path = get_calendar_path(save_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def load_news_data(save_name: str) -> Dict[str, Any]:
    """Loads news data from news.json."""
    path = get_news_path(save_name)
    if not path.exists():
        # Return empty structure for new saves
        return {
            'feed_entries': [],
            '_next_id': 1,
        }

    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {
                'feed_entries': [],
                '_next_id': 1,
            }


def save_news_data(save_name: str, data: Dict[str, Any]) -> None:
    """Saves news data to news.json."""
    path = get_news_path(save_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)