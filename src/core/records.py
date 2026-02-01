"""
Records and standings tracking for match history, streaks, and title reigns.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class MatchHistoryEntry:
    """A single match result in the history."""
    id: int
    date: dict  # {"year": 1, "month": 3, "week": 2}
    show_name: str
    is_ppv: bool
    match_type: str  # "Singles", "Tag Team", "Triple Threat", etc.
    participant_ids: List[int]
    participant_names: List[str]
    winner_ids: List[int]
    winner_names: List[str]
    loser_ids: List[int]
    loser_names: List[str]
    rating: int
    stars: float
    is_title_match: bool = False
    title_id: Optional[int] = None
    title_name: str = ""
    title_changed: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "date": self.date,
            "show_name": self.show_name,
            "is_ppv": self.is_ppv,
            "match_type": self.match_type,
            "participant_ids": self.participant_ids,
            "participant_names": self.participant_names,
            "winner_ids": self.winner_ids,
            "winner_names": self.winner_names,
            "loser_ids": self.loser_ids,
            "loser_names": self.loser_names,
            "rating": self.rating,
            "stars": self.stars,
            "is_title_match": self.is_title_match,
            "title_id": self.title_id,
            "title_name": self.title_name,
            "title_changed": self.title_changed,
        }

    @staticmethod
    def from_dict(data: dict) -> "MatchHistoryEntry":
        """Create from dictionary."""
        return MatchHistoryEntry(
            id=data["id"],
            date=data["date"],
            show_name=data["show_name"],
            is_ppv=data["is_ppv"],
            match_type=data["match_type"],
            participant_ids=data["participant_ids"],
            participant_names=data["participant_names"],
            winner_ids=data["winner_ids"],
            winner_names=data["winner_names"],
            loser_ids=data["loser_ids"],
            loser_names=data["loser_names"],
            rating=data["rating"],
            stars=data["stars"],
            is_title_match=data.get("is_title_match", False),
            title_id=data.get("title_id"),
            title_name=data.get("title_name", ""),
            title_changed=data.get("title_changed", False),
        )


@dataclass
class WrestlerRecords:
    """Extended records for a wrestler including streaks and PPV/TV stats."""
    wrestler_id: int
    current_win_streak: int = 0
    current_loss_streak: int = 0
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    ppv_wins: int = 0
    ppv_losses: int = 0
    tv_wins: int = 0
    tv_losses: int = 0

    @property
    def current_streak(self) -> int:
        """
        Returns the current streak as a signed integer.
        Positive = Win Streak, Negative = Loss Streak.
        """
        if self.current_win_streak > 0:
            return self.current_win_streak
        elif self.current_loss_streak > 0:
            return -self.current_loss_streak
        return 0

    def record_win(self, is_ppv: bool) -> None:
        """Record a win for this wrestler."""
        # Update streaks
        self.current_win_streak += 1
        self.current_loss_streak = 0

        # Update longest win streak
        if self.current_win_streak > self.longest_win_streak:
            self.longest_win_streak = self.current_win_streak

        # Update PPV/TV stats
        if is_ppv:
            self.ppv_wins += 1
        else:
            self.tv_wins += 1

    def record_loss(self, is_ppv: bool) -> None:
        """Record a loss for this wrestler."""
        # Update streaks
        self.current_loss_streak += 1
        self.current_win_streak = 0

        # Update longest loss streak
        if self.current_loss_streak > self.longest_loss_streak:
            self.longest_loss_streak = self.current_loss_streak

        # Update PPV/TV stats
        if is_ppv:
            self.ppv_losses += 1
        else:
            self.tv_losses += 1

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "wrestler_id": self.wrestler_id,
            "current_win_streak": self.current_win_streak,
            "current_loss_streak": self.current_loss_streak,
            "longest_win_streak": self.longest_win_streak,
            "longest_loss_streak": self.longest_loss_streak,
            "ppv_wins": self.ppv_wins,
            "ppv_losses": self.ppv_losses,
            "tv_wins": self.tv_wins,
            "tv_losses": self.tv_losses,
        }

    @staticmethod
    def from_dict(data: dict) -> "WrestlerRecords":
        """Create from dictionary."""
        return WrestlerRecords(
            wrestler_id=data["wrestler_id"],
            current_win_streak=data.get("current_win_streak", 0),
            current_loss_streak=data.get("current_loss_streak", 0),
            longest_win_streak=data.get("longest_win_streak", 0),
            longest_loss_streak=data.get("longest_loss_streak", 0),
            ppv_wins=data.get("ppv_wins", 0),
            ppv_losses=data.get("ppv_losses", 0),
            tv_wins=data.get("tv_wins", 0),
            tv_losses=data.get("tv_losses", 0),
        )


@dataclass
class TitleReign:
    """A single title reign record."""
    id: int
    title_id: int
    title_name: str
    holder_id: int
    holder_name: str
    holder_type: str  # "wrestler" or "tag_team"
    won_date: dict  # {"year": 1, "month": 3, "week": 2}
    lost_date: Optional[dict] = None
    successful_defenses: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title_id": self.title_id,
            "title_name": self.title_name,
            "holder_id": self.holder_id,
            "holder_name": self.holder_name,
            "holder_type": self.holder_type,
            "won_date": self.won_date,
            "lost_date": self.lost_date,
            "successful_defenses": self.successful_defenses,
        }

    @staticmethod
    def from_dict(data: dict) -> "TitleReign":
        """Create from dictionary."""
        return TitleReign(
            id=data["id"],
            title_id=data["title_id"],
            title_name=data["title_name"],
            holder_id=data["holder_id"],
            holder_name=data["holder_name"],
            holder_type=data["holder_type"],
            won_date=data["won_date"],
            lost_date=data.get("lost_date"),
            successful_defenses=data.get("successful_defenses", 0),
        )


@dataclass
class RecordsManager:
    """Manages all match history, wrestler records, and title reigns."""
    match_history: List[MatchHistoryEntry] = field(default_factory=list)
    wrestler_records: Dict[int, WrestlerRecords] = field(default_factory=dict)
    title_reigns: List[TitleReign] = field(default_factory=list)
    _next_match_id: int = 1
    _next_reign_id: int = 1

    def add_match(self, entry: MatchHistoryEntry) -> None:
        """Add a match to history."""
        self.match_history.append(entry)

    def get_next_match_id(self) -> int:
        """Get the next available match ID and increment."""
        match_id = self._next_match_id
        self._next_match_id += 1
        return match_id

    def get_next_reign_id(self) -> int:
        """Get the next available reign ID and increment."""
        reign_id = self._next_reign_id
        self._next_reign_id += 1
        return reign_id

    def get_wrestler_records(self, wrestler_id: int) -> WrestlerRecords:
        """Get or create records for a wrestler."""
        if wrestler_id not in self.wrestler_records:
            self.wrestler_records[wrestler_id] = WrestlerRecords(wrestler_id=wrestler_id)
        return self.wrestler_records[wrestler_id]

    def record_wrestler_win(self, wrestler_id: int, is_ppv: bool) -> None:
        """Record a win for a wrestler."""
        records = self.get_wrestler_records(wrestler_id)
        records.record_win(is_ppv)

    def record_wrestler_loss(self, wrestler_id: int, is_ppv: bool) -> None:
        """Record a loss for a wrestler."""
        records = self.get_wrestler_records(wrestler_id)
        records.record_loss(is_ppv)

    def start_title_reign(
        self,
        title_id: int,
        title_name: str,
        holder_id: int,
        holder_name: str,
        holder_type: str,
        date: dict,
    ) -> TitleReign:
        """Start a new title reign."""
        reign = TitleReign(
            id=self.get_next_reign_id(),
            title_id=title_id,
            title_name=title_name,
            holder_id=holder_id,
            holder_name=holder_name,
            holder_type=holder_type,
            won_date=date,
        )
        self.title_reigns.append(reign)
        return reign

    def end_title_reign(self, title_id: int, holder_id: int, date: dict) -> Optional[TitleReign]:
        """End a title reign by setting the lost_date."""
        for reign in reversed(self.title_reigns):
            if reign.title_id == title_id and reign.holder_id == holder_id and reign.lost_date is None:
                reign.lost_date = date
                return reign
        return None

    def record_title_defense(self, title_id: int, holder_id: int) -> None:
        """Record a successful title defense."""
        for reign in reversed(self.title_reigns):
            if reign.title_id == title_id and reign.holder_id == holder_id and reign.lost_date is None:
                reign.successful_defenses += 1
                return

    def get_current_reign(self, title_id: int) -> Optional[TitleReign]:
        """Get the current (ongoing) reign for a title."""
        for reign in reversed(self.title_reigns):
            if reign.title_id == title_id and reign.lost_date is None:
                return reign
        return None

    def get_title_history(self, title_id: int) -> List[TitleReign]:
        """Get all reigns for a specific title."""
        return [r for r in self.title_reigns if r.title_id == title_id]

    def get_wrestler_match_history(self, wrestler_id: int, limit: int = 50) -> List[MatchHistoryEntry]:
        """Get match history for a specific wrestler."""
        matches = [
            m for m in self.match_history
            if wrestler_id in m.participant_ids
        ]
        return matches[-limit:] if limit else matches

    def get_recent_matches(self, limit: int = 50) -> List[MatchHistoryEntry]:
        """Get most recent matches."""
        return self.match_history[-limit:] if limit else self.match_history

    def get_head_to_head(self, wrestler_a_id: int, wrestler_b_id: int) -> dict:
        """Get head-to-head record between two wrestlers."""
        wins_a = 0
        wins_b = 0
        matches = []

        for match in self.match_history:
            if wrestler_a_id in match.participant_ids and wrestler_b_id in match.participant_ids:
                matches.append(match)
                if wrestler_a_id in match.winner_ids:
                    wins_a += 1
                elif wrestler_b_id in match.winner_ids:
                    wins_b += 1

        return {
            "wrestler_a_id": wrestler_a_id,
            "wrestler_b_id": wrestler_b_id,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "total_matches": len(matches),
            "matches": matches,
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "match_history": [m.to_dict() for m in self.match_history],
            "wrestler_records": {
                str(k): v.to_dict() for k, v in self.wrestler_records.items()
            },
            "title_reigns": [r.to_dict() for r in self.title_reigns],
            "_next_match_id": self._next_match_id,
            "_next_reign_id": self._next_reign_id,
        }

    @staticmethod
    def from_dict(data: dict) -> "RecordsManager":
        """Create from dictionary."""
        manager = RecordsManager()

        manager.match_history = [
            MatchHistoryEntry.from_dict(m) for m in data.get("match_history", [])
        ]

        manager.wrestler_records = {
            int(k): WrestlerRecords.from_dict(v)
            for k, v in data.get("wrestler_records", {}).items()
        }

        manager.title_reigns = [
            TitleReign.from_dict(r) for r in data.get("title_reigns", [])
        ]

        manager._next_match_id = data.get("_next_match_id", 1)
        manager._next_reign_id = data.get("_next_reign_id", 1)

        return manager
