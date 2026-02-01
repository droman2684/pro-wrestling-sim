from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING
from core.economy import Company
from core.records import RecordsManager
from core.calendar import CalendarManager
from core.news_feed import NewsFeedManager

if TYPE_CHECKING:
    from core.title import Title
    from core.feud import Feud
    from core.stable import Stable
    from core.brand import Brand
    from core.weekly_show import WeeklyShow

@dataclass
class GameState:
    """
    Encapsulates the current game session state.
    Replaces global variables from main.py.
    """
    save_name: str = ""
    save_path: str = ""
    roster: List = field(default_factory=list)
    tag_teams: List = field(default_factory=list)
    titles: List['Title'] = field(default_factory=list)
    feuds: List['Feud'] = field(default_factory=list)
    stables: List['Stable'] = field(default_factory=list)
    company: Company = field(default_factory=Company)
    records: RecordsManager = field(default_factory=RecordsManager)
    calendar_manager: CalendarManager = field(default_factory=CalendarManager)
    news_feed: NewsFeedManager = field(default_factory=NewsFeedManager)
    year: int = 1
    month: int = 1
    week: int = 1

    @property
    def is_loaded(self) -> bool:
        return bool(self.save_path and self.roster)
    
    @property
    def date_string(self) -> str:
        return f"Year {self.year}, Month {self.month}, Week {self.week}"

    def advance_week(self):
        """Advances the game date by one week and applies recovery."""
        self.week += 1
        if self.week > 4:
            self.week = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

        # Weekly recovery for all wrestlers
        for wrestler in self.roster:
            # Stamina recovery
            wrestler.recover_stamina(amount=20)

            # Condition recovery (slow, long-term) - only if not injured
            if not wrestler.is_injured:
                condition_recovery = 3 + int(wrestler.recovery / 20)  # 3-8 per week
                wrestler.condition = min(100, wrestler.condition + condition_recovery)

            # Injury healing
            if wrestler.is_injured:
                wrestler.injury_weeks_remaining -= 1
                if wrestler.injury_weeks_remaining <= 0:
                    wrestler.is_injured = False
                    wrestler.injury_weeks_remaining = 0
                    wrestler.condition = min(wrestler.condition, 50)

    def get_wrestler_by_id(self, wrestler_id: int):
        """Find a wrestler by their ID."""
        for wrestler in self.roster:
            if wrestler.id == wrestler_id:
                return wrestler
        return None

    def get_wrestler_by_name(self, name: str):
        """Find a wrestler by their name."""
        for wrestler in self.roster:
            if wrestler.name.lower() == name.lower():
                return wrestler
        return None

    def get_tag_team_by_id(self, team_id: int):
        """Find a tag team by their ID."""
        for team in self.tag_teams:
            if team.id == team_id:
                return team
        return None

    def is_wrestler_on_team(self, wrestler_id: int) -> bool:
        """Check if a wrestler is on an active tag team."""
        for team in self.tag_teams:
            if team.is_active and wrestler_id in team.member_ids:
                return True
        return False

    def get_wrestler_team(self, wrestler_id: int):
        """Get the active tag team a wrestler is on, if any."""
        for team in self.tag_teams:
            if team.is_active and wrestler_id in team.member_ids:
                return team
        return None

    def get_feud_by_id(self, feud_id: int) -> Optional['Feud']:
        """Find a feud by its ID."""
        for feud in self.feuds:
            if feud.id == feud_id:
                return feud
        return None

    def get_wrestler_feud(self, wrestler_id: int) -> Optional['Feud']:
        """Get the active feud for a wrestler, if any."""
        for feud in self.feuds:
            if feud.is_active and feud.involves_wrestler(wrestler_id):
                return feud
        return None

    def is_wrestler_in_feud(self, wrestler_id: int) -> bool:
        """Check if a wrestler is currently in an active feud."""
        return self.get_wrestler_feud(wrestler_id) is not None

    def get_feud_between(self, wrestler_a_id: int, wrestler_b_id: int) -> Optional['Feud']:
        """Get the active feud between two specific wrestlers, if any."""
        for feud in self.feuds:
            if feud.is_active:
                if feud.involves_wrestler(wrestler_a_id) and feud.involves_wrestler(wrestler_b_id):
                    return feud
        return None

    def get_stable_by_id(self, stable_id: int) -> Optional['Stable']:
        """Find a stable by its ID."""
        for stable in self.stables:
            if stable.id == stable_id:
                return stable
        return None

    def get_wrestler_stable(self, wrestler_id: int) -> Optional['Stable']:
        """Get the active stable a wrestler is in, if any."""
        for stable in self.stables:
            if stable.is_active and wrestler_id in stable.member_ids:
                return stable
        return None

    def is_wrestler_in_stable(self, wrestler_id: int) -> bool:
        """Check if a wrestler is in an active stable."""
        return self.get_wrestler_stable(wrestler_id) is not None


