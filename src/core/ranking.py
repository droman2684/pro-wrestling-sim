from typing import List
from core.wrestler import Wrestler
from core.tag_team import TagTeam


def calculate_wrestler_rankings(wrestlers: List[Wrestler]) -> List[Wrestler]:
    """
    Calculates and returns a ranked list of wrestlers.
    Ranking criteria:
    1. Win Percentage (Wins / (Wins + Losses))
    2. Total Wins
    3. Overall Rating
    """
    ranked_wrestlers = sorted(
        [w for w in wrestlers if w.wins + w.losses > 0],
        key=lambda w: (w.wins / (w.wins + w.losses) if (w.wins + w.losses) > 0 else 0, w.wins, w.get_overall_rating()),
        reverse=True
    )
    return ranked_wrestlers


def calculate_tag_team_rankings(tag_teams: List[TagTeam], all_wrestlers: List[Wrestler]) -> List[TagTeam]:
    """
    Calculates and returns a ranked list of tag teams.
    Ranking criteria:
    1. Win Percentage (Wins / (Wins + Losses))
    2. Total Wins
    3. Team Rating
    """
    ranked_tag_teams = sorted(
        [tt for tt in tag_teams if tt.wins + tt.losses > 0 and tt.is_active],
        key=lambda tt: (tt.wins / (tt.wins + tt.losses) if (tt.wins + tt.losses) > 0 else 0, tt.wins, tt.get_team_rating(all_wrestlers)),
        reverse=True
    )
    return ranked_tag_teams