@dataclass
class MatchResult:
    """Result data from a single match simulation."""
    wrestler_a_name: str
    wrestler_b_name: str
    winner_name: str
    loser_name: str
    rating: int
    stars: float
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""
    is_feud_match: bool = False
    feud_intensity: str = ""
    feud_ended: bool = False
    interference_occurred: bool = False
    interference_by: str = ""  # Stable name
    interference_helped: bool = False  # True = helped, False = DQ backfire

    @property
    def summary(self) -> str:
        return f"{self.wrestler_a_name} vs {self.wrestler_b_name} - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class TagMatchResult:
    """Result data from a tag team match simulation."""
    team_a_name: str
    team_b_name: str
    winning_team_name: str
    losing_team_name: str
    pinned_wrestler_name: str
    rating: int
    stars: float
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""

    @property
    def summary(self) -> str:
        return f"{self.team_a_name} vs {self.team_b_name} - Winners: {self.winning_team_name} ({self.stars:.1f} stars)"


@dataclass
class RumbleResult:
    """Result data from a Royal Rumble match."""
    winner_name: str
    eliminations: List[dict]  # List of {wrestler_name, eliminated_by, entry_number, elimination_order}
    rating: int
    stars: float
    commentary: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return f"Royal Rumble - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class MultiManResult:
    """Result data from a multi-man match (Triple Threat, Fatal 4-Way)."""
    match_type: str  # "Triple Threat" or "Fatal 4-Way"
    participant_names: List[str]
    winner_name: str
    loser_names: List[str]  # All non-winners
    pinned_wrestler_name: str  # Who took the pin
    rating: int
    stars: float
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""

    @property
    def summary(self) -> str:
        return f"{self.match_type} - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class LadderMatchResult:
    """Result data from a ladder match."""
    match_type: str  # "Ladder Match", "3-Way Ladder Match", etc.
    participant_names: List[str]
    winner_name: str
    loser_names: List[str]
    rating: int
    stars: float
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""

    @property
    def summary(self) -> str:
        return f"{self.match_type} - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class IronManResult:
    """Result data from an Iron Man match."""
    match_type: str  # "30-Minute Iron Man Match"
    wrestler_a_name: str
    wrestler_b_name: str
    winner_name: str  # Empty if draw
    loser_name: str  # Empty if draw
    is_draw: bool
    falls_a: int
    falls_b: int
    fall_log: List[dict] = field(default_factory=list)
    rating: int = 0
    stars: float = 0.0
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""

    @property
    def summary(self) -> str:
        if self.is_draw:
            return f"{self.match_type} - DRAW {self.falls_a}-{self.falls_b} ({self.stars:.1f} stars)"
        return f"{self.match_type} - {self.winner_name} wins {self.falls_a}-{self.falls_b} ({self.stars:.1f} stars)"


@dataclass
class EliminationChamberResult:
    """Result data from an Elimination Chamber match."""
    match_type: str = "Elimination Chamber"
    participant_names: List[str] = field(default_factory=list)
    winner_name: str = ""
    loser_names: List[str] = field(default_factory=list)
    eliminations: List[dict] = field(default_factory=list)  # {wrestler_name, eliminated_by, entry_number, elimination_order}
    rating: int = 0
    stars: float = 0.0
    commentary: List[str] = field(default_factory=list)
    is_title_match: bool = False
    title_name: str = ""
    title_changed: bool = False
    new_champion_name: str = ""

    @property
    def summary(self) -> str:
        return f"{self.match_type} - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class MoneyInTheBankResult:
    """Result data from a Money in the Bank ladder match."""
    match_type: str = "Money in the Bank"
    participant_names: List[str] = field(default_factory=list)
    winner_name: str = ""
    loser_names: List[str] = field(default_factory=list)
    rating: int = 0
    stars: float = 0.0
    commentary: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return f"{self.match_type} - Winner: {self.winner_name} ({self.stars:.1f} stars)"


@dataclass
class ShowResult:
    """Result data from running a complete show."""
    show_name: str
    match_results: List[MatchResult] = field(default_factory=list)
    final_rating: int = 0
    profit: int = 0
    tv_rating: float = 0.0
    attendance: int = 0
    ticket_revenue: int = 0
    ppv_revenue: int = 0
    viewer_change: int = 0
    prestige_change: int = 0

    @property
    def match_count(self) -> int:
        return len(self.match_results)

    @property
    def feedback(self) -> str:
        """Generate show feedback based on final rating."""
        if self.final_rating > 85:
            return "An instant classic! The internet is buzzing."
        elif self.final_rating > 70:
            return "A very strong show. The fans went home happy."
        elif self.final_rating > 50:
            return "An average night. Some good wrestling, some filler."
        elif self.final_rating > 20:
            return "The crowd was bored. Needs more star power."
        else:
            return "A disaster. Refunds are being demanded."